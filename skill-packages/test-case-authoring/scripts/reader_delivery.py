"""Versioned Agent entry for one materialized review scope."""
import json


def case_references(case):
    from scoped_review import GROUPS, _references

    return dict(steps={group: [step.get('id') for step in case[group]]
                       for group in GROUPS if case.get(group)},
                data_refs=sorted(_references(case)))


def write_agent_index(output, batch, case_ids, stage, source_catalog, blockers):
    selected = {case['id']: case for case in batch['cases']}
    index = dict(format='tca.agent-review.v1', stage=stage, content_version=batch['content_version'],
                 candidate='candidate.json', case_ids=case_ids, cases={},
                 blockers=[b for b in blockers if b.get('case_id') in case_ids])
    for cid in case_ids:
        index['cases'][cid] = case_references(selected[cid])
    artifacts = [('agent.json', index)]
    if source_catalog is not None:
        index['source_catalog'] = 'source-catalog.json'
        index['source_catalog_version'] = source_catalog['content_version']
        artifacts.insert(0, ('source-catalog.json', source_catalog))
    for filename, value in artifacts:
        path = output / filename
        temporary = path.with_suffix('.tmp')
        temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        temporary.replace(path)
