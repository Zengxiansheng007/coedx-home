# TCA stage adapter to test-grill-me

This is a steps-only mapping onto existing public entries. It adds no business
state machine, mandatory JSON package, second interview or independently editable
answer source. Load test-grill-me by the host's same-name Skill resolution, never
an installed absolute path or assumed sibling directory depth. If unavailable,
report the missing shared capability and preserve the current task.

## Parent input and return

Before invoking the shared Skill, read the actual candidate, sole Q&A MD and
applicable source/version. Pass task identity, current stage, batch/case scope,
source and draft locations/versions, effective decisions and unresolved impacts,
professional check findings, eligible next phases, existing continuation authority
and TCA as return target. Do not require users to populate technical fields.

The shared Skill owns the dialogue and coverage interaction in its own SKILL.md.
It returns actual answers/provenance, summary confirmation, unresolved matters,
coverage dispositions, actual artifact locations and next-step recommendation.
TCA checks that return against its sources and performs the authorized authoring.
A shared return is not a professional qualification or a new approval receipt.

| Entry | TCA checks before shared questioning | Existing persisted/public entry after return |
| --- | --- | --- |
| Recording / complete handwritten P0 | Read source text, privacy, whole input, complete operation/data/expectation and provenance; never execute recording | authoring.build_batch; start_record on the task MD; clarification field mapping |
| Batch rules / coverage | Read source semantics and coverage-review; enrich only unresolved business rules and field targets | append_questions, respond, record_coverage, summarize; then separately authorized apply_summary |
| Report reconciliation / missing P0 | Read reports and attachments before questions; check current versions and complete approved P0 scope, propose omissions for actual disposition | reconcile_reports and check_extension; report facts via record_context and actual choices via record_note |
| P1/P2 start / priority / extra combinations | Explicit user start AND complete P0 qualification; separate provisional continuation; human checks and explicit include/defer/exclude | start_extension rechecks build_extension and check_extension; questions use the same task MD |
| Chat / Markdown / native XMind feedback | Read actual return and initial/latest candidate; preserve scope exclusions and undisplayed cases; local change defaults to current P1/P2 | start_feedback, respond, summarize, then authorized apply_feedback and exact-version review_feedback |
| Product conclusion / dependency change | Read original provisional meaning and evidence applicability; keep history; identify only affected rules/cases | product reconciliation and existing feedback entries; no automatic retest or merge |
| Draft ready / reviewed scope | Save and reread actual artifact; present version, case scope, changes and remaining blockers | direct review/review_feedback; recommend next phase and wait unless expressly authorized |

Use the linked professional references from SKILL.md for field schemas and checks.
Manual report selection, deferred scope and shared stage choice never replace
missing P0 evidence. Scope copies retain complete selected cases and are not full
catalog replacements; omission from display is never deletion.

## Confirmation mapping in the sole MD

- Rule answer: respond records formal/provisional/deferred with source and actual
  words. It does not approve a summary, draft, merge or execution.
- Summary-only confirmation: record_note with actual_reply, source_ref,
  confirmation_kind: summary, summary_id, content_version and case_ids. Retain
  the actual confirmed summary in the existing summarize event. Recommend the
  next phase's purpose and inputs, then wait; do not call apply_summary yet.
- Confirmation plus continuation: record the confirmation and a separate
  record_note with intent: continue and exact next phase/scope/version. A single
  utterance may supply both, but only if it explicitly means both. Valid prior
  continuation authority may be reused. Then apply_summary/apply_feedback uses
  the actual agreement and current summary id. These entries update candidate
  content, so they must not be used merely to save a confirm-only reply.
- Continuation later: read_notes and read_record, match the saved confirmation to
  the current summary id/version/scope, record the new continuation words and
  apply once. A stale confirmation cannot authorize changed content.
- Draft approval: review/review_feedback binds actual_reply, content_version and
  case_ids. It records approval of displayed complete cases only. Save/read back
  and reuse matching approval. Never require confirmation that a draft exists.
- Merge/execution request: record_actions records actual independent intent; it
  does not perform either action. P1/P2 still requires its explicit manual_start
  and current full P0 check; merely saying continue after P0 review is insufficient
  if the intended phase is ambiguous.

The extra record_note keys are contextual evidence, not a new executable gate.
The agent must interpret actual intent and verify applicability; public API tests
cannot prove that interpretation. User-facing delivery includes actual scope,
artifact or existing Q&A section, version, change, unresolved impact and the
specific object being confirmed. Never invent a stage report for an internal check.

## Validation boundary

Use public qa_record entries to verify confirm-only notes leave the candidate
unchanged, explicit application produces pending-review content, and review never
sets merge/execution success. Exercise complete P0 evidence and manual-start
failures through check_extension. Run separately observed dialogue to test intent
interpretation and routing; scripted replies are synthetic, not business approval.
Range cleanup and recovery follow the existing qa-record contract and their own
change scope, not a new mechanism in this adapter.
