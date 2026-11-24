"""Recording facts and V2 case preparation; never execute or approve a recording."""
from __future__ import annotations

import ast
import copy
import hashlib
import io
import json
import re
import tokenize
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlsplit
from typing import Any

from .case_contracts import canonical_hash, validate_document
from .b_case_snapshot import create_snapshot, render_snapshot_markdown
from .compiler_v2 import compile_case_v2
from .path_planner import plan_asset_path
from .product_aggregate import render_product_aggregate_v2
from .release_verifier import verify_release
from .strict_json import load_strict_json

_SENSITIVE = re.compile(r'password|passwd|pwd|token|secret|cookie|authorization|storage_state|session.?id|credential|api.?key|密码|口令|令牌', re.I)
_ACTIONS = {'goto','click','dblclick','fill','type','press','check','uncheck','select_option',
            'scroll_into_view_if_needed','wheel','is_visible','is_hidden','wait_for_selector','wait_for_url'}
_LOCATORS = {'locator','get_by_role','get_by_text','get_by_label','get_by_placeholder','get_by_test_id','nth','filter'}
_ASSERTIONS = {'to_be_visible','to_be_hidden','to_have_text','to_contain_text','to_have_value','to_be_checked','to_have_count'}
_UNKNOWN = '<unresolved>'
_MASK = '<credential-ref-required>'
_URL_CANDIDATE = re.compile(r"""(?:(?:[A-Za-z]|%[0-9A-Fa-f]{2})(?:[A-Za-z0-9+.-]|%[0-9A-Fa-f]{2})*(?::|%3[Aa]))?(?:/|%2[Ff]){2}[^\s"'<>\\]+""")


def _diagnostic_forms(value: str) -> list[str]:
    forms=[value]
    for _ in range(3):
        decoded=unquote(forms[-1])
        if decoded==forms[-1]: break
        forms.append(decoded)
    return forms


def _sensitive_key(value: str) -> bool:
    return any(_SENSITIVE.search(form) for form in _diagnostic_forms(value))


def _credential_content(value: str) -> bool:
    if re.fullmatch(r'credential:[A-Za-z0-9_.:/-]+',value):
        return False
    for form in _diagnostic_forms(value):
        if re.search(r'(?:password|passwd|pwd|token|secret|cookie|authorization|session.?id|api.?key|密码|口令|令牌)\s*[=:]|\bBearer\s+\S+',form,re.I):
            return True
        # 先保存原始候选的边界，再检查其组成部分；编码空格或引号不会截断 userinfo。
        for candidate in _URL_CANDIDATE.findall(form):
            for candidate_form in _diagnostic_forms(candidate):
                try:
                    parsed=urlsplit(candidate_form)
                    if parsed.username is not None or parsed.password is not None:
                        return True
                except ValueError:
                    return True
    return False


def _sanitize(value):
    """Return safe diagnostic content plus whether a credential gap is needed."""
    if isinstance(value,dict):
        result={}; found=False
        for key,child in value.items():
            if _sensitive_key(str(key)) or _credential_content(str(key)):
                result['<credential-field>']=_MASK; found=True
            else:
                safe,hit=_sanitize(child); result[key]=safe; found|=hit
        return result,found
    if isinstance(value,list):
        items=[_sanitize(child) for child in value]
        return [item[0] for item in items],any(item[1] for item in items)
    if isinstance(value,str) and _credential_content(value):
        return _MASK,True
    return value,False


def _literal(node: ast.AST, depth: int = 0) -> Any:
    if depth > 32:
        return _UNKNOWN
    if isinstance(node, ast.Constant) and isinstance(node.value,(str,int,float,bool,type(None))):
        return node.value
    if isinstance(node,(ast.Tuple,ast.List)):
        return [_literal(n,depth+1) for n in node.elts]
    if isinstance(node,ast.Dict) and all(isinstance(k,ast.Constant) and isinstance(k.value,str) for k in node.keys):
        return {k.value:_literal(v,depth+1) for k,v in zip(node.keys,node.values)}
    return _UNKNOWN


