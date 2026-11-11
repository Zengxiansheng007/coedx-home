# CR-20261111-203 - Chinese presentation and stable identity

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | core-skill-md, references-and-assets, scripts-and-validation |
| Source | Approved PRE-03 presentation task |
| Baseline | 12f07270bf1ae55150d35b64dbc8f66184f298f6 |
| Author | Codex |
| Related Records | CR-20261111-202 |

## Summary
Separate business titles from stable internal identity in both public views and
bind feedback to the exact returned subtree after actual business clarification.

## Context And Problem
The aggregated tree exposed case IDs and used their heading prefixes for feedback
matching. Removing the prefix alone would lose rename and same-name identity.

## Sections Changed
| File | Section | Change Summary |
|---|---|---|
| SKILL.md, references/presentation-identity.md | Display and feedback | Chinese clarification and agent-only binding contract |
| scripts/presentation.py, authoring.py, scoped_review.py | Public views | Business title/reference display; stable source unchanged |
| scripts/aggregation.py, feedback.py, xmind_feedback.py | Return boundary | Exact subtree binding, current version, reply evidence and conservative ambiguity |
| scripts/test_*.py, identity_test_support.py | Public regression | Rename, same-name distinction, feedback and inherited display contracts |

## Decision And Alternatives
Reuse existing candidate IDs, immutable baseline, scalar mapping and review gates.
Unique full unchanged subtrees can match exactly. Edited subtrees require internal
bindings supported by actual business clarification. Never infer identity from
title or position. Native topic IDs lack a registered baseline and are not trusted.

## Detailed Change
Public headings and applicability omit English case codes; P0/P1/P2 remain.
Internal flat mapping and dependency IDs remain stable. Agent-maintained bindings
carry displayed version, complete returned subtree digest and actual reply; evidence
is retained and checked for tampering. Existing summary, review and merge boundaries
remain. Unseen cases remain in the full catalog.

## Impact Analysis
Ordinary/scoped views, Markdown scalar feedback and supported single-sheet native
returns share this contract. Human-view file emission belongs to PRE-04 and is
unchanged. No UI-Test assets, global installation or business execution changed.

## Validation Evidence
| Check | Method | Result | Evidence |
|---|---|---|---|
| TDD | Public identity tests before implementation | Failed as expected, then passed for initial slices | Private PRE-03 logs |
| Feedback regression | Existing 8 public feedback tests | Passed after trusted review metadata normalization | Private execution log |
| Combined regression and mirror | Full skill discovery, byte comparison | 118 tests passed after integrating 106/107; final mirror proof in handoff | Private PRE-03 evidence |
| Real dialogue and XMind client | Independent host exercise | Pending at implementation handoff | Host-owned evidence |
| Skill validator | require-change-records | Exactly seven inherited findings (3 P0 / 3 P1 / 1 P2); not passed | Private PRE-03 evidence |

## Safety And Privacy
Synthetic inputs only. Source requirements and transcripts remain private outside
the repository. No installation, network export, publishing or real execution.

## Risks And Follow-up
Candidate only. Completely indistinguishable returns require business clarification
and chat-based correction; arbitrary native annotations and structural edits remain
unsupported. Client import and actual multi-turn simulation must be completed by
the host before claiming full PRE-03 acceptance. Inherited validator findings remain.

## Acceptance Coverage

- AC-015: public tests cover both views, rename, distinct same-name cases and
  reordered subtrees with exact binding; internal IDs and other cases persist.
- AC-021 identity: both projections retain the candidate version; binding changes,
  stale versions and ambiguous returns fail; existing summary and review gates stay.
- Related dependencies and unselected records: existing dependency/partial-merge
  public regressions passed in the 118-test combined run.
- Historical generated ID headings: accurate baseline/path matching preserves
  scalar feedback without title or ordinal inference; new output hides those IDs.
- AC-022 Chinese-title client import and independent actual dialogue: pending host.

Refs: [Presentation identity](../../../../references/presentation-identity.md).

## 2026-11-12 independent repair round

Baseline: isolated combined candidate de414b0 (frozen PRE03 c9e3838, QA108 035b3e8, QA109 becd8f8; integration ef5d4b4).

Typed case_id/case_ids and generated applicability references resolve to names; all business literal strings stay intact. Feedback scalar probes hold derived names fixed. Pure legacy feedback preserves unrelated cases. Prior actual native import compared 89/89 topics and title-return review completed at e92156c8c04f08d68c46b846ae956eca77559a48cadc71c646e156c30991f3f9 (root dialogue-result); new literal-collision behavior still needs affected review.

Validation: public-entry regressions in test_three_repairs.py; red reproduces all three findings plus new-question KeyError. Full suite and create-skill results are retained by Root outside the package. No private materials or actual reply transcripts are bundled. Status remains applied pending independent affected dialogue and review. No installation, formal merge or business execution.

Repair validation outcome: 129 standard-library tests pass; 71 source/mirror files match. create-skill --require-change-records retains 7 inherited findings (3 safety-negative fixture matches, 3 structure/resource findings, 1 description finding); not a clean validator pass or host acceptance. git diff --check passes. Prior PRE03 original client projection is byte-equivalent; prior sole Markdown replays without writing. Prior QA109 record remains unchanged but combined-version replay rejects its old exact summary; fresh affected simulation is required. Preserve all earlier failures and successful evidence at their original versions.

Compatibility correction after the above observation: the old QA109 event 12 summary matched exactly with no coverage; PRE03 then inserted empty case_bindings into history, changing the next content hash without business meaning. Persist bindings only when actual evidence exists. Targeted 24 tests pass; original QA109 21-event record replays to its exact 7de04d470812a270c69b596fd29d56a45f177e57c872dd273bb1d92bb573167a version without changing its bytes. The prior refusal remains a recorded intermediate failure, not the final recovery limitation. Actual nonempty identity binding remains protected. QA108 still requires its new affected simulation; no history is rewritten.
