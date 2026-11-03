"""Read-only recording interpretation to candidate batch and two derived views.

The agent supplies business interpretation; this module never evaluates source code.
"""
import copy
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


def _digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def _cell(text):
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('|', '&#124;').replace('\r', '').replace('\n', '<br>')


def _credential_guard(value):
    """Fail closed on recognizable inline credentials, without echoing values.

    This is a second guard after the skill's mandatory input privacy review,
    not a classifier for every possible secret or personal identifier.
    """
    if isinstance(value, dict):
        for key, child in value.items():
            if key == 'credential_ref':
                if not isinstance(child, str) or not re.fullmatch(r'credential://[A-Za-z0-9_./-]+', child):
                    raise ValueError('Invalid credential reference')
            elif re.search(r'password|passwd|secret|token|authorization|cookie|api[_-]?key', key, re.I):
                raise ValueError('Inline credential field; use credential_ref')
            else:
                _credential_guard(child)
    elif isinstance(value, list):
        for child in value:
            _credential_guard(child)
    elif isinstance(value, str):
        patterns = [r'Bearer\s+[^\s\x22\x27]+', r'-----BEGIN .*PRIVATE KEY',
                    r'(?:password|passwd|secret|token|authorization|cookie|api[_-]?key)[\x22\x27]?\s*[:=]\s*[\x22\x27][^\x22\x27]+',
                    r'(?:password|passwd|密码)[^;]{0,300}?\.(?:fill|type)\(\s*[\x22\x27](?!credential://)[^\x22\x27]+',
                    r'https?://[^\s/]+:[^\s/]+@',
                    r'[?&](?:token|password|secret|api_key)=[^&\s\x22\x27]+']
        if any(re.search(pattern, value, re.I) for pattern in patterns):
            raise ValueError('Inline credential detected; supply a sanitized reference-only input')


def _validate(draft, sources):
    for key in ('batch_id', 'case_id', 'title'):
        if not isinstance(draft.get(key), str) or not draft[key].strip():
            raise ValueError('Missing identity or title')
    if len(draft.get('module_path', [])) != 5 or not all(isinstance(x, str) and x.strip() for x in draft['module_path']):
        raise ValueError('Expected team/product/system/module/function path')
    if not draft.get('steps'):
        raise ValueError('Recording needs at least one business step')
    def check_source(item):
        source, span = item.get('source'), item.get('lines')
        if source == 'inference':
            return
        if source not in sources or not isinstance(span, list) or len(span) != 2 or any(type(x) is not int for x in span):
            raise ValueError('Invalid source range')
        if not 1 <= span[0] <= span[1] <= len(sources[source].splitlines()):
            raise ValueError('Invalid source range')
    def walk(value):
        if isinstance(value, dict):
            if 'source' in value:
                check_source(value)
                value['basis'] = {'recording': 'recording_observation', 'prd': 'material_statement', 'inference': 'ai_inference'}[value['source']]
            for child in list(value.values()):
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)
    walk(draft)
    covered = set()
    for item in draft.get('recording_coverage', []):
        check_source(dict(item, source='recording'))
        if not item.get('reason'):
            raise ValueError('Coverage requires a reason')
        covered.update(range(item['lines'][0], item['lines'][1] + 1))
    if any(i not in covered for i, line in enumerate(sources['recording'].splitlines(), 1) if line.strip()):
        raise ValueError('Recording has unaccounted lines')
    ids = [d['id'] for d in draft['data']]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate data identity')
    for item in draft['data']:
        check_source(item)
        if ('value' in item) == ('credential_ref' in item):
            raise ValueError('Data requires exactly one value or credential_ref')
    for claims in draft['context'].values():
        for claim in claims:
            check_source(claim)
    for group in ('steps', 'common_preconditions'):
        for step in draft.get(group, []):
            check_source(step)
            if not step.get('operation'):
                raise ValueError('Missing business operation')
            if any(ref not in ids for ref in step['data_refs']):
                raise ValueError('Unknown data reference')
            for field in ('expected', 'verification'):
                for claim in step[field]:
                    check_source(claim)


