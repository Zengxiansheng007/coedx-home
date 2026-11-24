# CR-20261117-101 - Named scalar data and feedback

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | core-skill-md / references-and-assets / scripts-and-validation |
| Source | TCO-01 #135; parent #134 AC-029 and data portion of AC-034 |
| Baseline | 1b7a133ee03644e304e9819486c210143d362eb5 |
| Author | Codex |

## Summary
Render explicit object plus single scalar together and map edited expressions back to original fields.

## Context And Problem
The shared renderer flattened every data field independently, and feedback accepted only one probe per line. Layout-only changes therefore needed compound field binding and preservation of the actual pre-TCO layout.

## Sections Changed
| File | Change |
|---|---|
| scripts/data_projection.py | Conservative scalar projection and exact probe decoding |
| scripts/scoped_review.py | Shared rendering; optional historical data layout |
| scripts/feedback.py | Compound edits, repeated-value agreement and legacy fallback |
| scripts/test_simple_data.py and scripts/fixtures/pre-tco-pair.md | Real public generation/save/feedback and historical export regression |
| SKILL.md; references/review-expression.md; references/feedback-contract.md | Invocation pointer, data rules, examples and feedback ambiguity |

## Decision And Alternatives
Reuse existing candidate identity, renderer probes, immutable first-display baseline and feedback review. Extra business fields keep labelled structure. No arbitrary colon split, string-length heuristic, independent data authority or automatic migration.

## Detailed Change
Only an explicit name and one scalar with no additional visible business condition compact. Configuration colons remain literal. An unchanged field anchors a one-field edit; simultaneous edits require a unique full-width display boundary. Ambiguous edits remain pending clarification. Old separated data exports retain their own layout fallback independently of historical audit rows.

## Impact Analysis
Canonical and distribution mirror updated identically. Generation, scoped review, save/readback and resumed rendering share the same projection. Original data, references, sources and historical baseline survive. Explicit empty string values are valid data inputs. Numeric leaves keep existing feedback restrictions; structural changes require explicit interpretation. TCO-02 shares rendering/feedback and must retain the new historical-data option during integration.

## Validation Evidence
Four red/green public slices: external evidence/tco-01/red-1..4.json and green-1..4.json. Eight targeted tests and 27 feedback/data regression tests passed (green-4.json); test-only corrections preserve earlier edge-tests.json. The old fixture was emitted by baseline 1b7a133 public build_scoped_review. Full authoring 259 tests passed before the final empty-value slice. Initial repository checks passed seven stages; copies detected a test-file update during the run and was corrected by syncing both copies. Final frozen checks are in external test-output/tco-01/checks-final/summary.json. create-skill reports only three inherited synthetic secret-pattern fixtures, with P1=0 and P2=0 (external validator.json); no new finding.

## Safety And Privacy
Synthetic inputs and SIMULATED replies only; no real material, account data or credentials. No installs, global changes, remote writes or business actions. Source records stay unchanged; candidates remain pending actual review.

## Risks And Follow-up
Candidate implementation only. Actual Skill dialogue, user import/edit/return and real business review belong to later increment acceptance. Existing validator synthetic-secret negative fixtures remain separate from actual sensitive data. Tool timeouts in historical copy and first regression attempt are retained in the execution evidence; no success inferred.
