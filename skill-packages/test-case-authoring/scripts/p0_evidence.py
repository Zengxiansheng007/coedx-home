"""Read-only P0 evidence reconciliation; never executes or merges cases."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys

from authoring import _credential_guard, _digest
from scoped_review import build_scoped_review, GROUPS


def _checks(case):
    return {f'{group}/{i}/verification/{j}': claim
            for group in GROUPS for i, step in enumerate(case.get(group, []))
            for j, claim in enumerate(step.get('verification', []))}


def _validate_catalog(catalog, round_id):
    build_scoped_review(catalog, round_id, [
        {'case_id': c['id'], 'action': 'related', 'reason': 'Read whole P0 evidence scope'}
        for c in catalog.get('cases', [])])


def approve_p0_scope(catalog, round_id, case_ids, actual_reply):
    """Bind the explicitly approved *whole round* independently of display/merge."""
    _credential_guard([catalog, round_id, case_ids, actual_reply])
    # Reuse the full-catalog reader/identity boundary rather than accepting a copy.
    _validate_catalog(catalog, round_id)
    indexed = {c['id']: c for c in catalog['cases']}
    if not round_id or not actual_reply.strip() or not case_ids or len(set(case_ids)) != len(case_ids):
        raise ValueError('Explicit whole P0 scope approval required')
    cases = {}
    for identity in case_ids:
        case = indexed[identity]
        if case['priority'] != 'P0' or not case.get('semantic_version') or not case.get('data_version') or not _checks(case):
            raise ValueError('Versioned P0 and necessary checks required')
        if any(not step.get('verification') or not step.get('expected')
               for group in GROUPS for step in case.get(group, [])):
            raise ValueError('Every operation needs expected results and necessary checks')
        refs = {ref for group in GROUPS for step in case.get(group, []) for ref in step.get('data_refs', [])}
        cases[identity] = {'case': copy.deepcopy(case), 'required_checks': _checks(case),
                           'data': [copy.deepcopy(d) for d in catalog['data'] if d['id'] in refs]}
    result = {'kind': 'p0_validation_baseline', 'schema_version': 1,
              'round_id': round_id, 'source_ref': catalog['source_ref'],
              'catalog_version': catalog['content_version'], 'catalog_digest': _digest(catalog),
              'actual_reply': actual_reply, 'cases': cases}
    result['id'] = _digest(result)
    return result


def check_extension(catalog, baseline, reports, request, *, mode='production'):
    """Reconcile supplied report contents and decisions, retaining every scoped P0."""
    _credential_guard([catalog, baseline, reports, request])
    _validate_catalog(catalog, baseline['round_id'])
    if mode not in ('production', 'simulation'):
        raise ValueError('Unknown evidence mode')
    payload = {k: v for k, v in baseline.items() if k != 'id'}
    if baseline.get('kind') != 'p0_validation_baseline' or baseline.get('id') != _digest(payload):
        raise ValueError('Changed P0 approval baseline')
    if mode == 'production' and any(r.get('synthetic') is not False for r in reports):
        raise ValueError('Real use requires actual reports; synthetic or unspecified nature refused')
    if mode == 'production' and 'synthetic://' in json.dumps([catalog, baseline, reports, request]):
        raise ValueError('Synthetic provenance cannot become actual evidence by relabeling')
    current = {c['id']: c for c in catalog['cases']}
    rows = []
    for identity, frozen in baseline['cases'].items():
        case = frozen['case']
        matches = [r for r in reports if r.get('case_id') == identity]
        status, reason, report = 'pending_check', 'Missing or ambiguous report', None
        if len(matches) == 1:
            report = matches[0]
            versions = all(report.get(k) == case.get(k) for k in ('module_path', 'semantic_version', 'data_version'))
            now = current.get(identity)
            # Workflow metadata may change after partial merge; business content may not.
            ignore = {'merge_status', 'execution_status', 'review_status', 'review_history'}
            unchanged = now is not None and {k:v for k,v in now.items() if k not in ignore} == {k:v for k,v in case.items() if k not in ignore}
            data = {d['id']: d for d in catalog['data']}
            unchanged = unchanged and all(data.get(d['id']) == d for d in frozen['data'])
            valid = (versions and unchanged and report.get('kind') == 'p0_execution_report'
                     and catalog.get('source_ref') == baseline['source_ref']
                     and report.get('round_id') == baseline['round_id']
                     and report.get('tested_version') == request.get('tested_version')
                     and bool(report.get('tested_version')) and bool(report.get('report_ref'))
                     and report.get('purpose') == 'functional_validation')
            if not valid:
                reason = 'Scope, version, purpose or source mismatch'
            elif report.get('result') in ('failed', 'not_run'):
                status, reason = report['result'], 'Matching report result'
            elif report.get('result') == 'passed':
                evidence = report.get('evidence', [])
                verified = {e.get('check_id') for e in evidence
                            if e.get('ref') and isinstance(e.get('content'), str) and e['content'].strip()
                            and e.get('sha256') == hashlib.sha256(e['content'].encode()).hexdigest()}
                if set(frozen['required_checks']) <= verified:
                    status, reason = 'passed', 'Matching necessary evidence contents supplied'
                else:
                    reason = 'Missing necessary evidence contents or digest mismatch'
        rows.append({'case_id': identity, 'module_path': case['module_path'], 'priority': 'P0',
                     'rule_status': current.get(identity, case).get('rule_status', 'unconfirmed'),
                     'review_status': current.get(identity, case).get('review_status', 'pending'),
                     'merge_status': current.get(identity, case).get('merge_status', 'not_merged'),
                     'execution_status': status, 'reason': reason,
                     'semantic_version': case['semantic_version'], 'data_version': case['data_version'],
                     'tested_version': report.get('tested_version') if report else None,
                     'report_ref': report.get('report_ref') if report else None,
                     'provisional_conditions': case.get('rule_decisions', [])})
    blockers = []
    manual = request.get('manual_start', {})
    if manual.get('baseline_id') != baseline['id'] or not manual.get('actual_reply', '').strip():
        blockers.append('manual_start_required')
    if not rows or any(r['execution_status'] != 'passed' for r in rows):
        blockers.append('whole_p0_not_passed')
    provisional = any(r['rule_status'] == 'provisional' for r in rows)
    continuation = request.get('provisional_continue', {})
    if provisional and not (continuation.get('continue') is True and continuation.get('actual_reply', '').strip()
                            and continuation.get('baseline_id') == baseline['id']):
        blockers.append('provisional_continue_required')
    if any(r['rule_status'] not in ('formal', 'provisional') for r in rows):
        blockers.append('unconfirmed_or_deferred_rules')
    if any(r['review_status'] != 'approved' for r in rows):
        blockers.append('p0_final_review_required')
    gap_review = request.get('gap_review', {})
    if not (gap_review.get('completed') is True and gap_review.get('basis') and gap_review.get('summary')):
        blockers.append('gap_review_required')
    gaps = []
    identities = set()
    for gap in request.get('gaps', []):
        if not gap.get('id') or gap['id'] in identities or not gap.get('proposal') or not gap.get('basis'):
            raise ValueError('Unique gap proposal and source basis required')
        identities.add(gap['id'])
        decision = gap.get('decision', {})
        route = decision.get('route')
        if route not in ('supplement_p0', 'extension', 'exclude') or not decision.get('actual_reply', '').strip():
            blockers.append('gap_decision_required:' + gap['id'])
            route = 'pending'
        if route == 'supplement_p0':
            blockers.append('supplement_p0_required:' + gap['id'])
        gaps.append(dict(copy.deepcopy(gap), route=route,
                         next_step='clarify_review_ui_test_validate_user_merge' if route == 'supplement_p0' else route))
    return {'baseline_id': baseline['id'], 'round_id': baseline['round_id'],
            'evidence_nature': 'simulated' if mode == 'simulation' else 'actual_report_contents',
            'cases': rows, 'gaps': gaps, 'decisions': copy.deepcopy(request),
            'blockers': blockers, 'can_extend': not blockers,
            'next_step': 'author_P1_P2' if not blockers else 'resolve_blockers',
            'formal_integration': 'pending_joint_validation'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', required=True)
    parser.add_argument('--request', required=True)
    parser.add_argument('--baseline')
    parser.add_argument('--reports')
    parser.add_argument('--mode', choices=['production', 'simulation'], default='production')
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    def read(path):
        return json.loads(Path(path).read_text(encoding='utf-8-sig'))
    try:
        catalog, request = read(args.catalog), read(args.request)
        if args.baseline:
            result = check_extension(catalog, read(args.baseline), read(args.reports) if args.reports else [], request, mode=args.mode)
            name = 'extension-check.json'
        else:
            result = approve_p0_scope(catalog, **request)
            name = 'p0-validation-baseline.json'
        output = Path(args.output_dir)
        output.mkdir(parents=True, exist_ok=False)
        (output / name).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    except (ValueError, KeyError, TypeError, AttributeError, OSError):
        print('P0 evidence check rejected: inspect report, scope and evidence contract.', file=sys.stderr)
        return 1
    print('Read-only P0 evidence check written; no execution or merge performed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