def _target(node: ast.AST, aliases: dict[str,str]) -> str:
    if isinstance(node,ast.Name):
        return aliases.get(node.id,node.id if re.fullmatch(r'page\d*',node.id) else _UNKNOWN)
    if isinstance(node,ast.Attribute) and node.attr in {'first','last','mouse'}:
        return _target(node.value,aliases)+'.'+node.attr
    if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr in _LOCATORS:
        parent=_target(node.func.value,aliases)
        args=[_literal(n) for n in node.args]
        kwargs={k.arg:_literal(k.value) for k in node.keywords if k.arg}
        return parent+'.'+node.func.attr+'('+json.dumps([args,kwargs],ensure_ascii=False)+')'
    return _UNKNOWN


def inspect_recording(recording_text: str, *, source_name: str = 'recording.py',
                      expected_steps: list[dict[str,Any]] | None = None) -> dict[str,Any]:
    """Static Python/Playwright subset. Unrecorded requirements need explicit facts.

    expected_steps are independently supplied recording observations: step_id,
    action, optional source_line, and optional gap_code/cause_ref. A missing action
    is not synthesized. All other unknowns remain review gaps.
    """
    if not isinstance(recording_text,str):
        raise ValueError('E_RECORDING_TYPE_INVALID')
    if not isinstance(source_name,str) or not re.fullmatch(r'[A-Za-z0-9._-]{1,128}',source_name) or _credential_content(source_name):
        raise ValueError('E_RECORDING_SOURCE_NAME_INVALID')
    observations=expected_steps or []
    if not isinstance(observations,list) or len(observations)>1000:
        raise ValueError('E_RECORDING_OBSERVATIONS_INVALID')
    seen=set()
    for item in observations:
        if not isinstance(item,dict) or not re.fullmatch(r'[A-Za-z0-9._-]{1,128}',str(item.get('step_id',''))) or item['step_id'] in seen:
            raise ValueError('E_RECORDING_OBSERVATIONS_INVALID')
        seen.add(item['step_id'])
        if item.get('action') not in _ACTIONS|_ASSERTIONS or item.get('gap_code') is not None and not re.fullmatch(r'[A-Z_]{1,64}',str(item['gap_code'])):
            raise ValueError('E_RECORDING_OBSERVATIONS_INVALID')
        for key in ('source_line','source_column'):
            if key in item and (type(item[key]) is not int or item[key] < (1 if key=='source_line' else 0)):
                raise ValueError('E_RECORDING_OBSERVATIONS_INVALID')
        if item.get('cause_ref') is not None and (not re.fullmatch(r'evidence:[A-Za-z0-9._:/-]{1,128}',str(item['cause_ref'])) or _credential_content(item['cause_ref'])):
            raise ValueError('E_RECORDING_OBSERVATIONS_INVALID')
    result={'schema_version':'ui-test.recording-review.v1','source_name':source_name,
            'source_hash':'sha256:'+hashlib.sha256(recording_text.encode('utf-8')).hexdigest(),
            'steps':[],'gaps':[],'approved':False,'status':'needs_clarification'}
    def gap(code, line=None, step_id=None, cause_ref=None):
        result['gaps'].append(dict(code=code,step_id=step_id or (f'line-{line}' if line else 'recording'),
            source_line=line,reason='evidenced' if cause_ref else 'unknown',cause_ref=cause_ref))
    if len(recording_text.encode('utf-8'))>262144:
        gap('RECORDING_SIZE_LIMIT'); return result
    try:
        # 构建 AST 前限制括号深度，忽略字符串及注释中的括号。
        depth=0
        for token in tokenize.generate_tokens(io.StringIO(recording_text).readline):
            if token.type==tokenize.OP:
                depth+=int(token.string in '([{')-int(token.string in ')]}')
                if depth>64:
                    gap('RECORDING_NESTING_LIMIT'); return result
        tree=ast.parse(recording_text)
    except (SyntaxError,ValueError,RecursionError,tokenize.TokenError,IndentationError):
        gap('INTERRUPTED_OR_INVALID_SYNTAX'); return result
    nodes=list(ast.walk(tree))
    if len(nodes)>20000:
        gap('RECORDING_NODE_LIMIT'); return result
    aliases={}
    uncertain=[n for n in nodes if isinstance(n,(ast.If,ast.For,ast.While,ast.Try,ast.Match,ast.AsyncFor,ast.IfExp))]
    for n in sorted(nodes,key=lambda n:(getattr(n,'lineno',0),getattr(n,'col_offset',0))):
        if isinstance(n,ast.Assign) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Attribute) and n.value.func.attr in _LOCATORS:
            for target in n.targets:
                if isinstance(target,ast.Name):
                    aliases[target.id]=_target(n.value,aliases)
        if not isinstance(n,ast.Call):
            continue
        method=n.func.attr if isinstance(n.func,ast.Attribute) else None
        if method in _LOCATORS or isinstance(n.func,ast.Name) and n.func.id in {'expect','sync_playwright','async_playwright'}:
            continue
        if method not in _ACTIONS|_ASSERTIONS:
            # 允许录制器启动及收尾形式，但不输出其中的数据。
            if method not in {'launch','new_context','new_page','close','run'}:
                gap('UNSUPPORTED_CALL',n.lineno)
            continue
        receiver=n.func.value
        assertion=method in _ASSERTIONS
        if assertion:
            if not isinstance(receiver,ast.Call) or not isinstance(receiver.func,ast.Name) or receiver.func.id!='expect' or not receiver.args:
                gap('UNSUPPORTED_ASSERTION',n.lineno); continue
            receiver=receiver.args[0]
        target=_target(receiver,aliases)
        if not target.startswith('page') or _UNKNOWN in target:
            gap('UNRESOLVED_TARGET',n.lineno); continue
        direct=isinstance(receiver,ast.Name) and receiver.id not in aliases
        raw_args=[_literal(a) for a in n.args]
        kwargs={k.arg:_literal(k.value) for k in n.keywords if k.arg}
        if direct and method in {'click','dblclick','fill','type','press','check','uncheck','select_option','is_visible','is_hidden','wait_for_selector'}:
            selector=raw_args.pop(0) if raw_args else kwargs.pop('selector',_UNKNOWN)
            if not isinstance(selector,str) or selector==_UNKNOWN:
                gap('UNRESOLVED_TARGET',n.lineno); continue
            target+='.'+json.dumps(selector,ensure_ascii=False)
        sensitive=_sensitive_key(target)
        # 对所有位置参数、关键字参数及嵌套内容统一遮蔽，再构建输出。
        args,args_hit=_sanitize(raw_args); kwargs,kwargs_hit=_sanitize(kwargs)
        target,target_hit=_sanitize(target)
        sensitive|=args_hit or kwargs_hit or target_hit
        if sensitive:
            args=[_MASK for _ in raw_args]; kwargs={k:_MASK for k in kwargs}
        sid=f'REC-{len(result["steps"])+1:03d}'
        step=dict(step_id=sid,action=method,target=target,arguments=args,keyword_arguments=kwargs,
                  source_line=n.lineno,source_column=n.col_offset,source_name=source_name,
                  expected_result=dict(assertion=method,arguments=args) if assertion else None,
                  approved=False,execution_verified=False)
        if sensitive:
            step['target']='<credential-target>'
        result['steps'].append(step)
        if sensitive:
            gap('CREDENTIAL_REF_REQUIRED',n.lineno,sid)
        if _UNKNOWN in json.dumps([target,args,kwargs]):
            gap('UNRESOLVED_EXPRESSION',n.lineno,sid)
        if re.search(r'rc_select_|\.nth\(|\.first|\.last|\[id[\^$*]=',target):
            gap('DYNAMIC_TARGET',n.lineno,sid)
        if any(c.lineno<=n.lineno<=getattr(c,'end_lineno',c.lineno) for c in uncertain):
            gap('CONTROL_FLOW_UNKNOWN',n.lineno,sid)
        if method in {'is_visible','is_hidden'}:
            gap('VISIBILITY_RESULT_UNKNOWN',n.lineno,sid)
        if any(k.arg is None for k in n.keywords):
            gap('UNRESOLVED_EXPRESSION',n.lineno,sid)
    consumed=set()
    for expected in observations:
        sid=expected['step_id']; line=expected.get('source_line')
        matched=[s for s in result['steps'] if s['step_id'] not in consumed and s['action']==expected['action']
            and (line is None or s['source_line']==line)
            and ('source_column' not in expected or s['source_column']==expected['source_column'])]
        if expected.get('gap_code') or len(matched)!=1:
            gap(expected.get('gap_code') or ('AMBIGUOUS_ACTION' if matched else 'MISSING_ACTION'),line,sid,expected.get('cause_ref'))
        else:
            consumed.add(matched[0]['step_id'])
    # 断言只归属同目标的最近前序动作，不能替其它动作消除未知期望。
    asserted=set(); latest={}
    for s in result['steps']:
        if s['expected_result'] is None:
            latest[s['target']]=s['step_id']
        elif s['target'] in latest:
            asserted.add(latest[s['target']])
    for s in result['steps']:
        if s['expected_result'] is None and s['step_id'] not in asserted:
            gap('EXPECTED_RESULT_UNKNOWN',s['source_line'],s['step_id'])
    if not result['steps']:
        gap('NO_RECORDED_STEPS')
    result['status']='reviewable' if not result['gaps'] else 'needs_clarification'
    return result


