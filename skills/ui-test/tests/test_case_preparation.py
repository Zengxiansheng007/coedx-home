import json
import copy
import io
import zipfile
import xml.etree.ElementTree as ET
import pytest
import tempfile
from pathlib import Path

from scripts.ui_test_core.case_preparation import inspect_recording


@pytest.mark.parametrize('record', [
    'page.goto(url="https://user:SYNTHETIC@demo.invalid/")',
    'page.wait_for_url(url="https://demo.invalid/?%74oken=SYNTHETIC")',
    'page.get_by_label("Title").fill(value="token=SYNTHETIC")',
    'page.get_by_label("Title").select_option([{"label":"token=SYNTHETIC"}])',
    'page.get_by_label("Title").fill({"password":"SYNTHETIC"})',
])
def test_every_recorded_value_is_sanitized_with_a_step_gap(record):
    result=inspect_recording(record)
    assert 'SYNTHETIC' not in json.dumps(result)
    assert any(g['code']=='CREDENTIAL_REF_REQUIRED' and g['step_id']=='REC-001' for g in result['gaps'])


def test_recording_observations_cannot_reuse_one_action_or_unrelated_assertion():
    result=inspect_recording('page.get_by_label("Title").click()\n',expected_steps=[
        dict(step_id='one',action='click'),dict(step_id='two',action='click')])
    assert any(g['step_id']=='two' and g['code']=='MISSING_ACTION' for g in result['gaps'])
    result=inspect_recording('expect(page.get_by_label("First")).to_have_value("before")\npage.get_by_label("Last").fill("after")\n')
    assert any(g['step_id']=='REC-002' and g['code']=='EXPECTED_RESULT_UNKNOWN' for g in result['gaps'])


@pytest.mark.parametrize('record',[
    'page.get_by_label("内容").fill("季度公告")\n',
    'page.get_by_label("标题").fill(value="不同值")\n',
])
def test_recording_origin_matches_declared_target_and_bound_parameter(record):
    from scripts.ui_test_core.case_preparation import prepare_branch
    m=material(); m['recording']=record
    m['origins']['title-step']=dict(kind='recording',source_line=1,
        target='page.get_by_label([['+json.dumps('标题',ensure_ascii=False)+'], {}])',
        parameter_id='title',expectation_reference='human:expected-title')
    result=prepare_branch(**{k:m[k] for k in ('source_case','test_data','recording','origins')})
    assert any(g['code']=='RECORDING_ORIGIN_MISMATCH' and g['step_id']=='title-step' for g in result['gaps'])


def test_fork_data_change_needs_explicit_expectation_reconciliation():
    from scripts.ui_test_core.case_preparation import prepare_branch,fork_branch,compile_prepared_branch
    m=material(); parent=prepare_branch(**{k:m[k] for k in ('source_case','test_data','recording','origins')})
    fork=fork_branch(parent,branch_id='rewritten',origin_reference='human:rewrite',parameters={'title':'新值'})
    assert any(g['code']=='BRANCH_EXPECTATION_REVIEW_REQUIRED' and g['step_id']=='title-step' for g in fork['gaps'])
    with pytest.raises(ValueError,match='E_PREPARATION_NEEDS_CLARIFICATION'):
        compile_prepared_branch(fork,config=m['config'],selection=dict(m['selection'],branch_id='rewritten'),
            dependency_assets=m['dependency_assets'],page_module_registry=m['page_module_registry'])


def test_export_provenance_content_is_bound_to_original_preparation():
    from scripts.ui_test_core.case_preparation import prepare_branch,compile_prepared_branch,export_xmind
    m=material(); prepared=prepare_branch(**{k:m[k] for k in ('source_case','test_data','recording','origins')})
    compiled=compile_prepared_branch(prepared,**{k:m[k] for k in ('config','selection','dependency_assets','page_module_registry')})
    compiled['provenance']['source_origins']['title-step']['reference']='human:replacement'
    with pytest.raises(ValueError,match='E_DERIVATIVE_ATTACHMENT_CHANGED'):
        export_xmind(compiled)


