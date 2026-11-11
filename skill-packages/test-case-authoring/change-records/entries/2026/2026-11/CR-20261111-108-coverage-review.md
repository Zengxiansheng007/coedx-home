# CR-20261111-108 - Source coverage and scope decisions

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | core-skill-md / references-and-assets / scripts-and-validation |
| Source | Issue 108 |
| Baseline | ef5d4b457e6fd24e480b7f348da97a16d1fe25a0 |
| Author | Codex |
| Related Records | CR-20261111-105 / CR-20261111-106 / CR-20261111-107 |

## Summary

Reread original materials, reply history and direct dependencies before summary; append discoveries to the sole task MD and preserve full approved P0 scope across display and isolated merge.

## Context And Problem

Answered registered questions did not account for source omissions. Display selection also incorrectly rejected approved validation IDs outside selected cases.

## Sections Changed

SKILL.md sequence, coverage-review/clarification/qa-record references, clarification and journal public actions, scoped_review validation scope, public coverage regressions and matching distribution.

## Decision And Alternatives

Reuse grill-with-docs coverage 1.0.0 and TPD source-item review obligations as Agent steps. Keep existing Q&A replay and full P0 checker. No new independent answers or business approval ceremony. Deterministic checks cannot establish semantic completeness or authenticate source reading.

## Detailed Change

append_questions preserves history and invalidates summaries. record_coverage retains branches, source findings, unknowns and actual disposition references. Later answers invalidate its revision. Scoped review accepts approved IDs from the whole catalog, not only displayed IDs; unknown IDs remain invalid.

## Impact Analysis

Legacy pure computation remains compatible. Live Skill must perform source review, not merely populate fields. Deferral retains unknown behavior and blocked cases. Range and priority proposals require actual user decisions. Existing reporting, full-case review, merge and execution boundaries remain separate.

## Validation Evidence

| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| TDD discovery | public MD append action | observed Unknown Q&A action then passing | private qa108 TDD observations |
| TDD source disposition | public coverage action | observed Unknown Q&A action then passing | private qa108 TDD observations |
| TDD approved scope | public scoped review | observed selected-case restriction then passing | private qa108 TDD observations |
| Public targeted regressions | unittest test_coverage_review | 4 passed before freeze | private targeted output |
| Full regression | unittest discover scripts/test_*.py | 118 passed; old display-limited test updated to reject genuinely unknown IDs, original failure retained | private regression-r2.txt |
| Structure / mirror | candidate checks | 7 inherited validator findings; zero mirror mismatches; no host acceptance claimed | private candidate-checks.json |
| Actual dialogue | independent natural multi-turn simulation | pending Root execution | no prewritten success or future replies |

## Safety And Privacy

Only synthetic regressions and public contracts are committed. No private source materials, global installation, external model, network publish or business execution. Local checks are not host security enforcement.

## Risks And Follow-up

Actual source rediscovery, complete scope/priority questions and independent review remain pending. Baseline structural-validator findings are reported separately. Applied status is not semantic, business or host acceptance.

Refs: https://github.com/Zengxiansheng007/coedx-home/issues/108

## 2026-11-12 independent repair round

Baseline: isolated combined candidate de414b0 (frozen PRE03 c9e3838, QA108 035b3e8, QA109 becd8f8; integration ef5d4b4).

Separate impact disposition now requires explicit disposition_scope and scope_basis with no write targets; ordinary unknown rules and dependent cases remain blocked. Deferred history remains visible. Prior actual dialogue failure is preserved and requires a fresh synthetic task, not rewritten summary hashes.

Validation: public-entry regressions in test_three_repairs.py; red reproduces all three findings plus new-question KeyError. Full suite and create-skill results are retained by Root outside the package. No private materials or actual reply transcripts are bundled. Status remains applied pending independent affected dialogue and review. No installation, formal merge or business execution.

Repair validation outcome: 129 standard-library tests pass; 71 source/mirror files match. create-skill --require-change-records retains 7 inherited findings (3 safety-negative fixture matches, 3 structure/resource findings, 1 description finding); not a clean validator pass or host acceptance. git diff --check passes. Prior PRE03 original client projection is byte-equivalent; prior sole Markdown replays without writing. Prior QA109 record remains unchanged but combined-version replay rejects its old exact summary; fresh affected simulation is required. Preserve all earlier failures and successful evidence at their original versions.