def _data_document(data):
    document={k:copy.deepcopy(v) for k,v in data.items() if k not in {'test_data_hash','source_path'}}
    if validate_document(document,'test-data.schema.json'):
        raise ValueError('E_PREPARATION_DATA_INVALID')
    return document


def _check_sensitive_material(value):
    """Reject obvious credential material before copying it to any draft/export.

    This is a narrow input contract, not a claim of general DLP completeness.
    Credential references are the only supported form for credential parameters.
    """
    if isinstance(value,dict):
        for key,child in value.items():
            if _credential_content(str(key)) or (_sensitive_key(str(key)) and not
                (isinstance(child,str) and re.fullmatch(r'credential:[A-Za-z0-9_.:/-]+',child))):
                raise ValueError('E_PREPARATION_CREDENTIAL_REFERENCE_REQUIRED')
            _check_sensitive_material(child)
    elif isinstance(value,list):
        for child in value:
            _check_sensitive_material(child)
    elif isinstance(value,str) and _credential_content(value):
        raise ValueError('E_PREPARATION_CREDENTIAL_REFERENCE_REQUIRED')


def prepare_branch(*, source_case: dict[str,Any], test_data: dict[str,Any],
                   recording: str = '', origins: dict[str,dict[str,Any]],
                   expected_recording_steps: list[dict[str,Any]] | None = None,
                   runtime_values: dict[str,Any] | None = None) -> dict[str,Any]:
    """Turn explicit V2 case facts and recording evidence into an unapproved draft.

    No expectation, binding or action is inferred to satisfy the V2 schema.
    A recording origin needs an exact source line and matching action; manual
    facts need their own human source reference. Missing facts stay in Grill.
    """
    if validate_document(source_case,'source-case-v2.schema.json'):
        raise ValueError('E_PREPARATION_SOURCE_INVALID')
    data=_data_document(test_data)
    _check_sensitive_material(source_case)
    # 完整扫描已验证文档，包含可选 notes/defaults、受管引用及所有字典键。
    _check_sensitive_material(data)
    # 只保留已绑定且明确标为普通数据的运行值，避免复制原索引中的无关私密字段。
    used_values={b['ref'].split(':',1)[1] for b in source_case['parameter_bindings'] if b['ref'].startswith('value:')}
    bound_values=None
    if runtime_values is not None:
        bound_values={k:copy.deepcopy(runtime_values[k]) for k in used_values if k in runtime_values}
        for value in bound_values.values():
            if not isinstance(value,dict) or value.get('classification')!='ordinary' or value.get('sensitive') is not False:
                raise ValueError('E_PREPARATION_CREDENTIAL_REFERENCE_REQUIRED')
            _check_sensitive_material(value)
    snapshot=create_snapshot(source_case,data,runtime_values=bound_values)
    # 快照解析器拒绝凭据字面量及敏感的普通数据绑定。
    if any(g['code'] in {'E_CREDENTIAL_REFERENCE_REQUIRED','E_SNAPSHOT_CREDENTIAL_REFERENCE_REQUIRED'} for g in snapshot['gaps']):
        raise ValueError('E_PREPARATION_CREDENTIAL_REFERENCE_REQUIRED')
    review=inspect_recording(recording,expected_steps=expected_recording_steps) if recording else None
    gaps=copy.deepcopy(snapshot['gaps'])
    source_origins={}
    consumed=set()
    _check_sensitive_material(origins)
    step_ids=[s['step_id'] for s in source_case['steps']]
    if len(step_ids)!=len(set(step_ids)):
        raise ValueError('E_PREPARATION_STEP_ID_DUPLICATE')
    if set(origins)-set(step_ids):
        raise ValueError('E_PREPARATION_ORIGIN_STEP_UNKNOWN')
    for step in source_case['steps']:
        sid=step['step_id']; origin=origins.get(sid,{})
        kind=origin.get('kind')
        if kind=='human' and isinstance(origin.get('reference'),str) and re.fullmatch(r'human:[A-Za-z0-9._:/-]+',origin['reference']):
            source_origins[sid]={'kind':'human','reference':origin['reference']}
        elif kind=='recording' and review:
            line=origin.get('source_line')
            matched=[s for s in review['steps'] if s['step_id'] not in consumed and s['source_line']==line
                and ('source_column' not in origin or origin['source_column']==s['source_column'])
                and s['target']==origin.get('target')
                and (s['action']==step['action'] or step['action']=='assert' and s['action'] in _ASSERTIONS)]
            if len(matched)!=1:
                gaps.append(dict(code='RECORDING_ORIGIN_MISMATCH',step_id=sid)); continue
            recorded=matched[0]; pid=origin.get('parameter_id')
            if recorded['action'] in {'fill','type','goto','wait_for_url','press','select_option','to_have_text','to_contain_text','to_have_value','to_have_count'}:
                parameter=next((p for p in snapshot['parameters'] if p['parameter_id']==pid),None)
                key={'goto':'url','wait_for_url':'url','press':'key','select_option':'values'}.get(recorded['action'],'value')
                value=recorded['arguments'][0] if len(recorded['arguments'])==1 else recorded['keyword_arguments'].get(key,_UNKNOWN)
                if pid not in step['parameter_ids'] or not parameter or parameter.get('reference_only') or canonical_hash(value)!=canonical_hash(parameter.get('value')):
                    gaps.append(dict(code='RECORDING_ORIGIN_MISMATCH',step_id=sid)); continue
            consumed.add(recorded['step_id'])
            source_origins[sid]=dict(kind='recording',source_line=line,source_column=recorded['source_column'],
                target=recorded['target'],parameter_id=pid,recorded_step_id=recorded['step_id'],source_hash=review['source_hash'])
            # 功能期望有独立人工来源，可补录制器缺少的期望，但不能补造动作或值。
            ref=origin.get('expectation_reference')
            if not isinstance(ref,str) or not re.fullmatch(r'human:[A-Za-z0-9._:/-]+',ref):
                gaps.append(dict(code='EXPECTATION_SOURCE_REQUIRED',step_id=sid))
            else:
                source_origins[sid]['expectation_reference']=ref
            gaps.extend(dict(g,step_id=sid) for g in review['gaps'] if g['step_id']==recorded['step_id']
                and not (g['code']=='EXPECTED_RESULT_UNKNOWN' and source_origins[sid].get('expectation_reference')))
        else:
            gaps.append(dict(code='STEP_SOURCE_REQUIRED',step_id=sid))
    if review and expected_recording_steps:
        gaps.extend(copy.deepcopy(g) for g in review['gaps'] if any(e['step_id']==g['step_id'] for e in expected_recording_steps))
    result=dict(schema_version='ui-test.prepared-branch.v1',case_id=source_case['case_id'],
        branch_id=source_case['branch_id'],source_case=copy.deepcopy(source_case),test_data=data,
        snapshot=snapshot,human_view=render_snapshot_markdown(snapshot),recording_review=review,
        source_origins=source_origins,gaps=gaps,approved=False,confirmation_required=True,
        status='needs_clarification' if gaps else 'reviewable',runtime_values=bound_values)
    result['preparation_hash']=canonical_hash(result)
    return result