def test_xmind_requires_verified_release_and_serializes_only_aggregate(tmp_path):
    from scripts.ui_test_core.case_preparation import prepare_branch,compile_prepared_branch,export_xmind
    from scripts.ui_test_core.case_sync import create_sync_plan,apply_sync_plan
    m=material(); prepared=prepare_branch(**{k:m[k] for k in ('source_case','test_data','recording','origins')})
    compiled=compile_prepared_branch(prepared,**{k:m[k] for k in ('config','selection','dependency_assets','page_module_registry')})
    with pytest.raises(ValueError,match='E_XMIND_VERIFIED_RELEASE_REQUIRED'):
        export_xmind(compiled)
    target=tmp_path/'case'; plan=create_sync_plan(compiled,target)
    assert apply_sync_plan(plan,lambda:compiled,target)['status']=='applied'
    release=target/'releases'/compiled['manifest']['build_fingerprint'].removeprefix('sha256:')
    archive=export_xmind(compiled,release_path=release,display_registry=display_registry())
    with zipfile.ZipFile(io.BytesIO(archive)) as workbook:
        outline=json.loads(workbook.read('aggregate.outline.json'))
        manifest=json.loads(workbook.read('aggregate-manifest.json'))
        assert outline['node_type']=='project-group'
        assert outline['children'][0]['node_type']=='product'
        assert manifest['status']=='in_sync' and manifest['included_cases'][0]['source_hash']==compiled['manifest']['source_hash']
        xml=ET.fromstring(workbook.read('content.xml'))
        topic=xml.find('.//{urn:xmind:xmap:xmlns:content:2.0}topic')
        def assert_projection(topic,node):
            assert topic.find('{urn:xmind:xmap:xmlns:content:2.0}title').text==node['label']
            children=topic.findall('./{urn:xmind:xmap:xmlns:content:2.0}children/{urn:xmind:xmap:xmlns:content:2.0}topics/{urn:xmind:xmap:xmlns:content:2.0}topic')
            assert len(children)==len(node['children'])
            for child,n in zip(children,node['children']): assert_projection(child,n)
        assert_projection(topic,outline)
    (release/'human-view.md').write_text('篡改',encoding='utf-8')
    with pytest.raises(ValueError,match='E_XMIND_VERIFIED_RELEASE_REQUIRED'):
        export_xmind(compiled,release_path=release,display_registry=display_registry())


def display_registry():
    return dict(project_groups={'demo-region':'演示项目组'},products={'demo-platform':'演示管理系统'},
        systems={'demo-notice-workbench':'演示管理系统'},modules={'operations-config':'运营配置',
        'message-management':'消息管理','announcement-management':'公告管理'},functions={'create':'创建'})


def export_ready(compiled):
    from scripts.ui_test_core.case_sync import create_sync_plan,apply_sync_plan
    from scripts.ui_test_core.case_preparation import export_xmind
    with tempfile.TemporaryDirectory(prefix='uit02-export-') as folder:
        target=Path(folder)/'case'; plan=create_sync_plan(compiled,target)
        assert apply_sync_plan(plan,lambda:compiled,target)['status']=='applied'
        release=target/'releases'/compiled['manifest']['build_fingerprint'].removeprefix('sha256:')
        return export_xmind(compiled,release_path=release,display_registry=display_registry())


@pytest.mark.parametrize('record',[
    'page.get_by_text("https://user:SYNTHETIC@demo.invalid/").click()',
    'page.get_by_label("Title").fill("Visit https://user:SYNTHETIC@demo.invalid/")',
    'page.locator("[href=\\\"https://user:SYNTHETIC@demo.invalid/\\\"]").click()',
])
def test_embedded_credential_urls_are_sanitized_in_every_text(record):
    result=inspect_recording(record)
    assert 'SYNTHETIC' not in json.dumps(result)
    assert any(g['code']=='CREDENTIAL_REF_REQUIRED' for g in result['gaps'])


