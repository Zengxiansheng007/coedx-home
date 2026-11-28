"""Bind source-assessed consecutive P0 operations for XMind projection only."""
import argparse
import copy
import json
from pathlib import Path

from authoring import _cell, _credential_guard, _digest


CHECK = '复用范围待核对：请核对原始材料，本例保留完整步骤'


def signature(case, data):
    refs = {ref for step in case['steps'] for ref in step.get('data_refs', [])}
    values = [item for item in data if item['id'] in refs]
    if len(values) != len(refs) or {item['id'] for item in values} != refs:
        raise ValueError(CHECK)
    return _digest([case['id'], case['priority'], case['title'], case['context'], case['steps'],
                    sorted(values, key=lambda item: item['id'])])


def checked_range(row, case, source):
    start, target, length = (row[key] for key in ('source_start', 'target_start', 'length'))
    if any(type(n) != int or n < 1 for n in (start, target, length)):
        raise ValueError(CHECK)
    if start + length - 1 > len(source['steps']) or target + length - 1 > len(case['steps']):
        raise ValueError(CHECK)
    if 'branch_step' in row:
        branch = row['branch_step']
        if type(branch) is not int or not target + length <= branch <= len(case['steps']):
            raise ValueError('共同段须在本例首个分叉步骤之前结束：' + CHECK)
    if not all(isinstance(row.get(k), str) and row[k].strip() for k in ('test_point', 'criterion', 'source_basis')):
        raise ValueError(CHECK)
    if not isinstance(row['changes'], list) or any(type(c.get('step')) != int or
            not target <= c['step'] < target + length or not isinstance(c.get('text'), str) or
            not c['text'].strip() for c in row['changes']):
        raise ValueError(CHECK)


def bind_case(case, assessment, catalog, data):
    row = copy.deepcopy(assessment)
    matches = [s for s in catalog['cases'] if s['id'] == row['p0_case_id']]
    if len(matches) != 1 or matches[0]['priority'] != 'P0' or case['priority'] not in ('P1', 'P2'):
        raise ValueError(CHECK)
    source = matches[0]
    checked_range(row, case, source)
    row['binding'] = dict(source_digest=signature(source, catalog['data']), target_digest=signature(case, data),
                          title=source['title'], review_status=source['review_status'],
                          catalog_version=catalog.get('content_version'))
    case['review_segment'] = row


def bind_segments(batch, assessments, source_catalog=None):
    """Return an independently versioned copy of a complete authored batch."""
    result = copy.deepcopy(batch)
    _credential_guard(assessments)
    indexed = {case['id']: case for case in result['cases']}
    if len(indexed) != len(result['cases']) or assessments.keys() - indexed.keys():
        raise ValueError(CHECK)
    for identity, assessment in assessments.items():
        case = indexed[identity]
        bind_case(case, assessment, source_catalog or result, result['data'])
        case['semantic_version'] = _digest({k: v for k, v in case.items() if k not in ('semantic_version', 'data_version')})
    result['content_version'] = _digest({k: v for k, v in result.items() if k != 'content_version'})
    return result


def project_segment(batch, case, node, source_catalog):
    row = case.get('review_segment')
    if not row:
        return
    def leaf(text):
        return dict(text=_cell(text), children=[], origins=[])
    try:
        binding = row['binding']
        catalog = source_catalog or batch
        matches = [s for s in catalog['cases'] if s['id'] == row['p0_case_id']]
        baseline = batch.get('initial_copy_baseline') or {}
        if matches or source_catalog is not None or row['p0_case_id'] not in baseline.get('not_displayed_case_ids', []):
            if len(matches) != 1 or signature(matches[0], catalog['data']) != binding['source_digest']:
                raise ValueError(CHECK)
            source = matches[0]
            checked_range(row, case, source)
            status = source['review_status']
        else:
            status = binding['review_status']
        if source_catalog is not None and baseline and baseline['catalog_version'] != source_catalog['content_version']:
            raise ValueError(CHECK)
        if baseline and binding['catalog_version'] != baseline['catalog_version'] and not matches:
            raise ValueError(CHECK)
        if signature(case, batch['data']) != binding['target_digest']:
            raise ValueError(CHECK)
        steps = next(child for child in node['children'] if child['text'] == '测试步骤')
        first, length = row['source_start'], row['length']
        status = {'pending': '待评审', 'approved': '已评审'}.get(status, status)
        lines = [leaf(f'复用：P0「{binding["title"]}」（{status}）第 {first}～{first+length-1} 步的操作顺序')]
        lines.extend(leaf(f'变化：第 {c["step"]} 步，{c["text"]}') for c in row['changes'])
        lines.append(leaf('判定：' + row['criterion']))
        pos = row['target_start'] - 1
        for number, child in enumerate(steps['children'], 1):
            child['target_step_number'] = number
        steps['children'][pos:pos+length] = lines
        node['children'].insert(0, dict(leaf('测试点：' + row['test_point']), segment_test_point=True))
    except (KeyError, ValueError, TypeError, StopIteration):
        node['children'].insert(0, leaf(CHECK))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ('candidate', 'assessments', 'output-dir'):
        parser.add_argument('--' + option, type=Path, required=True)
    args = parser.parse_args()
    from source_preparation import render_selection
    from module_handoff import write_artifacts
    def read(path):
        return json.loads(path.read_text(encoding='utf-8-sig'))
    batch = bind_segments(read(args.candidate), read(args.assessments))
    result = render_selection(batch)
    args.output_dir.mkdir(parents=True, exist_ok=False)
    write_artifacts(result, args.output_dir, review_ids=[case['id'] for case in batch['cases']])


if __name__ == '__main__':
    main()