def _check_prepared(prepared):
    if prepared.get('preparation_hash')!=canonical_hash({k:v for k,v in prepared.items() if k!='preparation_hash'}):
        raise ValueError('E_PREPARATION_CHANGED')
    if prepared.get('status')!='reviewable' or prepared.get('gaps') or prepared.get('approved') is not False:
        raise ValueError('E_PREPARATION_NEEDS_CLARIFICATION')


def compile_prepared_branch(prepared: dict[str,Any], *, config: dict[str,Any], selection: dict[str,Any],
                            dependency_assets: dict[str,Any],page_module_registry: dict[str,Any],
                            formal_human_view: bool = False) -> dict[str,Any]:
    """Use the sole compiler and planner. Compilation never grants execution."""
    _check_prepared(prepared)
    source=prepared['source_case']; data=copy.deepcopy(prepared['test_data'])
    if selection.get('case_id')!=source['case_id'] or selection.get('branch_id')!=source['branch_id']:
        raise ValueError('E_PREPARATION_PATH_SCOPE_MISMATCH')
    for key in ('system','module_path','function'):
        if selection.get(key)!=source['scope'].get(key):
            raise ValueError('E_PREPARATION_PATH_SCOPE_MISMATCH')
    for key in ('project_group','product'):
        if config['scope'].get(key)!=source['scope'].get(key):
            raise ValueError('E_PREPARATION_PATH_SCOPE_MISMATCH')
    data['test_data_hash']=canonical_hash(data)
    credentials={r.split(':',1)[1] for r in data['runtime_refs'] if r.startswith('credential:')}
    sequences={r.split(':',1)[1] for r in data['runtime_refs'] if r.startswith('sequence:')}
    from .human_view_handoff import TCA_RENDERER_VERSION
    renderer = {'renderer_version': TCA_RENDERER_VERSION} if formal_human_view else {}  # 已选正式流程加载编写端交接。
    compiled=compile_case_v2(source_case=source,test_data=data,dependency_assets=dependency_assets,
        config_fingerprint=canonical_hash(config),runtime_values=prepared['runtime_values'],
        credential_keys=credentials,sequence_keys=sequences,page_module_registry=page_module_registry,**renderer)
    plans={role:plan_asset_path(config,role,selection) for role in ('source_case','human_view','playwright_test','case_manifest')}
    compiled['path_plans']=plans
    compiled['preparation_record']=copy.deepcopy(prepared)
    compiled['provenance']=dict(schema_version='ui-test.case-provenance.v1',
        case_id=source['case_id'],branch_id=source['branch_id'],case_version=source['case_version'],
        source_hash=compiled['manifest']['source_hash'],test_data_hash=data['test_data_hash'],
        build_fingerprint=compiled['manifest']['build_fingerprint'],preparation_hash=prepared['preparation_hash'],
        recording_hash=prepared['recording_review']['source_hash'] if prepared['recording_review'] else None,
        source_origins=copy.deepcopy(prepared['source_origins']),path_plans=copy.deepcopy(plans),
        artifacts=sorted([*compiled['outputs'],'product-aggregate.xmind','provenance.json']),approved=False)
    compiled['provenance_hash']=canonical_hash(compiled['provenance'])
    return compiled


