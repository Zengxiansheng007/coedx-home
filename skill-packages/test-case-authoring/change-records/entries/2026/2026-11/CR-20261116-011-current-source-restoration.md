# CR-20261116-011 - Current-source restoration and distribution repair

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | core-skill-md / references-and-assets / scripts-and-validation / downstream-and-handoff |
| Source | TAS-11 #132, AC-019 through AC-022 |
| Baseline | 74f886b |
| Author | Codex |
| Related Records | CR-20261116-007, CR-20261116-008, CR-20261116-009, CR-20261116-010 |

## Summary
Transient current-source restoration isolates dependent failures before review and handoff, preserving original candidates and unrelated work.

## Context And Problem
Whole-catalog eager expansion blocked independent selected content. Cross-module source changes and materialized technical sources were not integrated into review/recovery. Summary copied a batch-wide data version to unchanged cases, causing false source drift. The tracked project TCA mirror lagged canonical by 49 files in the original checks/copies.json baseline.

## Sections Changed
| File | Section | Change Summary |
|---|---|---|
| scripts/restoration.py | preflight | Current source/data validation and nested complete restoration |
| scripts/scoped_review.py, clarification.py, feedback.py | public review | Selective blockers and exact selected approval |
| scripts/qa_record.py, module_handoff.py, extension.py, partial_merge.py | recovery/delivery | Actual candidate/source/doc reading; whole P0 gate preserved |
| scripts/cross_module_references.py | digest | Review/execution state is not business-source drift |
| references/restoration.md, SKILL.md | workflow | Source evidence and planned/materialized boundary |
| scripts/test_restoration.py and affected regression fixtures | public boundaries | Synthetic positive/negative review, source drift, nested cycle and recovery |
| .agents/skills/test-case-authoring | distribution | Exact canonical tracked package copy, historical records preserved |

## Decision And Alternatives
Reuse the sole candidate, public resolver and Q&A record. Do not add maintained expanded files, a mandatory state pack, or global installation. Current sources are caller-supplied evidence, not authority invented from cached digests. Unknown mirror extras are reported, not deleted.

## Detailed Change
Blocked case IDs and concrete clarification reasons accompany the unchanged candidate. Pure renders remain planned; artifact writing is selective and read back. Existing drafts use their real entry, and extension evidence still qualifies the entire approved P0 round.

## Impact Analysis
Independent seam audit found two additional source-propagation defects: writer filtered rendering lost the external catalog, and candidate same-ID data could shadow the source actually validated. Both have public failing/passing tests in red-seam-audit.txt and green-seam-audit.txt; source conflicts now block the dependent case explicitly.
Review feedback identity and unshown records survive. Old synthetic fixtures now supply actual current catalogs for source-bound review; changed shared data no longer receives a fabricated dependent approval. Preparation scope expiry reverts to complete inline meaning.

## Validation Evidence
| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| Public red-green | test_restoration.py | recorded | local evidence/tas-11/red.txt and green.txt |
| Full regression | unittest discover | see final report | local evidence/tas-11/regression-final.txt |
| Distribution and mandatory checks | tools/checks.py | see final report | local evidence/tas-11/checks |
| Change records validator | validate_create_skill.py --require-change-records | retain inherited findings | local evidence/tas-11/skill-validation.txt |
| Real dialogue/client/business | not performed | unverified | outside synthetic implementation evidence |

## Safety And Privacy
Synthetic fixtures only. Three inherited safety-test credential strings remain separately adjudicated, never erased to manufacture clean output. The historical inline-resource regex finding was resolved by quoting the actual CLI path; original failure output remains. No private source, global installation, remote write or business execution.

## Risks And Follow-up
Candidate implementation; actual four-case trial and XMind client acceptance belong to TAS-12. Human interpretation of supplied technical source bindings remains the agent responsibility; deterministic readers do not infer undocumented business facts.

Refs: #132, #121
