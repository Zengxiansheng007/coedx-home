# CR-20261116-016 - Technical note object identity

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | scripts-and-validation / references-and-assets / downstream-and-handoff |
| Source | user-confirmed duplicate technical scopes; AC-017/018/021/023 |
| Baseline | 1136bc8afe594a503f90af21d8ae84955c27f908 |
| Author | Codex |
| Related Records | CR-20261116-010; CR-20261116-013; CR-20261116-015 |

## Summary
Preserve object identity and full rule distinctions while removing repeated applicability within one case.

## Context And Problem
The generator grouped rendered rule text alone, substituted the case title for data without title/name, and appended repeated scopes. This confused distinct objects and hid full-path differences. Row-level deduplication could not repair repeated scope entries.

## Sections Changed
| File | Section | Change Summary |
|---|---|---|
| scripts/review_projection.py | technical_notes | Original-value/path grouping; object identity, readable labels and ambiguity preservation |
| scripts/test_technical_notes.py | public artifact tests | Synthetic red/green, identity, original whitespace, paths and local persistence |
| references/source-assessed-display.md | technical-note grouping | Exact grouping and unchanged-authority contract |

## Decision And Alternatives
Reuse the existing assessment, rendering and module writer. Group by complete path, scalar type and original value with outer whitespace trimmed. Semantic normalization and set-of-display-name compression are unsafe because they erase distinctions. No new index, candidate schema, business authority or dependency.

## Detailed Change
Data object_ref names are shown with collection-scoped owner IDs and complete JSON Pointer paths. Chinese labels supplement known fields. Distinct identities with the same name remain separate; known repeated identity collapses once. Ambiguous identity retains each occurrence with a position and warning. Interior whitespace remains visible through reversible escapes. Grouping stays inside one case.

## Impact Analysis
Only canonical TCA and identical repository mirror. The candidate, content version, source bindings, review state, business body, feedback and link semantics remain unchanged. Existing module case-section replacement retains omitted cases.

## Validation Evidence
| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| Public TDD | unittest test_technical_notes | Six tests passed after five red/green slices | external evidence/technical-notes-fix/implementer/red-1.json through green-5.json |
| Preservation | Public render_review_batch and write_artifacts | Candidate equality, business body, deterministic generation and partial sections retained | external implementer/preservation-corrected.json |
| Fixture correction | Add missing synthetic selection owner | Initial KeyError preserved; corrected public setup passed | external implementer/preservation.json and preservation-corrected.json |
| Implementation correction | CRLF-aware source edit | Initial NameError preserved; corrected loop passed | external implementer/green-3.json and green-3-corrected.json |
| Skill traceability validator | validate_create_skill.py --require-change-records | Exactly three inherited negative credential fixtures; P1=0, P2=0; candidate remains applied | external implementer/validator-corrected.json |
| Validator naming correction | Rename non-secret local scope key | Initial extra scanner finding retained; no real credential present | external implementer/validator.json |
| Full checks | tools/checks.py | All eight stages passed; 244 authoring tests passed before the final four-label mapping addition | external test-output/technical-notes/implementer/checks-final/summary.json |
| Final label increment | unittest discover test_technical_notes.py | Six tests passed on final source, including case and selection labels; reused unaffected full checks | external implementer/red-5.json and green-5.json |
| Initial full-check launcher | Node wait | Kernel timeout interrupted the first run; partial output retained, not counted as passed | external test-output/technical-notes/implementer/checks |

## Safety And Privacy
Synthetic fixtures only; no real source paths, credentials or business material committed. Private source verification remains outside the repository. No global installation, dependency addition, publishing or actual business execution.

## Risks And Follow-up
Applied candidate only; independent review and private four-case verification are Root-owned. Reuse prior client evidence only for unchanged behavior; this change does not claim fresh XMind operation or business approval. The inherited validator findings in negative credential fixtures remain separately recorded.

Refs: #121; #131; #133; source-assessed-display contract.
