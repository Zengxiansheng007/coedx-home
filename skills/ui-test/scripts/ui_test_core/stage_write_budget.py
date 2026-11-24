"""显式阶段写入预算、计数一致性和连续用例的阶段资格验证。"""
from __future__ import annotations
import copy
import hashlib
import re
from pathlib import Path
from .case_contracts import canonical_hash
from .path_utils import io_path

CONTRACT='stage-budget-v1'
VERIFIED='write_succeeded_verified'
UNATTEMPTED='not_attempted'
STATES={UNATTEMPTED,VERIFIED,'write_outcome_unknown','write_succeeded_verification_failed','write_failed'}

class StageBudgetError(ValueError):
    """稳定错误码，不回显运行时值或凭据。"""

def validate_policies(config):
    policies=config.get('stage_write_policies',[])
    if policies and (config.get('schema_version')!='2.2' or config.get('scope',{}).get('environment')!='test'):
        raise StageBudgetError('E_STAGE_POLICY_TEST_ENV_REQUIRED')
    seen=set()
    for policy in policies:
        key=(policy['case_id'],policy['branch_id'])
        if key in seen:raise StageBudgetError('E_STAGE_POLICY_DUPLICATE_SCOPE')
        seen.add(key)
        make_budget(policy)

def make_budget(policy):
    phases=policy.get('phase_ids')
    if not isinstance(phases,list) or not 1<=len(phases)<=16:
        raise StageBudgetError('E_STAGE_PHASES_INVALID')
    if any(not isinstance(p,str) or not re.fullmatch(r'[A-Za-z0-9._-]{1,80}',p) for p in phases):
        raise StageBudgetError('E_STAGE_PHASE_ID_INVALID')
    if len(set(phases))!=len(phases):raise StageBudgetError('E_STAGE_PHASES_INVALID')
    budget={'contract':CONTRACT,'case_id':policy['case_id'],'branch_id':policy['branch_id'],'phase_ids':list(phases),'max_per_phase':1}
    budget['budget_hash']=canonical_hash(budget)
    return budget

def validate_budget(budget,case_id=None,branch_id=None):
    if not isinstance(budget,dict) or budget.get('contract')!=CONTRACT or budget.get('max_per_phase')!=1:
        raise StageBudgetError('E_STAGE_BUDGET_INVALID')
    expected=make_budget(budget)
    if budget!=expected:raise StageBudgetError('E_STAGE_BUDGET_HASH_MISMATCH')
    if case_id is not None and budget['case_id']!=case_id:raise StageBudgetError('E_STAGE_BUDGET_CASE_MISMATCH')
    if branch_id is not None and budget['branch_id']!=branch_id:raise StageBudgetError('E_STAGE_BUDGET_BRANCH_MISMATCH')
    return copy.deepcopy(budget)

def select_stage_budget(config,case_id,branch_id,risk_level):
    validate_policies(config)
    matches=[p for p in config.get('stage_write_policies',[]) if (p['case_id'],p['branch_id'])==(case_id,branch_id)]
    if not matches:return None
    if risk_level not in ('R2','r2-ui-write-test'):raise StageBudgetError('E_STAGE_POLICY_R2_REQUIRED')
    return make_budget(matches[0])

def check_phase_plan(budget,phases,case_id,branch_id):
    if budget is None:
        if len(phases)>1:raise StageBudgetError('E_STAGE_POLICY_REQUIRED')
        return
    validate_budget(budget,case_id,branch_id)
    if phases!=budget['phase_ids']:raise StageBudgetError('E_STAGE_SOURCE_PLAN_MISMATCH')

def embedded_budget_issues(document,schema_name):
    """JSON Schema之外的哈希、范围、顺序和加总约束。"""
    if not isinstance(document,dict):return []
    budget=document.get('stage_write_budget')
    if schema_name=='execution-context-v3.schema.json':budget=document.get('config_summary',{}).get('stage_write_budget')
    if budget is None:return []
    try:
        validate_budget(budget,document.get('case_id'),document.get('branch_id'))
        if schema_name=='r2-approval-record-v2.schema.json':
            if document['max_submit_count']!=len(budget['phase_ids']):raise StageBudgetError('E_STAGE_APPROVAL_COUNT_MISMATCH')
        if schema_name=='run-result-v5.schema.json':
            rows=document.get('phase_results',[])
            if [row.get('phase_id') for row in rows]!=budget['phase_ids']:raise StageBudgetError('E_STAGE_RESULT_PHASES_MISMATCH')
            total=0
            stopped=False
            for row in rows:
                count=row.get('submit_count')
                state=row.get('write_state')
                if type(count) is not int or count not in (0,1) or state not in STATES:raise StageBudgetError('E_STAGE_RESULT_INVALID')
                if (count==0)!=(state==UNATTEMPTED):raise StageBudgetError('E_STAGE_RESULT_COUNT_STATE_MISMATCH')
                if stopped and count:raise StageBudgetError('E_STAGE_RESULT_AFTER_UNRESOLVED')
                total+=count
                if state!=VERIFIED:stopped=True
            if total!=document['submit_count']:raise StageBudgetError('E_STAGE_RESULT_TOTAL_MISMATCH')
            if document['overall_status']=='passed' and (stopped or total!=len(rows)):
                raise StageBudgetError('E_STAGE_RESULT_FALSE_PASS')
    except (StageBudgetError,KeyError,TypeError) as error:
        return [{'code':str(error) if isinstance(error,StageBudgetError) else 'E_STAGE_RESULT_INVALID','path':'/stage_write_budget','message':'阶段预算或结果不一致'}]
    return []