def test_preparation_rejects_embedded_credential_url_in_ordinary_material():
    from scripts.ui_test_core.case_preparation import prepare_branch
    m=material(); m['source_case']['steps'][1]['intent']='Visit https://user:SYNTHETIC@demo.invalid/'
    with pytest.raises(ValueError,match='E_PREPARATION_CREDENTIAL_REFERENCE_REQUIRED'):
        prepare_branch(**{k:m[k] for k in ('source_case','test_data','recording','origins')})


@pytest.mark.parametrize('ref',['https://user:SYNTHETIC@demo.invalid/','run:token:SYNTHETIC',{'token':'SYNTHETIC'}])
def test_every_derivative_consumer_refuses_unsafe_appended_failure_refs(ref):
    from scripts.ui_test_core.case_preparation import prepare_branch,compile_prepared_branch,diagnose_source_change,export_xmind
    m=material(); prepared=prepare_branch(**{k:m[k] for k in ('source_case','test_data','recording','origins')})
    compiled=compile_prepared_branch(prepared,**{k:m[k] for k in ('config','selection','dependency_assets','page_module_registry')})
    compiled['provenance']['failure_refs']=[ref]
    with pytest.raises(ValueError,match='E_FAILURE_REFERENCE_INVALID'):
        export_xmind(compiled)
    with pytest.raises(ValueError,match='E_FAILURE_REFERENCE_INVALID'):
        diagnose_source_change(compiled,compiled)


def test_fork_reconciles_direct_test_data_postcondition_dependencies():
    from scripts.ui_test_core.case_preparation import prepare_branch,compile_prepared_branch,fork_branch
    m=material(); m['source_case']['steps'][1]['postconditions'][0]['expected_ref']='test-data:/parameters/expected_title'
    m['test_data']['parameters']['expected_title']='季度公告'
    parent=prepare_branch(**{k:m[k] for k in ('source_case','test_data','recording','origins')})
    parameters=dict(parent['test_data']['parameters'],expected_title='新期望')
    fork=fork_branch(parent,branch_id='rewritten',origin_reference='human:direct-expectation-rewrite',parameters=parameters)
    assert any(g['code']=='BRANCH_EXPECTATION_REVIEW_REQUIRED' and g['step_id']=='title-step' for g in fork['gaps'])
    with pytest.raises(ValueError,match='E_PREPARATION_NEEDS_CLARIFICATION'):
        compile_prepared_branch(fork,config=m['config'],selection=dict(m['selection'],branch_id='rewritten'),
            dependency_assets=m['dependency_assets'],page_module_registry=m['page_module_registry'])
    fork=fork_branch(parent,branch_id='rewritten',origin_reference='human:direct-expectation-rewrite',parameters=parameters,
        step_updates={'title-step':dict(expected_result='标题值为新期望',postconditions=copy.deepcopy(m['source_case']['steps'][1]['postconditions']))})
    assert fork['status']=='reviewable' and '新期望' in fork['source_case']['steps'][1]['expected_result']


def test_direct_keyword_selector_is_part_of_recorded_target():
    result=inspect_recording('page.fill(selector="#title",value="ordinary")')
    assert result['steps'][0]['target']=='page."#title"'
    assert result['steps'][0]['keyword_arguments']=={'value':'ordinary'}
    assert not inspect_recording('page.click()')['steps']


def test_unchanged_fork_with_repeated_parameters_does_not_invent_data_drift():
    from scripts.ui_test_core.case_preparation import prepare_branch,fork_branch
    m=material(); m['source_case']['steps'][0]['parameter_ids'].append('title')
    parent=prepare_branch(**{k:m[k] for k in ('source_case','test_data','recording','origins')})
    fork=fork_branch(parent,branch_id='rewritten',origin_reference='human:unchanged-clone')
    assert fork['status']=='reviewable' and fork['gaps']==[] and fork['approved'] is False