def _views(batch):
    case = batch['cases'][0]
    data = {item['id']: item for item in batch['data']}
    version = batch['content_version']
    human = [f"# {case['id']} {case['title']}", f"版本：{version}",
             '模块：' + ' / '.join(case['module_path']), '候选；待评审；未合并；未执行']
    tree = [f'# 候选批次 {batch["id"]}', f'- 版本：{version}']
    indent = ''
    for part in case['module_path']:
        tree.append(indent + '- ' + _cell(part))
        indent += '  '
    case_heading = indent + f'- {case["id"]} { _cell(case["title"])} [P0；候选；待评审；未执行]'
    context_nodes = []
    for field, label in [('role', '角色'), ('initial_state', '初始状态')]:
        text = '；'.join(c['text'] for c in case['context'].get(field, [])) or '待澄清'
        human.append(label + '：' + _cell(text))
        context_nodes.append(indent + '  - ' + label + '：' + _cell(text))
    for group, label in [('common_preconditions', '公共前置操作'), ('steps', '测试步骤')]:
        if group == 'steps':
            tree.append(case_heading)
            tree.extend(context_nodes)
            indent += '  '
        tree.append(indent + '- ' + label)
        human.append(label + '：')
        if not case[group]:
            tree.append(indent + '  - 输入未提供，待核对')
            human.append('输入未提供，待核对')
            continue
        human.extend(['| 序号 | 操作 | 参数/数据 | 预期结果 |', '| --- | --- | --- | --- |'])
        for i, step in enumerate(case[group], 1):
            values = []
            for ref in step['data_refs']:
                item = data[ref]
                value = f"{ref}：{item.get('credential_ref', item.get('value', '待澄清'))}"
                for key, label in [('object_ref', '业务对象'), ('validity', '有效性'), ('reuse_policy', '复用策略'), ('invalidation_action', '失效处理')]:
                    if key in item:
                        value += f"；{label}：{item[key]}"
                values.append(value)
            expected = [c['text'] for c in step['expected']] or ['待澄清']
            verification = [c['text'] for c in step['verification']] or ['待澄清']
            outcome = '预期：' + '；'.join(expected) + '；验证点：' + '；'.join(verification)
            human.append(f"| {i} | {_cell(step['operation'])} | {_cell('；'.join(values) or '无')} | {_cell(outcome)} |")
            tree.extend([indent + f"  - {i}. {_cell(step['operation'])}", indent + '    - 参数/数据'])
            tree.extend(indent + '      - ' + _cell(v) for v in (values or ['无']))
            tree.append(indent + '    - 预期')
            tree.extend(indent + '      - ' + _cell(v) for v in expected)
            tree.append(indent + '      - 验证点：' + _cell('；'.join(verification)))
    if batch['questions']:
        human.append('待澄清：')
        tree.append('- 待澄清')
        for q in batch['questions']:
            human.append('- ' + _cell(q['field']) + '：' + q['reason'])
            tree.append('  - ' + _cell(q['field']) + '：' + q['reason'])
    return '\n'.join(human) + '\n', '\n'.join(tree) + '\n'


