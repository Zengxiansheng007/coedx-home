"""Deterministic P1/P2 design completeness; business interpretation is the skill's job."""
import argparse
import copy
import json
from pathlib import Path
import sys

from authoring import _credential_guard, _digest
from p0_evidence import check_extension
from scoped_review import build_scoped_review, GROUPS, _render


def _coverage(batch):
    design = batch['extension_design']
    cases = {c['id']: c for c in batch['cases']}
    entries = design['coverage']
    rows = {e['check_id']: e for e in entries}
    checks = [c for p in design['manual_points'] for c in p['checks']]
    point_ids = [p['id'] for p in design['manual_points']]
    if len(set(point_ids)) != len(point_ids):
        raise ValueError('Unique manual point identities required')
    ids = [c['id'] for c in checks]
    if not ids or len(set(ids)) != len(ids) or len(rows) != len(entries) or set(rows) != set(ids):
        raise ValueError('Every unique manual check needs exactly one coverage record')
    results, points, boundaries = [], [], {}
    for point in design['manual_points']:
        if not point.get('id') or not point.get('basis') or not point.get('checks'):
            raise ValueError('Manual point identity, source basis and checks required')
        statuses = []
        for check in point['checks']:
            if not check.get('description') or not check.get('aspects') or len(set(check['aspects'])) != len(check['aspects']):
                raise ValueError('Concrete check and unique required aspects needed')
            row = rows[check['id']]
            links = row.get('links', [])
            covered, summaries = set(), []
            for link in links:
                if link['case_id'] not in cases or not link.get('aspects') or not set(link['aspects']) <= set(check['aspects']):
                    raise ValueError('Coverage needs known complete cases and check aspects')
                case = cases[link['case_id']]
                covered.update(link['aspects'])
                summaries.append({'case_id': case['id'], 'module_path': case['module_path'],
                    'expected': [c['text'] for g in GROUPS for s in case.get(g, []) for c in s['expected']],
                    'verification': [c['text'] for g in GROUPS for s in case.get(g, []) for c in s['verification']]})
            missing = sorted(set(check['aspects']) - covered)
            decision = row.get('decision', {})
            if decision:
                if decision.get('route') not in ('deferred', 'excluded') or not decision.get('actual_reply', '').strip() or not decision.get('basis'):
                    raise ValueError('Explicit user disposition and basis required')
                if links:
                    raise ValueError('Disposition cannot hide linked coverage; split the check')
                status = decision['route']
            else:
                status = 'complete' if not missing else 'partial' if covered else 'gap'
            if missing and not decision and not row.get('pending'):
                raise ValueError('Missing aspects need a concrete pending explanation')
            if check.get('boundary_group') and links:
                if 'input' not in check or check['input'] is None or len(links) != 1:
                    raise ValueError('Each boundary input needs one independently numbered case')
                key = (check['boundary_group'], links[0]['case_id'])
                if key in boundaries and boundaries[key] != check['input']:
                    raise ValueError('Different boundary inputs cannot share one case')
                boundaries[key] = check['input']
            results.append({'point_id': point['id'], 'check_id': check['id'], 'description': check['description'],
                            'status': status, 'cases': summaries, 'missing': missing,
                            'pending': row.get('pending'), 'decision': copy.deepcopy(decision)})
            statuses.append(status)
        aggregate = statuses[0] if len(set(statuses)) == 1 else 'partial'
        points.append({'point_id': point['id'], 'basis': point['basis'], 'status': aggregate})
    return {'content_version': batch['content_version'], 'nature': 'design_coverage_not_execution',
            'checks': results, 'points': points,
            'ai_suggestions': copy.deepcopy(design['ai_suggestions']),
            'uncovered_combinations': copy.deepcopy(design['uncovered_combinations'])}