@pytest.mark.parametrize('escape',['%20','%27','%22','%2F','%3F','%23'])
def test_encoded_userinfo_keeps_boundaries_before_redaction(escape):
    from scripts.ui_test_core.case_preparation import prepare_branch
    url='https://user:SYNTHETIC'+escape+'@demo.invalid/'
    for record in [f'page.goto(url={url!r})',f'page.get_by_text({url!r}).click()',
                   f'page.get_by_label("Title").fill({("Visit "+url)!r})']:
        result=inspect_recording(record)
        assert 'SYNTHETIC' not in json.dumps(result)
        assert any(g['code']=='CREDENTIAL_REF_REQUIRED' for g in result['gaps'])
    m=material(); m['test_data']['notes']='Visit '+url
    with pytest.raises(ValueError,match='E_PREPARATION_CREDENTIAL_REFERENCE_REQUIRED'):
        prepare_branch(**{k:m[k] for k in ('source_case','test_data','recording','origins')})


@pytest.mark.parametrize('field',['notes','expected_defaults','parameter-key','encoded-key','metadata-description','runtime-ref'])
def test_complete_test_data_document_and_all_keys_are_checked(field):
    from scripts.ui_test_core.case_preparation import prepare_branch
    m=material(); secret='https://user:SYNTHETIC@demo.invalid/'
    if field=='notes': m['test_data']['notes']='Visit '+secret
    elif field=='expected_defaults': m['test_data']['expected_defaults']={'password':'SYNTHETIC'}
    elif field=='parameter-key': m['test_data']['parameters'][secret]='ordinary'
    elif field=='encoded-key': m['test_data']['expected_defaults']={'%70assword':'SYNTHETIC'}
    elif field=='metadata-description': m['test_data']['metadata']['description']='Visit '+secret
    elif field=='runtime-ref': m['test_data']['runtime_refs'].append('value:'+secret)
    with pytest.raises(ValueError,match='E_PREPARATION_CREDENTIAL_REFERENCE_REQUIRED'):
        prepare_branch(**{k:m[k] for k in ('source_case','test_data','recording','origins')})


def test_encoded_locator_sensitive_label_cannot_declassify_credential_value():
    result=inspect_recording('page.get_by_label("%70assword").fill("SYNTHETIC")')
    assert 'SYNTHETIC' not in json.dumps(result)
    assert any(g['code']=='CREDENTIAL_REF_REQUIRED' for g in result['gaps'])


def test_safe_optional_data_and_url_text_remain_ordinary():
    from scripts.ui_test_core.case_preparation import prepare_branch
    url='https://demo.invalid/a%20b?title=Quarterly'
    result=inspect_recording(f'page.goto(url={url!r})')
    assert result['steps'][0]['keyword_arguments']['url']==url
    assert not any(g['code']=='CREDENTIAL_REF_REQUIRED' for g in result['gaps'])
    m=material(); m['test_data'].update(notes='Visit '+url,expected_defaults={'title':'季度公告'})
    assert prepare_branch(**{k:m[k] for k in ('source_case','test_data','recording','origins')})['status']=='reviewable'


@pytest.mark.parametrize('value',[
    '//user:SYNTHETIC%20@demo.invalid/',
    'https%3A%2F%2Fuser%3ASYNTHETIC%20%40demo.invalid%2F',
    'session_id=SYNTHETIC',
])
def test_network_path_encoded_wrapper_and_session_fields_use_same_safety_boundary(value):
    from scripts.ui_test_core.case_preparation import prepare_branch
    result=inspect_recording(f'page.goto(url={value!r})')
    assert 'SYNTHETIC' not in json.dumps(result)
    assert any(g['code']=='CREDENTIAL_REF_REQUIRED' for g in result['gaps'])
    m=material(); m['test_data']['notes']=value
    with pytest.raises(ValueError,match='E_PREPARATION_CREDENTIAL_REFERENCE_REQUIRED'):
        prepare_branch(**{k:m[k] for k in ('source_case','test_data','recording','origins')})


@pytest.mark.parametrize('code,action,line,cause',[
    ('MISSING_DROPDOWN','select_option',2,None),('MISSING_SCROLL','scroll_into_view_if_needed',2,None),
    ('INVISIBLE_TARGET','click',2,'evidence:hidden-2'),('RECORDING_INTERRUPTED','click',2,'evidence:interrupted-2')])