def export_xmind(compiled: dict[str,Any], *, release_path: str | Path | None = None,
                 display_registry: dict[str,dict[str,str]] | None = None) -> bytes:
    """Serialize the sole product aggregate from an actually verified release."""
    _check_compiled(compiled)
    provenance=compiled['provenance']
    if release_path is None or display_registry is None:
        raise ValueError('E_XMIND_VERIFIED_RELEASE_REQUIRED')
    state=verify_release(release_path,current_identity=compiled['identity'])
    if any(state.get(k)!=v for k,v in {'release_integrity':'valid','input_sync':'in_sync','execution_gate':'ready'}.items()):
        raise ValueError('E_XMIND_VERIFIED_RELEASE_REQUIRED')
    release=Path(release_path)
    try:
        manifest=load_strict_json(release/'manifest.json')
        values={name:((release/name).read_text(encoding='utf-8') if name.endswith(('.py','.md')) else load_strict_json(release/name))
            for name in compiled['outputs']}
    except (OSError,UnicodeError,ValueError):
        raise ValueError('E_XMIND_VERIFIED_RELEASE_REQUIRED') from None
    if manifest!=compiled['manifest'] or any(canonical_hash(value)!=manifest['artifacts'][name] for name,value in values.items()):
        raise ValueError('E_XMIND_VERIFIED_RELEASE_REQUIRED')
    aggregate=render_product_aggregate_v2([dict(case_ir=values['case-ir.json'],resolved_ir=values['resolved-ir.json'],
        manifest=manifest,release_state=state)],display_registry=display_registry,
        config_fingerprint=compiled['identity']['config_fingerprint'])
    ns='urn:xmind:xmap:xmlns:content:2.0'
    def el(parent,tag,**attrs):
        return ET.SubElement(parent,'{'+ns+'}'+tag,attrs)
    root=ET.Element('{'+ns+'}xmap-content',{'version':'2.0'})
    sheet=el(root,'sheet',id='sheet-product'); el(sheet,'title').text=aggregate['manifest']['product_display_name']
    def project(parent,node):
        # XML 只镜像已有汇总树的节点及顺序，不再解释用例或生成第二份语义投影。
        topic=el(parent,'topic',id=hashlib.sha256(node['node_id'].encode()).hexdigest())
        el(topic,'title').text=node['label']
        notes=el(topic,'notes')
        el(notes,'plain').text=json.dumps({k:v for k,v in node.items() if k!='children'},ensure_ascii=False,sort_keys=True)
        if node['children']:
            children=el(el(topic,'children'),'topics',type='attached')
            for child in node['children']:
                project(children,child)
    project(sheet,aggregate['outline'])
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w',compression=zipfile.ZIP_DEFLATED) as workbook:
        for name,content in [('content.xml',ET.tostring(root,encoding='utf-8',xml_declaration=True)),
                             ('aggregate.outline.json',json.dumps(aggregate['outline'],ensure_ascii=False,sort_keys=True).encode('utf-8')),
                             ('aggregate-manifest.json',json.dumps(aggregate['manifest'],ensure_ascii=False,sort_keys=True).encode('utf-8')),
                             ('provenance.json',json.dumps(provenance,ensure_ascii=False,sort_keys=True).encode('utf-8'))]:
            info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED
            workbook.writestr(info,content)
    return stream.getvalue()


