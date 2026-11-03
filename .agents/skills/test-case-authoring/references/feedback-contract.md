# Chat and returned hierarchy Markdown feedback v1

Read when existing scoped-review content receives chat or edited Markdown.
Use `scripts/feedback.py` public Python API. The input is the current
`scoped_review_copy` batch from [scoped review](scoped-review-contract.md), with
its unchanged `initial_copy_baseline`. Full source and formal assets stay read-only.
`baseline.cases/data` are the FIRST DISPLAYED candidates, possibly already revised
from the catalog. `catalog_cases/catalog_data` remain the old selected catalog
records; they must never replace the displayed diff baseline.

```python
from feedback import prepare_feedback, apply_feedback, review_feedback
from clarification import respond, summarize

# Chat interpretation; actual_reply contains the actual user words.
pending = prepare_feedback(batch, 'chat', actual_reply=reply, changes=[
    {'collection': 'cases', 'id': 'EXAMPLE-1',
     'path': ['steps', 0, 'expected', 0, 'text'], 'value': 'Revised business result'}])
# Or read the actual file; do not overwrite it with regenerated content first.
pending = prepare_feedback(batch, 'markdown', actual_reply=file_reply,
                           markdown=returned_file.read_text(encoding='utf-8-sig'))
# Ask all independent questions from pending['grill']['chat'] in chat prose.
pending['grill'] = respond(pending['grill'], replies)
pending['grill'] = summarize(pending['grill'])
# Show its summary PLUS pending changes/deletions, affected cases and coverage.
result = apply_feedback(pending, agreement)
# Later, a separate final approval of full cases at result['batch']['content_version']:
result = review_feedback(result, final_approval)
```

The two `prepare_feedback` calls above are alternatives. Replies, agreement
and final approval follow the [clarification contract](clarification-contract.md).
Agreement binds the current `summary_id`, `confirmed: true`, actual reply;
final approval binds `content_version`, `case_ids`, `approved: true`, actual reply.
Synthetic evaluations label all replies SIMULATED. No external model is needed.

Chat changes identify `collection: cases|data`, stable `id`, and a leaf `path`
within that record. Existing nonempty business string leaves are supported.
Identity, module paths, reference lists, credentials and workflow fields cannot
be patched as business answers. Structural edits require a fresh scoped candidate
or explicit interpretation at the existing authoring boundary, retaining history.

Returned Markdown is the generated `xmind_markdown` hierarchy from the INITIAL
scope copy, not arbitrary Markdown or native XMind. Edit business scalar leaves
(title, operations, expected and verification text, context or data) while retaining
labels, hierarchy, order, header/version, IDs and row counts. Whole-case removals
include their full module subtree. Repeated projections of one data leaf must
agree. Unsupported structural edits fail closed and return to chat clarification.
Markup entities use the renderer's escaping. Native XMind parsing remains separate.

Each returned change is compared three ways: first displayed value, latest
accepted candidate value, proposed value. Unchanged first-display fields preserve
later accepted edits. Already applied changes are no-ops; conflicts require
clarification rather than reversion. Both views come from the latest candidate.

Chat can supply `removed_case_ids` and `deletion_decisions`, mapping each missing
ID to `{action: exclude|deactivate|restore, actual_reply: ...}`. Only IDs in the
initial display are eligible; absent unshown IDs never become deletion proposals.
Clear decisions are reused from the batch. Ambiguous deletion uses the existing
grill, with three options; record `deletion_action` in its actual answer. Summary
agreement then applies that answer. Do not supply an unagreed action only at apply.
Excluded cases stay recorded as `feedback_disposition: excluded_this_round` and
are absent from the regenerated review view. Deactivation retains complete content
and history with `maintenance_action: deactivate`; restore retains the current
accepted content. None of these actions deletes full catalog content.

Changes remain proposals during grill. `apply_feedback` applies one agreed
summary, saves feedback history, preserves the initial baseline, updates common
data and affected case versions, archives prior final approvals and marks affected
cases pending review. Provisional answers retain their product-check condition
in feedback rule history. Deferred cases remain unapplied. An affected existing
case's agreed decisions set its rule state just as in batch clarification:
deferred scope stays deferred, otherwise any provisional answer keeps provisional
state and its product-check condition, otherwise explicit formal decisions set
formal state (including previously unconfirmed or provisional candidates).
Recording an answer alone changes no candidate state; exact-summary agreement
and application are required. Existing decisions and conditions remain history.
An affected existing
coverage mapping uses `{check_id, case_ids, expected_summary,
verification_summary, status}`; associations are retained, summaries regenerated
from complete linked cases, data references refreshed and status set to
`pending_review` with its old record in history. This describes design coverage,
never execution success or full manual-point coverage.

Results contain `batch`, both views, actual `changes`, `review_notes` and a
`review_session` for the existing final-review gate. Write these only to a NEW
authorized candidate directory. Candidate content is the common semantic source;
formal derived files are not an update target. Review/merge/execution remain
distinct. Formal ui-test readers, synchronization and business execution await
their separate integration and approval.
