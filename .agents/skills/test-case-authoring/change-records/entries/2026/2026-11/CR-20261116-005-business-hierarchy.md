# CR-20261116-005 - Source-assessed business hierarchy

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | changed |
| Scope | core-skill-md, references-and-assets, scripts-and-validation |
| Source | TAS-05 / issue 126, parent 121 AC-008/022/024 |
| Baseline | 093ee090594368f174c2723d68ad9737d1e5de63 |
| Author | Codex |
| Related Records | CR-20261111-202, CR-20261111-203 |

## Summary
Render explicit source-assessed business groups while preserving cases and scope.

## Context And Problem
Module aggregation lacked a separate business hierarchy. Title inference would conflate
business semantics and stable identity. Existing feedback relies on reversible source offsets.

## Sections Changed
| File | Section | Change Summary |
|---|---|---|
| SKILL.md | Aggregation entry | Source assessment and review across generation/resume |
| references/aggregation-contract.md | Business groups | Announcement and other business, version and scope rules |
| scripts/aggregation.py | Projection and feedback | Generated group paths and group preparation ownership |
| scripts/scoped_review.py | Technical fields | Keep grouping source metadata internal and protected |
| scripts/test_business_hierarchy.py | Public behavior | Grouping, preservation, scoped exclusions, MD/native identity |

## Decision And Alternatives
Extend existing candidate metadata and lossless projection. No hardcoded classifier,
parallel business state, persistent mapping file or new daily module view.

## Detailed Change
Optional business_group path/source supplies assessed labels below existing module paths.
Only populated groups render. Missing metadata preserves legacy tasks; invalid supplied
metadata fails. Existing digest-and-reply feedback handles case rename within groups;
directory move/rename requires source clarification and regeneration, never guessed identity.
Grouping alone preserves semantic/data versions and complete case fields; scoped rebuilding
binds a new content version and source baseline.

## Impact Analysis
Both public batch and scoped rendering share the projection. Preparation equivalence is
bounded to the explicit business group; extraction policy itself is unchanged for TAS-07.
Existing scalar feedback, native parser and legacy records remain supported.
Case IDs, source, coverage, data, conditions, independent checks and endpoints are retained.

## Validation Evidence
| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| TDD | Public announcement grouping before/after implementation | Expected missing-hierarchy failure then pass | External tas-05 red-01-fixture-fixed and green-01-corrected logs |
| Targeted regression | unittest business hierarchy, aggregation, presentation identity, scoped review | 21 passed | External tas-05 regression-01.txt |
| Full regression | unittest discover -p test_*.py | 184 passed; added reverse-direction assertion then 3 hierarchy tests passed | External tas-05 full-suite-retry.txt, direction-check.txt |
| Skill validator | validate_create_skill.py --require-change-records | Rejected: inherited 3 P0 / 3 P1 / 1 P2 findings; no new record findings | External tas-05 validator.txt |
| Mirror / whitespace / privacy | Byte comparison, git diff --check, changed-file scan | Passed | External tas-05 completion report |
| User review / real client | Actual grouping review and XMind import/edit/return | Not verified; parser fixture is not client evidence | No actual review claimed |

## Safety And Privacy
Only synthetic fixture data is committed. No real source material, credentials, business
execution, global installation, network publishing or formal asset changes.

## Risks And Follow-up
Candidate only. Source string validation does not establish semantic truth or user approval.
Announcement fixture tests grouping mechanics; actual four-case trial is separate.
AC-008/022/024 implementation and public checks do not close actual user/client acceptance.
Inherited validator findings, if reported, remain separate from this ticket.

Refs: [Aggregation contract](../../../../references/aggregation-contract.md).
