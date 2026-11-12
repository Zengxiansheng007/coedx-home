"""Resolve typed case references without rewriting business literals."""
def case_name(batch, identity):
    cases = {c['id']: c for c in (batch.get('initial_copy_baseline') or {}).get('cases', [])}  # Include prior reference names.
    cases.update({c['id']: c for c in batch['cases']})  # Current title wins after rename.
    return cases.get(identity, {}).get('title', '关联用例（名称待核对）')  # Unknown references need clarification.


def render_chat(batch, case_ids=None):
    """Project only an explicitly requested 1–9 complete cases, without writes."""
    from authoring import _credential_guard  # Same privacy boundary as other views.
    from scoped_review import _render  # Reuse complete business groups and data rules.
    _credential_guard(batch)  # Protect returned text too.
    result = {'content_version': batch['content_version'], 'case_ids': []}  # Bind the actual source version.
    if case_ids is None:  # Batch delivery remains XMind by default.
        return result  # Never infer a request to display all cases.
    if not isinstance(case_ids, (list, tuple)) or not 1 <= len(case_ids) <= 9:  # Bound the actual selection.
        raise ValueError('Request 1–9 distinct cases for chat')  # No truncation or automatic paging.
    if any(not isinstance(cid, str) for cid in case_ids) or len(set(case_ids)) != len(case_ids):  # Reject ambiguous requests.
        raise ValueError('Request distinct stable case identities')  # Business identity resolution happens before this seam.
    cases = {case['id']: case for case in batch['cases']}  # Keep the complete source for references.
    if any(cid not in cases for cid in case_ids):  # Reject stale or unknown selection.
        raise ValueError('Unknown case requested for chat')  # Never silently skip requested content.
    selection = {row['case_id']: row for row in batch['selection']}  # Preserve original selection reasons.
    views = []  # Only requested cases enter the returned text.
    for cid in case_ids:  # Preserve the user's requested order.
        note = dict(selection.get(cid, {'case_id': cid, 'reason': '候选评审'}))  # Support authoring and scoped batches.
        note.setdefault('action', 'add')  # Authoring selection omits the maintenance action.
        single = dict(batch, cases=[cases[cid]], selection=[note])  # Shallow projection; renderer never mutates it.
        views.append(_render(single, reference_batch=batch)['human_view'])  # Full source resolves outside references.
    result.update(case_ids=list(case_ids), human_view='\n'.join(views))  # Text is for the conversation only.
    return result  # No human-view file or secondary business source.
