"""Resolve typed case references without rewriting business literals."""
def case_name(batch, identity):
    cases = {c['id']: c for c in (batch.get('initial_copy_baseline') or {}).get('cases', [])}  # Include prior reference names.
    cases.update({c['id']: c for c in batch['cases']})  # Current title wins after rename.
    return cases.get(identity, {}).get('title', '关联用例（名称待核对）')  # Unknown references need clarification.