def test_missing_recording_steps_are_diagnosed_without_fabrication(code,action,line,cause):
    result=inspect_recording('page.get_by_label("标题").fill("实际标题")\n',
        expected_steps=[dict(step_id='business-step-2',action=action,source_line=line,gap_code=code,cause_ref=cause)])
    gap=next(g for g in result['gaps'] if g['code']==code)
    assert gap['step_id']=='business-step-2' and gap['source_line']==2
    assert gap['reason']==('evidenced' if cause else 'unknown')
    assert len(result['steps'])==1 and result['steps'][0]['expected_result'] is None


def test_dynamic_and_invisible_recorded_targets_keep_unknown_results():
    result=inspect_recording('page.locator("#rc_select_209").click()\npage.get_by_text("隐藏目标").is_hidden()\n')
    assert [(g['code'],g['step_id']) for g in result['gaps'] if g['code'] in {'DYNAMIC_TARGET','VISIBILITY_RESULT_UNKNOWN'}]==[
        ('DYNAMIC_TARGET','REC-001'),('VISIBILITY_RESULT_UNKNOWN','REC-002')]
    assert all(s['expected_result'] is None for s in result['steps'])


def material():
    from tests.fixtures_v2 import source_case_v2,make_test_data_document
    from tests.test_project_paths import project_v2,selection
    case=source_case_v2(); data=make_test_data_document()
    case.update(case_id='DEMO-ANNOUNCEMENT-P0-A',branch_id='system-announcement',risk_level='R1',
        scope=dict(project_group='demo-region',product='demo-platform',system='demo-notice-workbench',
                   module_path=['operations-config','message-management','announcement-management'],function='create'),
        parameter_bindings=[dict(parameter_id='title',label='标题',ref='test-data:/parameters/title'),
                            dict(parameter_id='rule',label='日期规则',ref='test-data:/generation_rules/date_offset')],
        dependency_refs=['component.title','flow.open'])
    case['steps']=[dict(step_id='title-step',section='feature',intent='输入标题',action='fill',module_id='title',
        parameter_ids=['title','rule'],expected_result='标题值为季度公告',binding_ref='component.title',evidence=['dom'],
        postconditions=[dict(assertion_id='title-value',operator='equals',expected_ref='parameter:title',evidence=['dom'])])]
    case['steps'].insert(0,dict(step_id='open',section='setup',intent='进入表单',action='flow',module_id='page.title',
        parameter_ids=[],expected_result='表单可见',binding_ref='flow.open',
        postconditions=[dict(assertion_id='form-ready',operator='visible',expected_ref='literal:true',evidence=['dom'])]))
    data.update(case_id=case['case_id'],branch_id=case['branch_id'],parameters={'title':'季度公告'},
                generation_rules={'date_offset':1},runtime_refs=[])
    config=project_v2(); config['write_ready']=True
    config['asset_governance'].update(execution_asset_root=r'D:\test\ui_test',knowledge_root=r'D:\test\rag',staging_root=r'D:\test\ui_test\_tmp')
    registry=dict(schema_version='ui-test.page-module-registry.v1',page_id='title-page',
        modules={'title':dict(display_name='标题',branch_modes={'system-announcement':'operate','rewritten':'operate'},assertion_binding_ref='component.title')})
    return dict(source_case=case,test_data=data,config=config,selection=selection(),
        dependency_assets={'component.title':{'version':1},'flow.open':{'version':1}},page_module_registry=registry,
        recording='page.get_by_label("标题").fill("季度公告")\nexpect(page.get_by_label("标题")).to_have_value("季度公告")\n',
        origins={'title-step':dict(kind='human',reference='human:case-author-v1'),
                 'open':dict(kind='human',reference='human:setup-v1')})