class StagePermitLedger:
    """许可发放与消费分离；未知、失败或未消费的许可不能推进下一阶段。"""
    def __init__(self,budget=None):
        self.budget=validate_budget(budget) if budget is not None else None
        self.phase_ids=list(budget['phase_ids']) if budget else ['single']
        self.rows=[{'phase_id':p,'submit_count':0,'write_state':UNATTEMPTED} for p in self.phase_ids]
        self.issued=set()

    def reserve(self,phase_id=None):
        phase=phase_id if self.budget else 'single'
        if self.budget is None and phase_id is not None:raise StageBudgetError('E_UNDECLARED_PHASE')
        if phase not in self.phase_ids:raise StageBudgetError('E_STAGE_NOT_AUTHORIZED')
        index=self.phase_ids.index(phase)
        if phase in self.issued:raise StageBudgetError('E_STAGE_PERMIT_ALREADY_ISSUED')
        if any(row['write_state']!=VERIFIED for row in self.rows[:index]):raise StageBudgetError('E_STAGE_PREDECESSOR_NOT_VERIFIED')
        self.issued.add(phase)
        def consume():
            row=self.rows[index]
            if row['submit_count']:raise StageBudgetError('E_STAGE_PERMIT_ALREADY_CONSUMED')
            row.update(submit_count=1,write_state='write_outcome_unknown')
        return consume

    def record(self,phase_id,state):
        phase=phase_id if self.budget else 'single'
        if phase not in self.phase_ids or state not in STATES-{UNATTEMPTED}:raise StageBudgetError('E_STAGE_OUTCOME_INVALID')
        row=self.rows[self.phase_ids.index(phase)]
        if row['submit_count']!=1 or row['write_state']!='write_outcome_unknown':raise StageBudgetError('E_STAGE_OUTCOME_NOT_PENDING')
        row['write_state']=state

def qualification_prefix(steps,phase_index=0):
    submits=[i for i,s in enumerate(steps) if s['action']=='submit']
    if not 0<=phase_index<len(submits):raise StageBudgetError('E_STAGE_QUALIFICATION_PHASE_INVALID')
    return steps[:submits[phase_index]]

def build_stage_qualification(*,run_id,case_id,branch_id,build_fingerprint,budget,steps,step_results,screenshot_ref,screenshot_sha256,phase_index=0,prior_submit_count=0):
    validate_budget(budget,case_id,branch_id)
    phases=[s.get('parameters',[{}])[0].get('value') for s in steps if s['action']=='submit']
    check_phase_plan(budget,phases,case_id,branch_id)
    prefix=qualification_prefix(steps,phase_index)
    expected=[s.get('source_step_id',s.get('step_id')) for s in prefix]
    actual=[s['step_id'] for s in step_results if s['status']=='passed']
    if actual!=expected or len(actual)!=len(step_results):raise StageBudgetError('E_STAGE_QUALIFICATION_COVERAGE')
    if prior_submit_count!=phase_index:raise StageBudgetError('E_STAGE_QUALIFICATION_PRIOR_COUNT')
    result={'schema_version':'ui-test.stage-pre-submit-qualification.v1','run_id':run_id,'case_id':case_id,'branch_id':branch_id,'build_fingerprint':build_fingerprint,'stage_write_budget':budget,'qualification_scope':'first-write-boundary' if phase_index==0 else 'phase-boundary','qualified_phase_id':budget['phase_ids'][phase_index],'deferred_phase_ids':budget['phase_ids'][phase_index+1:],'prior_submit_count':prior_submit_count,'current_phase_submit_count':0,'step_results':copy.deepcopy(step_results),'screenshot_ref':screenshot_ref,'screenshot_sha256':screenshot_sha256,'overall_status':'passed','sequence_allocated':False}
    result['qualification_hash']=canonical_hash(result)
    return result

def validate_stage_qualification(document,*,steps,budget,build_fingerprint,root,activation=False):
    from .case_contracts import validate_document
    if validate_document(document,'stage-pre-submit-qualification.schema.json'):raise StageBudgetError('E_STAGE_QUALIFICATION_SCHEMA')
    validate_budget(document['stage_write_budget'],budget['case_id'],budget['branch_id'])
    if document['stage_write_budget']!=budget or document['build_fingerprint']!=build_fingerprint:raise StageBudgetError('E_STAGE_QUALIFICATION_IDENTITY')
    expected_hash=canonical_hash({k:v for k,v in document.items() if k!='qualification_hash'})
    if document['qualification_hash']!=expected_hash:raise StageBudgetError('E_STAGE_QUALIFICATION_HASH')
    index=budget['phase_ids'].index(document['qualified_phase_id'])
    rebuilt=build_stage_qualification(run_id=document['run_id'],case_id=document['case_id'],branch_id=document['branch_id'],build_fingerprint=build_fingerprint,budget=budget,steps=steps,step_results=document['step_results'],screenshot_ref=document['screenshot_ref'],screenshot_sha256=document['screenshot_sha256'],phase_index=index,prior_submit_count=document['prior_submit_count'])
    if rebuilt!=document:raise StageBudgetError('E_STAGE_QUALIFICATION_CONTENT')
    if activation and index!=0:raise StageBudgetError('E_STAGE_ACTIVATION_REQUIRES_FIRST_BOUNDARY')
    ref=Path(document['screenshot_ref'])
    if ref.is_absolute() or ref.drive or ref.root or '..' in ref.parts:raise StageBudgetError('E_STAGE_SCREENSHOT_REF')
    if 'sha256:'+hashlib.sha256(io_path(Path(root)/ref).read_bytes()).hexdigest()!=document['screenshot_sha256']:
        raise StageBudgetError('E_STAGE_SCREENSHOT_HASH')
    return True
