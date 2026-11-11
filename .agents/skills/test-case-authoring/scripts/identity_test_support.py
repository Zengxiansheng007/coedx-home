"""Explicit synthetic test binding; never used by production identity matching."""
from aggregation import feedback_topics


def bound_cases(batch, markdown, titles=None):
    topics = feedback_topics(markdown)  # Test fixtures explicitly know each intended edited case.
    result = {}
    for case in batch['cases']:
        title = (titles or {}).get(case['id'], case['title'])
        nodes = [n for n in topics if n['path'] == case['module_path'] and n['title'] == title]
        if len(nodes) == 1:
            result[case['id']] = dict(nodes[0], source_version=markdown.splitlines()[1][len('- 版本：'):], actual_reply='SIMULATED: explicitly bind this fixture case and its full business path')
    return result
