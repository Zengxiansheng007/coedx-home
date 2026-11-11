# CR-20261111-109 - Feedback returns to the same clarification record

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | core-skill-md / references-and-assets / scripts-and-validation |
| Source | Issue 109; confirmed questioning requirements REQ-003/004/006 |
| Baseline | ef5d4b457e6fd24e480b7f348da97a16d1fe25a0 |
| Author | Codex |
| Related Records | CR-20261111-105, CR-20261111-106 |

## Summary

Record review proposals and focused follow-up in the same task Markdown, then use existing summary application and complete-case review.

## Context And Problem

Feedback had a pure API but no persisted review-stage transition. Clear changes generated redundant rule questions, while rebuilt questions lost the original dependency graph.

## Sections Changed

SKILL.md feedback entry; references/feedback-contract.md; scripts/feedback_record.py adapter; qa_record.py allowlist and replay; feedback.py focused questions and centralized answer updates; clarification.py exact proposal summary binding; test_feedback_record.py public behavior regressions. Source and distribution mirror are identical.

## Decision And Alternatives

Reuse existing feedback application and review, issue 106 partial answers and stable dependencies, and the existing Markdown event store. Do not add another approval or recovery engine. The agent interprets actual words and identifies affected rules; deterministic checks do not claim natural-language understanding.

## Detailed Change

Clear changes remain recorded proposals until summary agreement. Ambiguous questions carry full presentation and named answer aspects. Changed premises reopen only their graph descendants, preserving old answer histories and provisional conditions. Applying the exact summary archives affected old approvals and requires complete updated cases to be reviewed separately. Unrelated old answer updates are not reapplied.

## Impact Analysis

Pure API callers retain default behavior. Live feedback uses the sole task record. Proposed shared-data edits retain consumer tracking; answer updates stay within their declared case. Native adapters remain responsible for actual file intake. No formal catalog mutation, execution, installation or external publication is added.

## Validation Evidence

Two public-interface red-green slices: unknown start_feedback action, then missing targeted reopen support. Workspace temporary directories avoid the documented Windows sandbox system-TEMP replacement failure. Full regression and structure-validator outputs are retained in private qa109 evidence. Natural host-driven simulation and independent review remain pending; no simulated answers are prefilled.

## Safety And Privacy

Synthetic inputs only. Credential guards and scope/version checks remain in existing APIs. No private requirements or actual transcripts copied into source. No network calls, new dependencies, global installation or business execution.

## Risks And Follow-up

Candidate status only. Agent semantic coverage remains necessary; this adapter is not an OS enforcement boundary. Cross-stage task restoration belongs to issue 110. Inherited structure-validator findings remain separate. Cases remain unexecuted.

Refs: https://github.com/Zengxiansheng007/coedx-home/issues/109

## 2026-11-12 independent repair round

Baseline: isolated combined candidate de414b0 (frozen PRE03 c9e3838, QA108 035b3e8, QA109 becd8f8; integration ef5d4b4).

Feedback validates explicit proposals and answer updates together using the normal summary conflict collector before mutation. New feedback questions no longer cause frontier KeyError. Coverage survives feedback entry as stale and must be reread. Historical actual 21-event simulation completed at 7de04d470812a270c69b596fd29d56a45f177e57c872dd273bb1d92bb573167a (root dialogue-08-final-proof); this is prior healthy-path evidence, not repaired conflict acceptance.

Validation: public-entry regressions in test_three_repairs.py; red reproduces all three findings plus new-question KeyError. Full suite and create-skill results are retained by Root outside the package. No private materials or actual reply transcripts are bundled. Status remains applied pending independent affected dialogue and review. No installation, formal merge or business execution.

Repair validation outcome: 129 standard-library tests pass; 71 source/mirror files match. create-skill --require-change-records retains 7 inherited findings (3 safety-negative fixture matches, 3 structure/resource findings, 1 description finding); not a clean validator pass or host acceptance. git diff --check passes. Prior PRE03 original client projection is byte-equivalent; prior sole Markdown replays without writing. Prior QA109 record remains unchanged but combined-version replay rejects its old exact summary; fresh affected simulation is required. Preserve all earlier failures and successful evidence at their original versions.

Compatibility correction after the above observation: the old QA109 event 12 summary matched exactly with no coverage; PRE03 then inserted empty case_bindings into history, changing the next content hash without business meaning. Persist bindings only when actual evidence exists. Targeted 24 tests pass; original QA109 21-event record replays to its exact 7de04d470812a270c69b596fd29d56a45f177e57c872dd273bb1d92bb573167a version without changing its bytes. The prior refusal remains a recorded intermediate failure, not the final recovery limitation. Actual nonempty identity binding remains protected. QA108 still requires its new affected simulation; no history is rewritten.

## 2026-11-12 local integration evidence

Frozen candidate 6679a11172b35a2810d6fe419390f5a0d76021f3 fast-forwarded from ef5d4b4 under Root authorization. This follow-up changes evidence records only.

QA109: actual 21-event synthetic feedback and ten final checks passed. Unchanged sole-record replay restores complete candidate equality at 7de04d470812a270c69b596fd29d56a45f177e57c872dd273bb1d92bb573167a. Healthy actual-path evidence is reused; conflict rejection and appended-question/coverage behavior passed independent targeted tests and review. No dialogue outcome is fabricated.

Independent re-review closed three P1 findings and the composition issue; six focused tests passed. Reuse 129 full tests before the optional-metadata fix and 24 affected tests afterward, without repeating unchanged suites. Private actual/review evidence stays outside the package; historical versions/failures remain. Seven inherited scanner findings (3 P0 / 3 P1 / 1 P2) remain, not a clean scan. No publishing, Issue closure, installation or business execution.
