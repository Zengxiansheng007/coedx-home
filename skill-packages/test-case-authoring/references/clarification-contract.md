# Public batch clarification contract

`scripts/clarification.py` provides pure Python entry points. They accept and
return JSON-compatible batch/session objects without files, network, browser,
execution or merge side effects. Use `scripts/authoring.py` for initial recording
conversion. A batch may contain several complete candidate cases with stable
identities. Use `authoring.render_batch(batch)` for matching multi-case views.

```python
from clarification import start_grill, respond, summarize, apply_summary, review, record_actions
session = start_grill(batch, enriched_questions)
# Show session['chat'] in conversation; it contains the whole eligible round.
session = respond(session, replies)  # only actual answers; repeat for later rounds
session = summarize(session)       # show session['summary'] to the user
session = apply_summary(session, confirmation)
session = review(session, final_review)
session = record_actions(session, explicit_actions)  # only when actually requested
```

Every question preserves the original `field`, `reason`, `case_id` and evidence,
and adds `id`, `depends_on` (question IDs), `options` (at least two),
`recommendation`, `rationale`, `example`, `affected_checks`, and `target_paths`.
Every converter doubt must be represented. Several questions can address one
field. Cyclic/unknown dependencies are rejected. The agent must check semantic
dependencies; the helper only enforces the declared graph.

A reply has `question_id`, `decision` (`formal`, `provisional`, `deferred`),
`actual_reply`, and `updates`. Provisional replies also require `product_check`.
An update is `{"path":["cases",0,"title"],"value":"Reviewed business title"}`.
Paths must have been declared in the question's `target_paths`. Business fields
can be nested case content or separate data (context, operations, expectations,
verification, data policy, priority basis and other actual affected fields).
Use array indexes from this frozen batch, checking case/data identities before
mapping chat text. Identity, workflow state and version fields are protected.
New dictionary fields may be added; parent containers must exist. Replace an
array as a whole when adding/removing members; preserve stable step identities.
Claims retain provenance, using `source: user_decision` for a confirmed rule;
observation history remains in question evidence. Data values remain in `data`,
and steps use `data_refs`. Credential values are forbidden even in replies.

Only explicit answers are recorded. Correcting an answer appends history and
invalidates dependent answers, which must be asked again. A round stays open
until its presented unanswered questions are resolved. Deferred ancestors block
their dependent questions; the summary names blocked questions and case scope.
Other cases remain eligible. Deferred case updates are held back. No partial
reply changes candidate content or its views.

`summarize` rejects outstanding required questions. Its `summary` contains an
`id`, original content version, answer revision, actual decisions, proposed
updates, product conditions and blocked cases/questions. Confirmation has
`confirmed: true`, that `summary_id`, and the actual agreement in `actual_reply`.
Only `apply_summary` changes candidates, atomically, validates business content,
updates data/semantic/content versions and returns `human_view` and
`xmind_markdown`. Conflicting writes to one path require another clarification.
Final reviews of changed content are retained in `review_history` and become
pending. Questions retain all histories. Explicit unchanged answers can be
reused by starting with the same question descriptions/history from the batch;
changed question descriptions need a new answer. Review status changes alone
do not change the content version.

Final review has `approved: true`, exact `content_version`, nonempty `case_ids`,
and `actual_reply`. It requires the current confirmed/applied summary and refuses
deferred/unconfirmed cases. It never creates execution or merge instructions.
It returns the ui-test recommendation and updated views. Explicit actions have
`kind: execution_start` or `merge_instruction`, current `content_version`,
`case_ids`, `actual_reply`. `record_actions` records these requests only; even a
P0 merge request keeps the case `not_merged` / `not_run`. The receiving ui-test
must independently enforce verification and formal merge conditions. One clear
user message can supply several records; repeated identical actions are reused.

The helper validates deterministic structure and scope, not whether the agent
understood a user sentence. Evaluate that through the actual SKILL.md workflow
with clearly simulated source material and natural-language user replies.
Neither structural checks nor these simulations prove XMind desktop acceptance
or cross-skill production integration.