def build_batch(recording, interpretation, prd=None):
    """Convert an agent interpretation; return batch, human_view, xmind_markdown.

    Inputs are in-memory UTF-8 text and a JSON-compatible interpretation. No writes,
    subprocesses, browser, network calls or execution of recording code occur here.
    """
    draft = copy.deepcopy(interpretation)
    _credential_guard([recording, draft, prd])
    sources = {'recording': recording}
    if prd is not None:
        sources['prd'] = prd
    _validate(draft, sources)
    case = {'id': draft['case_id'], 'title': draft['title'], 'priority': 'P0',
            'module_path': draft['module_path'], 'priority_basis': '核心录制路径候选，待用户评审',
            'maintenance_action': 'add', 'review_status': 'pending', 'rule_status': 'unconfirmed',
            'merge_status': 'not_merged', 'execution_status': 'not_run',
            'context': draft['context'], 'steps': draft['steps'],
            'common_preconditions': draft.get('common_preconditions', [])}
    questions = []
    for field in ('role', 'initial_state'):
        if not case['context'].get(field):
            questions.append({'field': field, 'reason': '缺少依据，待澄清', 'case_id': case['id']})
    for i, step in enumerate(case['steps']):
        if not step['expected'] or not step['verification']:
            questions.append({'field': f'steps/{i}', 'reason': '预期或验证点缺失，待澄清', 'case_id': case['id']})
    def inspect(claims, field):
        if len({c['text'] for c in claims}) > 1:
            questions.append({'field': field, 'reason': '资料或观察不一致，待用户裁决', 'case_id': case['id'], 'evidence': claims})
        if any(c['source'] == 'inference' for c in claims):
            questions.append({'field': field, 'reason': 'AI 推断，待用户确认', 'case_id': case['id'], 'evidence': claims})
    for field, claims in case['context'].items():
        inspect(claims, field)
    for group in ('steps', 'common_preconditions'):
        for i, step in enumerate(case[group]):
            step.setdefault('id', f'{case["id"]}/{group}/{i + 1}')
            for field in ('expected', 'verification'):
                inspect(step[field], f'{group}/{i}/{field}')
    for item in draft['data']:
        missing = [key for key in ('object_ref', 'validity', 'reuse_policy', 'invalidation_action') if key not in item]
        if missing:
            questions.append({'field': 'data/' + item['id'], 'reason': '业务数据条件缺失，待澄清', 'missing': missing, 'case_id': case['id']})
        if item['source'] == 'inference':
            questions.append({'field': 'data/' + item['id'], 'reason': 'AI 数据建议，待用户确认', 'case_id': case['id']})
    batch = {'schema_version': 1, 'id': draft['batch_id'], 'stage': 'P0',
             'sources': [{'id': key, 'kind': key, 'sha256': hashlib.sha256(text.encode()).hexdigest()} for key, text in sources.items()],
             'initial_copy_baseline': None, 'selection': [{'case_id': case['id'], 'reason': '录制核心路径'}],
             'approved_validation_scope': [], 'cases': [case], 'data': draft['data'], 'questions': questions}
    batch['recording_coverage'] = draft['recording_coverage']
    batch['data_version'] = _digest(batch['data'])
    case['semantic_version'] = _digest(case)
    case['data_version'] = batch['data_version']
    batch['content_version'] = _digest(batch)
    human, tree = _views(batch)
    _credential_guard([batch, human, tree])
    return {'batch': batch, 'human_view': human, 'xmind_markdown': tree}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--recording', required=True)
    parser.add_argument('--interpretation', required=True)
    parser.add_argument('--prd')
    parser.add_argument('--output-dir', required=True, help='New directory only')
    args = parser.parse_args()
    try:
        recording = Path(args.recording).read_text(encoding='utf-8-sig')
        interpretation = json.loads(Path(args.interpretation).read_text(encoding='utf-8-sig'))
        prd = Path(args.prd).read_text(encoding='utf-8-sig') if args.prd else None
        result = build_batch(recording, interpretation, prd)
        output = Path(args.output_dir)
        output.mkdir(parents=True, exist_ok=False)
        (output / 'candidate.json').write_text(json.dumps(result['batch'], ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        (output / 'human-view.md').write_text(result['human_view'], encoding='utf-8')
        (output / 'xmind.md').write_text(result['xmind_markdown'], encoding='utf-8')
    except (ValueError, KeyError, TypeError, AttributeError, OSError):
        print('Candidate conversion rejected: check input contract, credential references and new output directory.', file=sys.stderr)
        return 1
    print('Candidate views written; pending review, not executed or merged.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