def test_preparation_consumers_share_real_values_and_versioned_provenance():
    from scripts.ui_test_core.case_preparation import prepare_branch,compile_prepared_branch,export_xmind
    inputs=material(); original=copy.deepcopy(inputs)
    prepared=prepare_branch(**{k:inputs[k] for k in ('source_case','test_data','recording','origins')})
    assert prepared['status']=='reviewable' and prepared['approved'] is False
    assert '季度公告' in prepared['human_view'] and 'date_offset' in prepared['human_view']
    compiled=compile_prepared_branch(prepared,**{k:inputs[k] for k in ('config','selection','dependency_assets','page_module_registry')})
    assert compiled['manifest']['source_hash']==prepared['snapshot']['dependency_hashes']['source_case']
    assert compiled['manifest']['test_data_hash']==prepared['snapshot']['dependency_hashes']['test_data']
    assert compiled['provenance']['source_origins']['title-step']['reference']=='human:case-author-v1'
    assert compiled['path_plans']['source_case']['target_path'].startswith('D:\\test\\ui_test\\')
    assert 'branches\\system-announcement\\' in compiled['path_plans']['playwright_test']['target_path']
    archive=export_ready(compiled)
    with zipfile.ZipFile(io.BytesIO(archive)) as workbook:
        xml=ET.fromstring(workbook.read('content.xml'))
        assert xml.tag=='{urn:xmind:xmap:xmlns:content:2.0}xmap-content'
        titles=[node.text for node in xml.iter('{urn:xmind:xmap:xmlns:content:2.0}title')]
        assert any('季度公告' in str(title) for title in titles)
        provenance=json.loads(workbook.read('provenance.json'))
        assert provenance['build_fingerprint']==compiled['manifest']['build_fingerprint']
    assert inputs==original


def test_fork_and_changed_source_preserve_prior_assets_and_invalidate_derivatives():
    from scripts.ui_test_core.case_preparation import prepare_branch,compile_prepared_branch,fork_branch,diagnose_source_change,export_xmind
    m=material(); prepared=prepare_branch(**{k:m[k] for k in ('source_case','test_data','recording','origins')})
    old=compile_prepared_branch(prepared,**{k:m[k] for k in ('config','selection','dependency_assets','page_module_registry')})
    old['provenance']['failure_refs']=['run:historical-failure-1']
    original=copy.deepcopy(old); archive=export_ready(old)
    fork=fork_branch(prepared,branch_id='rewritten',origin_reference='human:rewrite-v2',
                     parameters={'title':'改写的公告'},generation_rules={'date_offset':2},
                     step_updates={'title-step':dict(expected_result='标题值为改写的公告',
                         postconditions=copy.deepcopy(m['source_case']['steps'][1]['postconditions']))})
    assert fork['approved'] is False and fork['confirmation_required'] is True
    assert fork['test_data']['branch_id']=='rewritten' and fork['test_data']['data_revision']==2
    assert fork['source_case']['case_version']==3
    assert '改写的公告' in fork['human_view'] and '季度公告' in prepared['human_view']
    selection=dict(m['selection'],branch_id='rewritten')
    current=compile_prepared_branch(fork,config=m['config'],selection=selection,
        dependency_assets=m['dependency_assets'],page_module_registry=m['page_module_registry'])
    diagnostic=diagnose_source_change(current,old)
    assert diagnostic['changed'] is True and diagnostic['confirmation_required'] is True
    assert {'playwright-test.py','product-aggregate.xmind','provenance.json'}.issubset(diagnostic['stale_artifacts'])
    assert diagnostic['preserved_failure_refs']==['run:historical-failure-1']
    assert old==original and export_ready(old)==archive
    fork['test_data']['parameters']['title']='later mutation'
    assert prepared['test_data']['parameters']['title']=='季度公告'
    with pytest.raises(ValueError,match='E_PREPARATION_CHANGED'):
        compile_prepared_branch(fork,config=m['config'],selection=selection,
            dependency_assets=m['dependency_assets'],page_module_registry=m['page_module_registry'])


