# Chat and returned hierarchy Markdown feedback v1

Read when existing scoped-review content receives chat or edited Markdown.
For live conversations use `qa_record.advance_record` on the existing task MD;
`scripts/feedback.py` remains the pure computation and regression interface. The input is the current
`scoped_review_copy` batch from [scoped review](scoped-review-contract.md), with
its unchanged `initial_copy_baseline`. Full source and formal assets stay read-only.
`baseline.cases/data` are the FIRST DISPLAYED candidates, possibly already revised
from the catalog. `catalog_cases/catalog_data` remain the old selected catalog
records; they must never replace the displayed diff baseline.

## Same-task review chapter

Read the existing MD and current candidate before interpreting feedback. Save
`advance_record(path, 'start_feedback', payload)` before presenting anything.
The payload includes `channel`, actual user `actual_reply`, `source_ref`, and
the supported `prepare_feedback` arguments below. Clear textual changes use
`clear_changes=True`; they are proposals for the existing summary confirmation,
not newly approved cases and not a separate rule-approval questionnaire.

Ambiguous or partial changes use `questions` with stable IDs, full Chinese
question/options/recommendation/reason/boundary/example/evidence, `answer_parts`
for object/condition/behavior gaps, and explicit `depends_on`. Include existing
questions unchanged; add only the relevant new questions. Candidate answer
`target_paths` must belong to that question's case; shared-data edits use explicit
`changes`, which account for all selected consumers. New scope stays a suggestion.

For a changed old condition, pass `reopen_question_ids` naming those premises.
The adapter reopens only them and their declared dependencies; old actual words,
answer versions, approvals and provisional product checks remain in the record.
Use ordinary persisted `respond` for actual later answers and partial corrections.
An unchanged decision is reused, and an unanswered aspect remains a question.
If the user changes the proposed textual edit itself during clarification, finish
recording that feedback as a note and reconcile the pending proposal explicitly;
never mutate the returned projection or silently overwrite the proposal on disk.

After all relevant replies, call persisted `summarize`; display its decisions,
the pending before/current/proposed values, conditions and affected scope. Only
the actual summary agreement goes to `apply_feedback`. Then render and present
the complete revised affected cases and use `review_feedback` for their distinct
current-version approval. Pending feedback rejects ordinary `apply_summary` or
`review` as a shortcut. No step starts execution or merges the catalog.

Both newly shown questions and actual replies are saved/read back in the same
MD. The technical `feedback_pending`/`feedback_result` values are replayed
projections, not independently editable business answer files. Existing pure API
examples below illustrate computations; live answers must take this persisted path.

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

Returned Markdown is the generated `xmind_markdown` hierarchy from the initial
scope copy or a current same-version review display, not arbitrary Markdown or native XMind. Edit business scalar leaves
(title, operations, expected and verification text, context or data) while retaining
labels, hierarchy, order, header/version, IDs and row counts. Whole-case removals
include their full module subtree. Repeated projections of one data leaf must
agree. Unsupported structural edits fail closed and return to chat clarification.
Markup entities use the renderer's escaping. For native returns use
[the XMind adapter](xmind-feedback-contract.md), which reads the file before
entering this same feedback workflow.

Each returned change is compared three ways: first displayed value, latest
accepted candidate value, proposed value. Unchanged first-display fields preserve
later accepted edits. Already applied changes are no-ops; conflicts require
clarification rather than reversion. Both views come from the latest candidate.
Current-version Markdown binds its edits to the current candidate, allowing a
second edit of an accepted field to enter grill. For an explicit chat revision
of an already accepted field, pass `source_version=batch['content_version']`
and `before` with the current field value in each change. The skill obtains
these from the current display and the user's explicit correction. Stale version,
mismatched `before`, unbound overwrites and unknown structure remain rejected.
Initial values and earlier accepted proposals remain in their existing history;
the revised field still needs summary agreement and a new final review.
Final review may add workflow prose without changing the semantic version. A
pre-approval displayed file remains eligible: the reader ignores only exact
trusted same-version final-review/history prose and normalizes its pending versus
approved display status. It never imports those fields as decisions. Altered or
unknown metadata, business structure and conflicting semantics remain rejected;
the immutable initial baseline and current accepted decisions stay authoritative.

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
in feedback rule history. Deferred cases remain unapplied. Shared clarification
and feedback maintain `active_rule_decisions` separately from historical answers.
The latest agreed answer for the same stable rule_id (otherwise question_id)
supersedes only that identity's active predecessor. Distinct identities on the
same field remain independent. A chat change may explicitly include `rule_id`
when the actual reply resolves that identified rule; field equality alone never
establishes supersession. Decisions without identities are preserved individually
and conservatively. Any active deferred rule blocks the case;
otherwise any active provisional rule keeps it provisional. Only with all active
conditions resolved can it become formal. An unscoped legacy condition remains
pending clarification rather than being cleared by an unrelated field answer.
Explicit product-change reconciliation resolves the identified product rule in
that proposal only, preserving unrelated rules and historical conditions.
Generated feedback question IDs bind the initial source scope and full proposal,
not a per-session counter. Automatically enriched existing doubts bind their
original source/question fingerprint, retained as `feedback_origin` for repeat
rounds. Distinct source doubts at the same list position remain independent.
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