def render_extension(batch, case_id=None, *, case_ids=None):  # Preserve existing one-case callers.
    """Regenerate scoped review and coverage from the current clarified batch version."""
    _credential_guard(batch)
    result = _render(batch)
    coverage = _coverage(batch)
    lines = ['# Design coverage (not execution)', 'Version: ' + batch['content_version']]
    for point in coverage['points']:
        lines.append(f"- {point['point_id']}: {point['status']}; basis: {point['basis']}")
    for row in coverage['checks']:
        lines.append(f"- {row['check_id']} {row['description']}: {row['status']}; missing: {', '.join(row['missing'])}; pending: {row['pending'] or 'none'}")
        for case in row['cases']:
            lines.append(f"  - {case['case_id']} ({' / '.join(case['module_path'])}); expected: {'; '.join(case['expected'])}; verification: {'; '.join(case['verification'])}")
        if row['decision']:
            lines.append('  - User disposition: ' + json.dumps(row['decision'], ensure_ascii=False))
    lines.extend(['## AI suggestions (separate from mandatory human baseline)',
                  *['- ' + json.dumps(s, ensure_ascii=False) for s in coverage['ai_suggestions']],
                  '## Uncovered combinations', *['- ' + x for x in coverage['uncovered_combinations']],
                  '## UI gaps and user write/explore decisions',
                  *['- ' + json.dumps(g, ensure_ascii=False) for g in batch['extension_design']['ui_gaps']]])
    result.update(coverage=coverage, coverage_notes='\n'.join(lines) + '\n')
    if case_id is not None and case_ids is not None:  # Avoid two competing selection inputs.
        raise ValueError('Choose one chat selection input')  # Never guess which request wins.
    from presentation import render_chat  # One selection contract for every authoring stage.
    chat = render_chat(batch, [case_id] if case_id is not None else case_ids)  # Validate exact 1–9 scope.
    result.pop('human_view', None)  # Default delivery is the complete scoped XMind copy.
    if 'human_view' in chat:  # Only a real selection exposes chat text.
        result['human_view'] = chat['human_view']  # Same candidate and complete reference context.
    return result


