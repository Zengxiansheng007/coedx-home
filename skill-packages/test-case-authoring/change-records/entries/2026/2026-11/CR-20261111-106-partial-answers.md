# CR-20261111-106 - Partial answers and dependent rounds

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | core-skill-md / references-and-assets / scripts-and-validation |
| Source | Issue 106; confirmed questioning requirements REQ-004 |
| Baseline | 46b654a2e6b438d8223a6dc63155e3115f65c744 |
| Author | Codex |
| Related Records | CR-20261111-105 |

## Summary

Preserve partial answers in the sole task Markdown and ask remaining aspects or an explicit unknown disposition before closing a rule.

## Context And Problem

Any prior reply was treated as complete. Unknown could only be recorded as an inert note; a reopened premise could leave an already displayed dependent question eligible.

## Sections Changed

SKILL.md batch sequence; clarification-contract.md and qa-record-contract.md; clarification.py completeness, presentation and dependent invalidation; test_partial_answers.py public persisted regressions. Distribution mirror matches source.

## Decision And Alternatives

Reuse issue 105 event replay and grill-with-docs/TPD aspect checks. No second answer store, new dependency, independent business approval or runtime expansion. Semantic interpretation remains with the agent; named aspects support deterministic omission checks without pretending to parse natural language.

## Detailed Change

Named object/condition/behavior aspects accumulate only supplied answers. Partial and unknown are incomplete response states, not business dispositions. Unknown returns complete Chinese choices, recommendation, rationale, boundary and example. Three existing explicit decisions remain formal/provisional/deferred. Summaries retain accumulated aspects; corrections preserve history and reopen only declared descendants. Reopened premises withdraw stale dependent questions.

## Impact Analysis

Legacy single-aspect questions remain compatible. Compound live questions must declare aspects; agent must verify actual words and dependency semantics. Candidate updates still await exact summary confirmation, full-case review remains separate, and unrelated questions retain their decisions.

## Validation Evidence

Three public-interface red-green slices observed: partial rejected before implementation; unknown lacked disposition prompt; reopened premise wrongly left FOLLOW eligible. First full regression: 99 passed. Latest combined regression and validator outputs are retained outside the repository under ticket qa106 evidence. Actual 16-event host simulation completed: partial and unknown remained open, only declared dependencies were revisited after 100-to-80 correction, the old summary was not applied, and the new summary was applied once before exact-version final simulated review. Private qa106/dialogue-observed.md and dialogue-index.json retain actual replies and source hashes. Independent ticket review found no blocking standards or specification issue (private review-106-107.md). Integrated unittest discovery passed 114 tests (private integration-106-107-regression.txt).

## Safety And Privacy

Synthetic inputs only; credential guards retained. No private requirement text, real business cases, secrets or transcripts copied into source. No global installation, remote writes or business execution. Existing structure-validator findings are reported separately and do not grant acceptance.

## Risks And Follow-up

Full-batch post-integration review remains separate; ticket-level simulation and independent review are complete. Existing structural-validator findings remain open; applied status is not host acceptance. Aspect completeness does not prove semantic correctness or source coverage. Scope discovery, feedback and cross-stage recovery belong to later tickets. All candidate cases remain unexecuted.

Refs: https://github.com/Zengxiansheng007/coedx-home/issues/106