def test_unresolved_origin_and_wrong_branch_cannot_compile():
    from scripts.ui_test_core.case_preparation import prepare_branch,compile_prepared_branch
    m=material(); prepared=prepare_branch(source_case=m['source_case'],test_data=m['test_data'],origins={})
    assert [g['code'] for g in prepared['gaps']]==['STEP_SOURCE_REQUIRED','STEP_SOURCE_REQUIRED']
    with pytest.raises(ValueError,match='E_PREPARATION_NEEDS_CLARIFICATION'):
        compile_prepared_branch(prepared,**{k:m[k] for k in ('config','selection','dependency_assets','page_module_registry')})
    m['test_data']['branch_id']='another'
    with pytest.raises(ValueError,match='E_SNAPSHOT_BRANCH_MISMATCH'):
        prepare_branch(source_case=m['source_case'],test_data=m['test_data'],origins=m['origins'])


def test_credential_references_only_and_no_store_reads():
    from scripts.ui_test_core.case_preparation import prepare_branch,compile_prepared_branch,export_xmind
    m=material(); m['source_case']['parameter_bindings'].append(dict(parameter_id='auth',label='测试账号密码',ref='credential:shared-login'))
    m['source_case']['steps'][0]['parameter_ids'].append('auth'); m['test_data']['runtime_refs']=['credential:shared-login']
    prepared=prepare_branch(**{k:m[k] for k in ('source_case','test_data','recording','origins')})
    compiled=compile_prepared_branch(prepared,**{k:m[k] for k in ('config','selection','dependency_assets','page_module_registry')})
    assert 'credential:shared-login' in prepared['human_view']
    auth=next(p for p in compiled['parameter_manifest']['parameters'] if p['parameter_id']=='auth')
    assert auth['reference_only'] is True and 'value' not in auth
    assert export_ready(compiled)
    m['test_data']['parameters']['password']='must-never-export'
    with pytest.raises(ValueError,match='E_PREPARATION_CREDENTIAL_REFERENCE_REQUIRED'):
        prepare_branch(**{k:m[k] for k in ('source_case','test_data','recording','origins')})


def test_prepared_data_runs_with_fixed_snapshot_and_rejects_later_drift(tmp_path):
    from scripts.ui_test_core.case_preparation import prepare_branch,compile_prepared_branch
    from scripts.ui_test_core.execution_data_session import ExecutionDataSession,ExecutionDataError
    m=material(); prepared=prepare_branch(**{k:m[k] for k in ('source_case','test_data','recording','origins')})
    compiled=compile_prepared_branch(prepared,**{k:m[k] for k in ('config','selection','dependency_assets','page_module_registry')})
    path=tmp_path/'test-data.json'; path.write_text(json.dumps(compiled['outputs']['test-data.json']),encoding='utf-8')
    session=ExecutionDataSession(parameter_manifest=compiled['parameter_manifest'],test_data_path=path,run_id='RUN-20261007-001',
                                build_fingerprint=compiled['manifest']['build_fingerprint'])
    session.start()
    assert session.consume('title')=='季度公告' and session.consume('rule')==1
    snapshot=session.seal_snapshot(tmp_path/'resolved-test-data.json')
    assert snapshot['test_data_hash']==compiled['manifest']['test_data_hash']
    assert snapshot['branch_id']=='system-announcement'
    fixed=(tmp_path/'resolved-test-data.json').read_bytes()
    changed=copy.deepcopy(m['test_data']); changed['parameters']['title']='运行中改值'
    path.write_text(json.dumps(changed),encoding='utf-8')
    with pytest.raises(ExecutionDataError,match='E_EXECUTION_TEST_DATA_DRIFT'):
        session.consume('title')
    assert (tmp_path/'resolved-test-data.json').read_bytes()==fixed


def test_recording_origin_requires_exact_line_and_own_expectation_source():
    from scripts.ui_test_core.case_preparation import prepare_branch
    m=material(); m['origins']['title-step']=dict(kind='recording',source_line=1,
        target='page.get_by_label([["标题"], {}])',parameter_id='title')
    result=prepare_branch(**{k:m[k] for k in ('source_case','test_data','recording','origins')})
    assert any(g['code']=='EXPECTATION_SOURCE_REQUIRED' and g['step_id']=='title-step' for g in result['gaps'])
    m['origins']['title-step']['expectation_reference']='human:expected-title-1'
    result=prepare_branch(**{k:m[k] for k in ('source_case','test_data','recording','origins')})
    assert result['status']=='reviewable'
    assert result['source_origins']['title-step']['source_line']==1


