# CR-20261117-105 - Goal and preparation ownership

| Field | Value |
| --- | --- |
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | core-skill-md / references-and-assets / scripts-and-validation |
| Source | TCO-05 #139; parent #134 AC-033 |
| Baseline | 1b7a133ee03644e304e9819486c210143d362eb5 |
| Author | Codex |
| Related Records | CR-20261117-017 |

## Summary
Separate necessary state preparation from independent verification by purpose,
source and actual consumers. Preserve entry and current-value dependencies.

## Context And Problem
The previous generic semantic guidance did not require existing-goal lookup or
explicit consumer assessment before transferring mixed preparation. In the local
four-case source sample, page entry included a time measurement unused by those
case goals. This is an agent-authoring instruction defect, not a renderer defect.

## Sections Changed

| File | Section | Change Summary |
| --- | --- | --- |
| SKILL.md | Authoring entry | Trigger ownership assessment before generation and after feedback/recovery |
| references/source-semantics.md | Entry | Reach the shared purpose contract |
| references/extension-contract.md | Candidate drafting | Existing goal and current-value check |
| references/goal-preparation.md | New contract and checklist | Purpose/source/dependency method and lifecycle limits |
| scripts/test_goal_preparation.py | Public tests | Synthetic goal, counterexample, unresolved rule and time sample |

## Decision And Alternatives
Keep semantics with the agent. No keyword classifier, domain special case,
mandatory sidecar or new production API. Existing source/interpretation APIs
preserve the authored semantics; public tests do not prove NLP instruction adherence.
No template file exists for this branch; update the inline drafting checklist and
extension candidate instructions instead of creating a second data format.

## Detailed Change
Existing catalog lookup precedes new independent goals. Split mixed preparation
while retaining required page entry. Capture dynamic values in the current case
at the dependency point. Unknown precision/tolerance/waits remain unresolved,
blocking only affected comparisons. Definition reuse never changes execution count.

## Impact Analysis
Canonical and distribution mirror receive identical bytes. No runtime behavior,
P0 evidence gates, original material, sole Q&A, global installation or business
execution changes. Source-grounded four-case output is isolated candidate evidence,
not full generation acceptance, a completed real time batch or user review.

## Validation Evidence

| Check | Command or Method | Result | Evidence |
| --- | --- | --- | --- |
| Public seam | unittest test_goal_preparation.py | 4/4 passed | Ticket evidence |
| Actual source authoring | Read source nodes, original P0, sole answers; freshly author candidate; public scoped generation/save/readback | Four cases preserve entry; no unrelated time capture; data unchanged | Isolated ticket output |
| Existing time goal | Read full catalog and actual Q3 | Two matching goals found; precision remains unresolved; no duplicate case created | Local assessment |
| Skill validator | validate_create_skill.py --require-change-records | Rejected: exactly 3 inherited synthetic credential-pattern findings; no new findings | Ticket skill-validation.txt |
| TDD | Steps-only change | No executable production change; no claimed red/green code fix | Public preservation checks separate from forward-test |

## Safety And Privacy
Only sanitized synthetic test content is committed. Private source paths and
actual generated four-case files remain in isolated local evidence. No new user
answers, approvals or execution results were synthesized.

## Risks And Follow-up
Fresh-context prompt evaluation is independent work pending Root dispatch.
Full TCO-07 generation, actual current-draft business review and XMind roundtrip
remain outside this ticket evidence. Inherited validator synthetic findings stay
disclosed; the package remains an applied candidate.

Refs: #139, #134; current-source restoration and source semantics.
