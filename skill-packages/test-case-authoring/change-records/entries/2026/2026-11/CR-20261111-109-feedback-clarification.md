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
