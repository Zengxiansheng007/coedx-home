# CR-20261114-002 - Graded titles and expectation expression

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | core-skill-md, references-and-assets, scripts-and-validation |
| Source | Issue 114, REQ-009/017, AC-015/025 |
| Baseline | 3b9cb992db1211e9a5c08f0e40a43ac6cb6cfa7c |
| Author | Codex |
| Related Records | CR-20261114-001 |

## Summary
Same-version total, scoped and chat views use priority plus one space plus business title.
Exact duplicate checks are suppressed without changing internal source claims.

## Context And Problem
Ungraded titles and repeated expected/verification claims obscured business review.

## Sections Changed
Shared review_expression helper, scoped projection, aggregation title mapping,
feedback probe visibility, public-entry regression fixtures and source-review guide.

## Decision And Alternatives
Agent reviews semantic equivalence against sources and canonicalizes equivalent
wording. The renderer removes exact duplicates only; it never guesses synonyms.
Independent observation locations, objects and results remain visible.

## Detailed Change
Probe visibility is fixed to the original candidate so hidden duplicates cannot
shift source offsets. Title feedback strips only the trusted grade and retains ID.
Historical ungraded exports retain the existing exact legacy layout fallback.

## Impact Analysis
Integrated issue 113 module instructions unchanged. No installation, publishing,
formal catalog writes, ui-test changes or real business execution.

## Validation Evidence
Public test_review_expression red: missing P0 heading; green: three priorities,
duplicate suppression, independent check, immutable source and unchanged return.
Full regression and validator results are recorded in external test-output/rr02.
After integrating issue 113, 150 tests passed (15.248s). Targeted test passed again.
Skill validator retains seven inherited findings (description trigger wording,
missing validation/safety headings, three synthetic credential-test matches,
and command-path parsing); no change-record finding. Not claimed validator-clean.
Frozen historical fixtures are retained rather than regenerated.

## Safety And Privacy
Only synthetic fixtures and general instructions added. No credentials or private inputs.

## Risks And Follow-up
Candidate only. Actual XMind client acceptance belongs to issue 119; no automatic
natural-language equivalence claim. Hidden-claim edits use explicit chat interpretation.
