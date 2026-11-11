# CR-20261111-202 - Semantic review aggregation

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | core-skill-md, references-and-assets, scripts-and-validation |
| Source | Approved PRE-02 presentation task |
| Baseline | 43456ac371ad65972b86219ee7912d6f61e6247b |
| Author | Codex |
| Related Records | None |

## Summary
Project complete semantic paths once and share identical ordered preparation within a function, retaining case applicability and all special groups.

## Context And Problem
Both batch and scoped output repeated directory trees. Feedback inferred source positions from that layout, so aggregation also requires a reversible projection.

## Sections Changed
| File | Section | Change Summary |
|---|---|---|
| SKILL.md, references/aggregation-contract.md | Rendering workflow | Source, applicability and client verification rules |
| scripts/aggregation.py | Projection and feedback expansion | Full paths, preparation comparison, source bindings |
| scripts/authoring.py, scripts/scoped_review.py | Public rendering | One aggregated tree |
| scripts/feedback.py | Markdown return | Expand shared edits before existing business review |
| scripts/test_aggregation.py, scripts/test_feedback.py, scripts/test_dependencies.py | Public regression | Semantic differences, native returns, current subtree layout |

## Decision And Alternatives
Reuse existing complete scoped leaf rendering and scalar feedback interpretation with reversible line ownership. Avoid title-only grouping or persistent duplicate business sources.

## Detailed Change
Compare ordered steps, context, data and dependencies; retain preparation references for every case and preserve singleton preparation. Hide nested technical version hashes already represented by the batch header. No clarification API or output-file policy changes.

## Impact Analysis
Authoring, scoped review, Markdown and supported native XMind feedback consume the same layout. Case source records and execution preparation remain unchanged. PRE-03 can reuse source bindings; stable English IDs remain visible in this ticket.

## Validation Evidence
| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| TDD | Public aggregation test before implementation | Failed as expected: duplicate path | Private execution transcript |
| Regression | unittest discover in skill scripts | 99/99 passed, including conservative object identity comparison | Private PRE-02 evidence |
| Real client import | XMind 26.4.1327.202606142039 menu import and local native save | Passed for the exact synthetic r1 hierarchy; all 127 titles and tree positions equal source Markdown | Private host observation and independent complete-tree comparison |
| Presentation behavior | Public batch/scoped output, shared Markdown/native feedback and actual client output | Exercised directly; separate generic multi-turn simulation not required for this presentation-only ticket by host | Public regressions and private client evidence |
| Structure, mirror, privacy | Skill validator and byte comparison | No new validator findings; inherited 3 P0 / 3 P1 / 1 P2 remain; final mirror check recorded privately | Final handoff |

## Safety And Privacy
Only synthetic fixtures and generic implementation are packaged. Private requirements, business assets and client evidence remain outside the repository. No global install, network calls, publishing or business execution.

## Risks And Follow-up
Candidate only; independent code review remains. Actual client evidence covers only the imported r1 hierarchy and original text, not business correctness, arbitrary clients or later title changes. The synthetic r1 closing step reused a save expectation: preserve that historical input and evidence, and use the separately corrected r2 fixture for later semantic demonstrations; r2 has not been imported. Semantic comparison is conservative exact structured equality plus aligned rendered descendants, not inference of natural-language synonyms. Nested object IDs remain significant; only generated top-level step IDs are ignored. Structural edits outside supported scalar feedback remain clarification work. Inherited validator findings are not claimed fixed by this ticket.

## Acceptance Coverage

| Criterion | Result | Basis |
|---|---|---|
| AC-013 | Passed for presentation scope | Public batch/scoped tests and actual full-tree comparison preserve complete paths and same-name product/system levels |
| AC-014 | Passed for presentation scope | Exact preparation sharing, context/order/data/expectation/object differences, special groups, singleton applicability and shared feedback regressions |
| AC-016 scope portion | Passed | Selection excludes unselected cases and retains original catalog content |
| AC-022 hierarchy portion | Passed for exact r1 client input | Real menu import, native save and 127-topic complete comparison; later PRE-03 titles require new import |

Refs: [Aggregation contract](../../../../references/aggregation-contract.md).

## Independent Review Repair R1 / R2

Repair baseline: 4d44a93229afd6f48fbf3323aaddc4fdd98769f4; integration input 46b654a2e6b438d8223a6dc63155e3115f65c744. The prior 99-test and actual 127-topic client evidence remains historical; it did not cover these display regressions.

- R1: shared rendering previously listed every question as unresolved. Both public entries now omit valid answered questions from pending nodes, retain history, and display unanswered or stale questions.
- R2: shared rendering previously contradicted a source-backed no-preparation note with an unknown placeholder. The note now appears once inside common preparation; only missing preparation and missing notes yield the placeholder. Notes alongside actual preparation steps are preserved.
- S1: clarify stack and semantic-parent operations with local right-side comments.
- TDD: each new public regression failed for its intended display assertion before the respective fix. An earlier test setup with one option was rejected and retained separately. Pre-integration full suite: 101 tests passed. Integrated verification is recorded separately.
- Merge resolution: preserve both CR-105 and CR-202 index/ledger entries; retain the integrated Q&A adapter, clarification changes and Skill instructions. No clarification API changes made by this repair.
- Acceptance impact: AC-014 display correction and REQ-014 consistency require the new affected-client sample; original r1 import remains valid for its exact original input, not evidence for this correction. No PRE-03/04 changes or business execution.
