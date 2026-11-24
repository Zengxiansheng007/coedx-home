# CR-20261116-015 - Local companion link delivery

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | scripts-and-validation / references-and-assets / downstream-and-handoff |
| Source | actual Windows XMind companion click failure; REQ-014/015/017; AC-017/018/021/023 |
| Baseline | 0270247ffde69cfc0c54ad1367621933537880e7 |
| Author | Codex |
| Related Records | CR-20261116-010; CR-20261116-013 |

## Summary
Bind delivered local companion links to their actual files while preserving conservative feedback interpretation.

## Context And Problem
The imported native document retained the relative Agent-notes href. Actual clicking opened an HTTP address and a blank page. Materialization verified file existence but never established a local-file link. Existing edited native return qualification remains valid and is preserved.

## Sections Changed
| File | Section | Change Summary |
|---|---|---|
| scripts/module_handoff.py | entrance and write_artifacts | Explicit local destination in saved XMind Markdown |
| scripts/feedback.py | Markdown header interpretation | Exact source-directory-bound normalization |
| scripts/xmind_feedback.py | inspection, preparation and CLI | Bind native link to generated header and original delivery directory |
| scripts/test_companion_links.py; scripts/test_external_handoff.py; scripts/test_module_handoff.py | public delivery and feedback seams | Encoding, relocation, scoped-prefix retention, CLI file URI and rejection regressions |
| references/module-handoff-contract.md | delivery | Local paths, portability and rematerialization |
| references/xmind-feedback-contract.md | source binding | Preserve historical return and reject unbound links |

## Decision And Alternatives
Retain one existing module document, no index, attachment, copy, server or installation. Resolve local links only on delivery, leaving portable render and candidate semantics unchanged. A returned arbitrary URI is never a trusted allowlist. The exact original delivery directory is supplied by the operator and combined with the current batch to reconstruct the expected link. Actual client behavior requires separate evidence.

## Detailed Change
Delivery resolves local references through Path.resolve().as_uri() and encodes section fragments. Only the saved XMind entrance changes; portable render and batch remain unchanged. Feedback normalizes an exact source-bound materialized entrance to the existing canonical form before unchanged identity and scalar guards. The native CLI exposes --companion-base.

## Impact Analysis
Only TCA local package and identical repository mirror. Public write_artifacts callers share the same materialization; native and Markdown feedback preserve identity and scalar-change guards. No global skill or executor change.

## Validation Evidence
| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| Red regression | unittest test_companion_links | local href and missing return-binding fail | evidence/companion-link-fix/red.txt; return-red.txt outside repo |
| Historical actual native return | read-only replay with original explicit bindings | ready_for_clarification, one change, inputs unchanged | actual-return-before.json outside repo |

| Targeted regression | unittest test_companion_links test_module_handoff test_xmind_feedback | 11 passed | regression.txt outside repo |
| Historical actual native return after change | same read-only replay | ready_for_clarification, one change, original hashes unchanged | actual-return-after.json outside repo |
| Client file URI probe | Root-operated actual import and user reply/screenshot | local-file icon and trust prompt observed; user confirmed manually opening target; Root owns evidence | scoped actual-client evidence outside repo |

| Scope-prefix regression | compare complete scoped Markdown except link destinations | failed before fix, passed after; scope non-deletion and validation boundary retained | scope-header-red.txt; scope-header-green.txt outside repo |
| CLI regression | unittest test_external_handoff test_companion_links | 8 passed; prior relative-path test assumption updated to file URI | cli-regression.txt outside repo |
| Required package checks | tools/checks.py | all eight stages passed; 239 authoring tests passed | checks-final/summary.json outside repo |
| Skill traceability validator | validate_create_skill.py --require-change-records | rejected: exactly three inherited synthetic credential fixtures; P1=0, P2=0; fixtures unchanged | skill-validation.txt outside repo |
| Changed-file privacy review | source/mirror diff and fixture-baseline comparison | no private paths or real materials introduced; original negative fixtures unchanged | pre-freeze-review.json outside repo |

## Safety And Privacy
Only synthetic tests and generalized records committed. Private actual material and generated machine paths stay outside the package. No publish, installation or business execution.

## Risks And Follow-up
Candidate only. Absolute local destinations remain machine-local; moving the complete folder requires rematerialization at its new location. Moving only a native review file retains its source-directory binding. The client can require a trust prompt and manual file association; never suppress these. Actual probe success is scoped to the observed Windows client and supplied target, not arbitrary clients or complete business acceptance. Native headers with multiple links retain the existing pending-interpretation boundary.

Refs: #121; #131; #133; [official local file links](https://xmind.com/user-guide/link-new).