def _check_compiled(compiled):
    outputs=compiled['outputs']; manifest=compiled['manifest']; provenance=compiled['provenance']
    refs=provenance.get('failure_refs',[])
    if not isinstance(refs,list) or len(refs)>10000 or any(not isinstance(r,str)
        or not re.fullmatch(r'(?:run|evidence|failure):[A-Za-z0-9._:/-]{1,1024}',r)
        or _credential_content(r) for r in refs):
        raise ValueError('E_FAILURE_REFERENCE_INVALID')
    if compiled.get('provenance_hash')!=canonical_hash({k:v for k,v in provenance.items() if k!='failure_refs'}):
        raise ValueError('E_DERIVATIVE_ATTACHMENT_CHANGED')
    prepared=compiled.get('preparation_record',{})
    try:
        _check_prepared(prepared)
    except ValueError:
        raise ValueError('E_DERIVATIVE_ATTACHMENT_CHANGED') from None
    if provenance['preparation_hash']!=prepared['preparation_hash'] or provenance['source_origins']!=prepared['source_origins']:
        raise ValueError('E_DERIVATIVE_ATTACHMENT_CHANGED')
    if prepared['source_case']!=outputs['source-case.json'] or canonical_hash(prepared['test_data'])!=manifest['test_data_hash']:
        raise ValueError('E_DERIVATIVE_ATTACHMENT_CHANGED')
    if compiled['case_ir']!=outputs['case-ir.json'] or compiled.get('path_plans')!=provenance['path_plans']:
        raise ValueError('E_DERIVATIVE_ATTACHMENT_CHANGED')
    if set(outputs)!=set(manifest['artifacts']) or any(canonical_hash(value)!=manifest['artifacts'][name] for name,value in outputs.items()):
        raise ValueError('E_DERIVATIVE_ATTACHMENT_CHANGED')
    if compiled['resolved_ir']!=outputs['resolved-ir.json'] or compiled['parameter_manifest']!=outputs['case-parameter-manifest.json']:
        raise ValueError('E_DERIVATIVE_ATTACHMENT_CHANGED')
    if canonical_hash(compiled['identity'])!=manifest['build_fingerprint']:
        raise ValueError('E_DERIVATIVE_ATTACHMENT_CHANGED')
    for key in ('source_hash','test_data_hash','build_fingerprint','case_id','branch_id'):
        if provenance.get(key)!=manifest.get(key):
            raise ValueError('E_DERIVATIVE_ATTACHMENT_CHANGED')
    if provenance.get('case_version')!=outputs['source-case.json']['case_version'] or set(provenance['source_origins'])!={s['step_id'] for s in outputs['source-case.json']['steps']}:
        raise ValueError('E_DERIVATIVE_ATTACHMENT_CHANGED')


