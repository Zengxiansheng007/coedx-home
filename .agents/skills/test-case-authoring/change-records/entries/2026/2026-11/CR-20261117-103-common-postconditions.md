# CR-20261117-103 - Common postconditions

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | core-skill-md / references-and-assets / scripts-and-validation / downstream-and-handoff |
| Source | #134 and #137 |
| Baseline | e1b7ea9c6dadf5cdde3b0b48c586a582aea0a034 |
| Author | Codex |
| Related Records | CR-20261117-102 |

## Summary
Retain actual post obligations from authoring through common directional scope, module projection, feedback, save and restoration.

## Context And Problem
Post fields were dropped at generation and absent from consumer groups; the scope adapter rejected post direction. Adding a group also changes old reuse digests unless absent fields retain the historical signature.

## Sections Changed
| File | Section | Change Summary |
|---|---|---|
| SKILL.md; references/aggregation-contract.md; references/batch-contract.md; references/restoration.md | Contract and example | Both directions, absence, original sequence |
| scripts/authoring.py; scripts/preparation_scope.py; scripts/aggregation.py; scripts/scoped_review.py | Public generation and rendering | Preserve post source and scope/feedback origins |
| scripts/step_reuse.py; scripts/local_step_feedback.py; scripts/cross_module_references.py; scripts/module_handoff.py; scripts/clarification.py; scripts/partial_merge.py | Consumers | Include post steps/data without changing absent legacy digests |
| scripts/test_common_postconditions.py; assets/fixtures/post-legacy-reuse-e1b7ea9.json | Public checks | Synthetic current and actual baseline reference fixture |

## Decision And Alternatives
Extend existing preparation_scopes v2; original case steps remain authoritative. No duplicate state or automatic cleanup. Both directions use the same module projection and source bindings.

## Detailed Change
Direction-specific source group, notes and overlap checks retain local identities. Optional fields survive source validation and generation. Post data, provenance and expectations reach every group consumer and restored sequence.

## Impact Analysis
Public feedback proposes only applicable owners. Scope changes retain existing local invalidation. Broader subset lifecycle remains #138. Historical absence preserves old signatures and no post display.

## Validation Evidence
Red/green public generation, scope, save/read, feedback and restoration records are in external evidence/tco-03. Frozen baseline fixture exposed absent-field signature regression before repair. Final checks recorded in result.md.

## Safety And Privacy
Only synthetic fixtures; no private business material, remote/global writes or execution. No new runtime dependency. Existing secret-negative test fixtures remain evidence, not credentials.

## Risks And Follow-up
Applied candidate. Actual user draft review and XMind import remain unverified; local tests cannot confer business acceptance. Complete current scope review is a supplied evidence judgment.

Refs: #134; #137.

## Final validation

All eight required stages passed in external test-output/tco-03/checks-post-notes/summary.json and evidence/tco-03/checks-post-notes.log. workflow-tests: Ran 67 tests; verification-tests: Ran 8 tests; authoring-tests: Ran 274 tests; grill-distribution-tests: Ran 1 test. Validator remains exactly three inherited negative-fixture findings, no new findings. Five postcondition public tests pass; prior failures preserved. Mirrors and diff checks passed. Candidate pending independent review; no client/business acceptance.
