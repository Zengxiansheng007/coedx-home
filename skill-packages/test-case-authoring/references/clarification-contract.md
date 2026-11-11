# Public batch clarification contract

For actual conversations, use [the single Markdown adapter](qa-record-contract.md)
to save questions before sending and actual replies before dependent judgments.
The pure functions below are computation seams; their returned session is a
derived projection, never a second independently editable business answer source.

`scripts/clarification.py` provides pure Python entry points. They accept and
return JSON-compatible batch/session objects without files, network, browser,
execution or merge side effects. Use `scripts/authoring.py` for initial recording
or handwritten conversion. A batch may contain several complete candidate cases with stable
identities. Use `authoring.render_batch(batch)` for matching multi-case views.

```python
from clarification import start_grill, respond, summarize, apply_summary, review, record_actions
session = start_grill(batch, enriched_questions)
# Show session['chat'] in conversation; it contains the whole eligible round.
session = respond(session, replies)  # only actual answers; repeat for later rounds
# Live conversations must actually reread sources/history/dependencies and persist
# record_coverage through qa_record before summarize; see coverage-review.md.
session = summarize(session)       # show session['summary'] to the user
session = apply_summary(session, confirmation)
session = review(session, final_review)
session = record_actions(session, explicit_actions)  # only when actually requested
```

Every question preserves the original `field`, `reason`, `case_id` and evidence,
and adds `id`, `depends_on` (question IDs), `options` (at least two),
`recommendation`, `rationale`, `example`, `affected_checks`, and `target_paths`.
Every converter doubt must be represented. Several questions can address one
field. Optional `rule_id` identifies the same business rule across questions or
feedback rounds and is retained in summary decisions. Distinct question IDs
without a rule_id are independent rules even on the same field. Reuse the same
question ID, or explicitly bind the same rule_id, only when the actual user
answer revises that same rule. A field path locates content, not rule identity.
Cyclic/unknown dependencies are rejected. The agent must check semantic
dependencies; the helper only enforces the declared graph.

For unregistered source findings use `append_questions(session, questions)`;
old answers remain intact and new IDs must be unused. For each actual source
review use `record_coverage(session, observation)` as described in
[coverage review](coverage-review.md). These pure seams are also available as
same-name actions in the sole MD adapter. A later reply or discovery invalidates
the recorded review revision; unresolved source branches block its summary.

A reply has `question_id`, `decision` (`formal`, `provisional`, `deferred`),
`actual_reply`, and `updates`. Provisional replies also require `product_check`.
For compound questions declare `answer_parts` as stable aspect names mapped to
concrete descriptions (object, condition, behavior, subdivided when necessary).
Replies supply only actual `answered_parts`; `partial` and `unknown` preserve
incomplete replies without business authorization or candidate updates. The
returned `remaining_parts` and Chinese chat ask the remaining question; unknown
returns a full disposition question. Formal/provisional require all declared
aspects; explicit deferred may leave them unknown. Summary carries accumulated
aspects while all original replies and their source references remain in history.
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
Complete catalog module paths of at least five levels retain every level through
summary application. The recording/handwritten converter retains its separate
five-level input contract. Rule status aggregates `active_rule_decisions` by
stable rule ID (otherwise question ID): unrelated provisional product conditions or deferred rules survive
new formal answers. Historical decisions remain recorded separately; current
views and report checks use the active conditions. Only explicit same-identity
clarification supersedes its earlier answer. Legacy decisions without either
identity remain distinct and conservative even when their fields match.

For a complete supplied case with no doubts, include its existing business rules
in the summary and obtain explicit current-content understanding agreement.
`apply_summary` retains that actual agreement as `supplied_content_confirmation`
and sets rule status to formal. Conversion alone stays unconfirmed. No redundant
field questions or invented answer records are required; final review remains a
separate explicit current-version action.

Final review has `approved: true`, exact `content_version`, nonempty `case_ids`,
and `actual_reply`. It requires the current confirmed/applied summary and refuses
deferred/unconfirmed cases. It never creates execution or merge instructions.
It returns updated views and a stage-specific recommendation: P0 recommends
separately user-started ui-test validation; P1/P2 recommends user-started authoring
merge of the reviewed scope, followed by separately user-started ui-test after
merge. Neither recommendation applies a merge or executes cases. Explicit actions have
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

## Review repair boundary

Scope-only independent impacts use disposition_scope=separate_impact plus scope_basis and empty target_paths. Show the scope distinction before asking; preserve actual deferred/unknown decisions. The default case_rule (including an empty target_paths list) and its dependency closure still block. See coverage-review.md for source classification; never relabel a necessary unknown rule to bypass a blocker.