def fork_branch(parent: dict[str,Any], *, branch_id: str, origin_reference: str,
                parameters: dict[str,Any] | None = None,
                generation_rules: dict[str,Any] | None = None,
                step_updates: dict[str,dict[str,Any]] | None = None) -> dict[str,Any]:
    """Independent editable candidate: own branch, data revision and human source.

    Existing semantic expectations are copied as draft facts, never approved.
    Changing their meaning requires an explicit edited Source Case and re-prepare.
    """
    _check_prepared(parent)
    if not isinstance(branch_id,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{2,127}',branch_id) or branch_id==parent['branch_id']:
        raise ValueError('E_FORK_DISTINCT_BRANCH_REQUIRED')
    if not isinstance(origin_reference,str) or not re.fullmatch(r'human:[A-Za-z0-9._:/-]+',origin_reference):
        raise ValueError('E_FORK_SOURCE_REQUIRED')
    if any(origin_reference in {o.get('reference'),o.get('expectation_reference')} for o in parent['source_origins'].values()):
        raise ValueError('E_FORK_INDEPENDENT_SOURCE_REQUIRED')
    source=copy.deepcopy(parent['source_case']); data=copy.deepcopy(parent['test_data'])
    source.update(branch_id=branch_id,case_version=source['case_version']+1)
    data.update(branch_id=branch_id,data_revision=data['data_revision']+1)
    if parameters is not None:
        data['parameters']=copy.deepcopy(parameters)
    if generation_rules is not None:
        data['generation_rules']=copy.deepcopy(generation_rules)
    updates=step_updates or {}
    if not isinstance(updates,dict) or set(updates)-{s['step_id'] for s in source['steps']}:
        raise ValueError('E_FORK_EXPECTATION_UPDATE_INVALID')
    for step in source['steps']:
        update=updates.get(step['step_id'])
        if update is not None:
            if not isinstance(update,dict) or set(update)!={'expected_result','postconditions'}:
                raise ValueError('E_FORK_EXPECTATION_UPDATE_INVALID')
            step.update(copy.deepcopy(update))
    origins={step['step_id']:dict(kind='human',reference=origin_reference) for step in source['steps']}
    candidate=prepare_branch(source_case=source,test_data=data,origins=origins,runtime_values=parent['runtime_values'])
    # 使用既有解析器的逐步参数及后置条件，覆盖直接 test-data 引用且避免重复参数误判。
    old_steps={s['source_step_id']:s for s in parent['snapshot']['resolved_steps']}
    new_steps={s['source_step_id']:s for s in candidate['snapshot']['resolved_steps']}
    for step in source['steps']:
        sid=step['step_id']; old=old_steps[sid]; new=new_steps[sid]
        changed=any(old[key]!=new[key] for key in ('parameters','postconditions'))
        if changed and sid not in updates:
            candidate['gaps'].append(dict(code='BRANCH_EXPECTATION_REVIEW_REQUIRED',step_id=step['step_id']))
    if candidate['gaps']:
        candidate['status']='needs_clarification'
    candidate['lineage']=dict(parent_case_hash=parent['snapshot']['dependency_hashes']['source_case'],
                             parent_data_hash=parent['snapshot']['dependency_hashes']['test_data'],
                             parent_preparation_hash=parent['preparation_hash'])
    candidate['preparation_hash']=canonical_hash({k:v for k,v in candidate.items() if k!='preparation_hash'})
    return candidate


def diagnose_source_change(current: dict[str,Any], prior: dict[str,Any]) -> dict[str,Any]:
    """Read-only invalidation report; original artifacts and failures are untouched."""
    _check_compiled(current)
    _check_compiled(prior)
    changed=[key for key in ('case_id','branch_id','case_version','source_hash','test_data_hash',
        'build_fingerprint','preparation_hash','recording_hash','source_origins','path_plans')
        if current['provenance'].get(key)!=prior['provenance'].get(key)]
    refs=copy.deepcopy(prior['provenance'].get('failure_refs',[]))
    return dict(changed=bool(changed),changed_dependencies=changed,
        stale_artifacts=copy.deepcopy(prior['provenance']['artifacts']) if changed else [],
        prior_build_fingerprint=prior['manifest']['build_fingerprint'],
        current_build_fingerprint=current['manifest']['build_fingerprint'],
        preserved_failure_refs=refs,confirmation_required=bool(changed),history_modified=False)
