# Review continuity and targeted reopen

Read before routing any work after a review has closed, including format conversions,
new versions, new conversations, failed validation, and downstream plan generation.

## Authority and independent statuses

Verify the actual ledger's closureEvidence, phase/result and effective decisions before
interpreting a document's display status. Preserve four separate facts: review closure,
artifact consistency/approval, technical qualification, and execution authorization.
An unverified runtime, missing installation approval, or a newly generated document is
not evidence that settled requirements became undecided. Never manufacture artifact
approval or implementation readiness merely because the review closed.

If a new document mistakenly says requirements-review while requirements are unchanged,
classify it as a document/governance defect. Repair the owner artifact, navigation,
hash-bound anchor and checks within current user authority; do not ask settled questions
again. Historical ledger/receipt/report evidence remains immutable.

## Reopen eligibility

Only these evidence-backed triggers may reopen affected questions:

- substantive-requirement-change: changed goals, scope, behavior, permissions, states,
  interfaces, acceptance obligations or quality guarantees;
- evidenced-conflict: current authoritative sources or implementation facts contradict
  a confirmed decision within its applicable scope;
- new-major-risk: newly evidenced safety, security, data-integrity or other high-impact
  risk invalidates a previous assumption or requires a changed decision.

Not triggers on their own: Markdown/JSON conversion, wording without meaning change,
headings, layout, links, display numbering, metadata repair, a version/hash change,
new task/conversation, plan drafting, an ordinary test failure, or pending technical
qualification already recorded at closure. Formatting that actually changes permission
or meaning is substantive, regardless of its label.

Unknown impact is not format-only and is not proof of a whole-review failure. Inspect
the changed content and its linked evidence; block only dependent work pending
classification, continuing unaffected authorized work. Do not silently label drift
non-semantic to bypass a gate.

## Required impact record and local review

Before calling reopen, record the trigger, old/new evidence references, changed
requirement/decision IDs, affected question IDs, impacted artifacts/RTM/tests,
unaffected decisions, reason, owner and classification evidence. New major risks with
no matching old question get a new scoped question linked to the old baseline; do not
reopen an unrelated question merely to obtain an ID.

Use the existing single-question reopen operation only on those IDs. Preserve prior
answers, decision history, closure evidence and receipts. The new closure question
names the scoped change-review, not all historical requirements. Do not reuse a
consumed writeback batch. Fresh user authority for formatting or downstream drafting
may support a new bounded batch without repeating the closed Grill.

Whole-review reopening is exceptional: establish a documented cross-cutting impact
that invalidates all relevant decisions and obtain explicit user agreement to that
expanded review scope. Never infer it from an unclassified issue or a new version.

## Format-only reconciliation and handoff

For an applicable ledger with observed protected-file drift, use the existing
reconcile-format-only operation with reviewer evidence to update the verified baseline
without reopening questions. It does not authorize file edits or infer semantic
equivalence. New formats/paths require updated source/anchor hashes and link/ID/RTM
checks under the actual current writing authorization.

Report review closure, document-validation outcome, pending technical gates, and
execution authority separately. A validation failure routes to the responsible owner
for repair; reopen a requirement only when its evidence satisfies an eligible trigger.
The next architecture/development/test design may have its own review status without
resetting the upstream requirement review.

## Deterministic coverage and limits

The fixture assets/fixtures/review-continuity.json states routing expectations.
scripts/test_review_continuity.py checks required policy content and existing runtime
invariants for formatting and targeted reopening. It does not automate truth or impact
classification. The caller must supply honest evidence; unrestricted legacy reopen
reason strings are not a new semantic enforcement boundary.