def test_recording_credential_target_and_url_literals_cannot_escape():
    record='page.locator("input[password=synthetic-secret]").fill("synthetic-secret")\npage.goto("https://user:synthetic-secret@demo.invalid/?token=synthetic-secret")\n'
    result=inspect_recording(record)
    assert 'synthetic-secret' not in json.dumps(result)


def test_export_refuses_changed_compiler_attachment():
    from scripts.ui_test_core.case_preparation import prepare_branch,compile_prepared_branch,export_xmind
    m=material(); prepared=prepare_branch(**{k:m[k] for k in ('source_case','test_data','recording','origins')})
    compiled=compile_prepared_branch(prepared,**{k:m[k] for k in ('config','selection','dependency_assets','page_module_registry')})
    compiled['resolved_ir']['resolved_steps'][1]['intent']='来源外改写'
    with pytest.raises(ValueError,match='E_DERIVATIVE_ATTACHMENT_CHANGED'):
        export_xmind(compiled)


def test_immutable_release_consumer_preserves_older_source_and_failure_artifacts(tmp_path):
    from scripts.ui_test_core.case_preparation import prepare_branch,compile_prepared_branch,diagnose_source_change
    from scripts.ui_test_core.case_sync import create_sync_plan,apply_sync_plan
    m=material(); kwargs={k:m[k] for k in ('config','selection','dependency_assets','page_module_registry')}
    prepared=prepare_branch(**{k:m[k] for k in ('source_case','test_data','recording','origins')})
    old=compile_prepared_branch(prepared,**kwargs)
    target=tmp_path/'case'; plan=create_sync_plan(old,target)
    result=apply_sync_plan(plan,lambda:old,target)
    assert result['status']=='applied'
    release=target/'releases'/old['manifest']['build_fingerprint'].removeprefix('sha256:')
    history={p.name:p.read_bytes() for p in release.iterdir() if p.is_file()}
    failure=target/'failure.json'; failure.write_text('{"run_id":"old-run","status":"failed"}',encoding='utf-8')
    old['provenance']['failure_refs']=['run:old-run']
    m['source_case']['case_version']+=1; m['test_data']['data_revision']+=1
    m['test_data']['parameters']['title']='来源变更后的标题'
    new=compile_prepared_branch(prepare_branch(**{k:m[k] for k in ('source_case','test_data','recording','origins')}),**kwargs)
    plan=create_sync_plan(new,target); assert apply_sync_plan(plan,lambda:new,target)['status']=='applied'
    diag=diagnose_source_change(new,old)
    assert 'playwright-test.py' in diag['stale_artifacts'] and diag['preserved_failure_refs']==['run:old-run']
    assert {p.name:p.read_bytes() for p in release.iterdir() if p.is_file()}==history
    assert json.loads(failure.read_text(encoding='utf-8'))['status']=='failed'


def test_recording_review_keeps_real_values_and_unknown_expectations_without_execution(tmp_path):
    marker=tmp_path/'must-not-exist'
    recording=f'import os\nos.system("echo forbidden > {marker.as_posix()}")\npage.get_by_label("标题").fill("季度公告")\npage.get_by_label("password").fill("synthetic-secret")\n'
    result=inspect_recording(recording)
    assert not marker.exists()
    assert result['steps'][0]['arguments']==['季度公告']
    assert result['steps'][0]['source_line']==3
    assert result['steps'][0]['expected_result'] is None
    assert result['steps'][1]['arguments']==['<credential-ref-required>']
    assert 'synthetic-secret' not in json.dumps(result)
    assert any(g['code']=='UNSUPPORTED_CALL' for g in result['gaps'])
    assert all(step['approved'] is False for step in result['steps'])