def build_extension(catalog, baseline, reports, entry_request, design, mode='production'):
    """Recheck P0 entry, then build one shared P1/P2 candidate/review batch."""
    _credential_guard(design)
    entry = check_extension(catalog, baseline, reports, entry_request, mode=mode)
    if not entry['can_extend']:
        raise ValueError('P0 entry blocked; resolve report, manual-start or gap decisions first')
    design = copy.deepcopy(design)
    if not design.get('manual_points'):
        raise ValueError('Mandatory human baseline required')
    candidates = design['candidates']
    candidate_ids = {c['id'] for c in candidates}
    for gap in design['ui_gaps']:
        decision = gap.get('decision', {})
        if not gap.get('description') or not gap.get('basis') or not gap.get('recommendation') or not gap.get('case_ids') or not set(gap['case_ids']) <= candidate_ids:
            raise ValueError('Concrete UI gap, affected cases, source and recommendation required')
        if decision.get('route') != 'write_first' or not decision.get('actual_reply', '').strip():
            raise ValueError('User must choose write-first; explore-first waits for supplied exploration')
    for suggestion in design['ai_suggestions']:
        decision = suggestion.get('decision', {})
        if not all(suggestion.get(k) for k in ('id', 'proposal', 'basis', 'risk', 'uncovered_scope')):
            raise ValueError('AI combinations need basis, risk and uncovered scope')
        if decision.get('route') not in ('include', 'defer', 'exclude') or not decision.get('actual_reply', '').strip():
            raise ValueError('Extra combinations require an explicit user choice')
        if decision['route'] == 'include' and (not suggestion.get('case_ids') or not set(suggestion['case_ids']) <= candidate_ids):
            raise ValueError('Included suggestions need independent complete cases')
        if decision['route'] != 'include' and suggestion.get('case_ids'):
            raise ValueError('Unselected suggestions cannot become candidate cases')
    for case in candidates:
        if case.get('priority') not in ('P1', 'P2') or not case.get('priority_basis') or not all(case.get('priority_factors', {}).get(k) for k in ('importance', 'risk', 'frequency')):
            raise ValueError('Priority proposal needs importance, risk and frequency')
        if not all(case.get('context', {}).get(k) for k in ('role', 'initial_state')) or not case.get('data_preparation') or not case.get('steps'):
            raise ValueError('Role, initial state, preparation and operations required')
        for group in GROUPS:
            for step in case.get(group, []):
                if not step.get('operation') or not step.get('expected') or not step.get('verification'):
                    raise ValueError('Independent complete expected and observable verification required')
                if any(not claim.get('text', '').strip() or not claim.get('source')
                       for field in ('expected', 'verification') for claim in step[field]):
                    raise ValueError('Nonempty source-traced business claims required')
        case.update(rule_status='unconfirmed', review_status='pending', merge_status='not_merged', execution_status='not_run')
        for field in ('final_review', 'supplied_content_confirmation', 'rule_decisions'):
            case.pop(field, None)
    selections = design.get('selection') or [{'case_id': c['id'], 'action': 'add', 'reason': 'P1/P2 design expansion'} for c in candidates]
    result = build_scoped_review(catalog, design['batch_id'], selections, candidates=candidates,
                                 candidate_data=design['candidate_data'])
    batch = result['batch']
    data = {d['id']: d for d in batch['data']}
    for item in data.values():
        if not all(item.get(k) for k in ('object_ref', 'validity', 'reuse_policy', 'invalidation_action')):
            raise ValueError('Explicit business data conditions required')
    batch['extension_design'] = {k: v for k, v in design.items() if k not in ('candidates', 'candidate_data')}
    batch['extension_entry'] = entry
    for index, case in enumerate(batch['cases']):
        if case['id'] not in candidate_ids:
            continue
        case['data_version'] = batch['data_version']
        case['semantic_version'] = _digest({k: v for k, v in case.items() if k not in ('semantic_version', 'data_version')})
        batch['questions'].append({'case_id': case['id'], 'field': 'priority',
            'reason': 'Confirm P1/P2 priority proposal using importance, risk and frequency',
            'suggested_target_paths': [['cases', index, 'priority'], ['cases', index, 'priority_basis']]})
    batch['initial_copy_baseline']['cases'] = copy.deepcopy(batch['cases'])
    batch['initial_copy_baseline']['copy_version'] = _digest({
        key: batch['initial_copy_baseline'][key] for key in ('cases', 'data', 'selection')})
    batch['content_version'] = _digest({k: v for k, v in batch.items() if k != 'content_version'})
    rendered = render_extension(batch)
    rendered.update(changes=result['changes'], review_notes=result['review_notes'])
    rendered['review_notes'] += rendered['coverage_notes']
    return rendered


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, help='Envelope: catalog, baseline, reports, entry_request, design')
    parser.add_argument('--mode', choices=['production', 'simulation'], default='production')
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    try:
        envelope = json.loads(Path(args.input).read_text(encoding='utf-8-sig'))
        result = build_extension(**envelope, mode=args.mode)
        output = Path(args.output_dir)
        output.mkdir(parents=True, exist_ok=False)
        for filename, key in [('candidate.json', 'batch'), ('coverage.json', 'coverage'), ('changes.json', 'changes')]:
            (output / filename).write_text(json.dumps(result[key], ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        for filename, key in [('xmind.md', 'xmind_markdown'), ('review-notes.md', 'review_notes')]:
            (output / filename).write_text(result[key], encoding='utf-8')
    except (ValueError, KeyError, TypeError, AttributeError, OSError):
        print('Expansion rejected: inspect P0 gate, human coverage, decisions and business completeness.', file=sys.stderr)
        return 1
    print('P1/P2 scope and design coverage written; pending grill and final review, not executed or merged.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
