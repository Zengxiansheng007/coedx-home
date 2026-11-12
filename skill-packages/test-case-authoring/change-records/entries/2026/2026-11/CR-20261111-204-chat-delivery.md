# CR-20261111-204 - Requested chat delivery

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | changed |
| Scope | core-skill-md, references-and-assets, scripts-and-validation |
| Source | Approved PRE-04 presentation ticket |
| Baseline | fe5f1727f166fd8252c751f871780e281ff9582d |
| Author | Codex |
| Related Records | CR-20261111-201, CR-20261111-202, CR-20261111-203 |

## Summary
Keep persisted XMind review copies and candidate records; show requested 1–9
complete human-view cases directly in chat without creating a human-view file.

## Context And Problem
Authoring, scoped review and dependency CLI entries still wrote human-view MD.
P0 instructions also required automatic complete chat output. Selecting a subset
could resolve references against historical titles rather than current full source.

## Sections Changed
| File | Section | Change Summary |
|---|---|---|
| SKILL.md and chat-delivery contract | Initial and regenerated delivery | Scope default and requested 1–9 display |
| presentation.py and extension.py | Public projection | Explicit bounded selection, same-version complete cases |
| authoring.py, scoped_review.py, dependencies.py | CLI artifacts | Remove human-view file writes |
| scoped_review.py | Typed reference projection | Full source context in every business group |
| Existing CLI tests and test_chat_delivery.py | Public seams | File outputs, selection, immutability, feedback and references |

## Decision And Alternatives
Reuse existing pure rendering, candidate versions, stable identities and review
workflow. Retain full pure views for semantic comparison; use render_chat only for
chat delivery. Reject unknown/duplicate/over-nine requests instead of guessing,
truncating or pagination. No new dependency or second business source.

## Detailed Change
P0, scope and dependencies persist candidate/XMind and necessary technical records.
Extension keeps the legacy single-case call and adds explicit multi-case selection.
Main workflow links the delivery contract at every affected presentation stage.
Existing historical files are retained; overwrite rejection remains in place.

## Impact Analysis
AC-016 covers file output and actual chosen complete cases; AC-017 covers quiet batch
delivery and no automatic chunks; AC-021 covers same-version semantics and feedback.
Display selection never changes catalog contents, functional test scope or approval.
No real catalog, global installation, UI-Test execution or external publication.

## Validation Evidence
| Check | Method | Result | Evidence |
|---|---|---|---|
| TDD | Missing public selector, authoring/scope/dependency file assertions | Each failed before its implementation; targeted checks then passed | Private PRE04 tool evidence |
| Selected reference semantics | Current linked title through step extension | Failed with stale baseline title, passed with full-source reference context | test_chat_delivery |
| Affected combination | Authoring, handwritten, scoped, dependency, extension, chat | 39 tests passed before additional reference/extension slices | Private PRE04 evidence |
| Final regression and validator | Public discovery and require-change-records | 134 tests passed; validator retains exactly seven inherited findings (3 P0 / 3 P1 / 1 P2), rejected, not clean | Private PRE04 evidence |
| Natural behavior | Fresh actor scheduled by Root | Pending; no scripted transcript substitutes for actual dialogue | Host-owned evidence |

## Safety And Privacy
Synthetic inputs only. No external model, install, push, real business execution or
source requirement publication. Private evidence stays outside this package.

## Risks And Follow-up
Root owns actual natural simulation and independent review. Local public APIs cannot
enforce arbitrary callers' file writes; policy and canonical CLI paths are bounded.
Do not claim XMind client compatibility or business success from these tests.

## Independent review repair (2026-11-12)

Baseline 294a12a69b72cc42af68255a64caafb75a0bfa98; integration 47e84fbd merged as 4a1f2bc. REQ-010/012/014: repair distinct Markdown table blocks and replace generic rule-audit flattening with effective business projection. Historical failed output and actual dialogue remain unchanged. Public signatures, candidate version and approval gates are unchanged. authoring.render_batch now uses the same complete projection as chat and XMind, including unresolved question reasons.

TDD: public table blocks failed 0 versus 2; public post-apply rules failed 3 repeated interpretations versus 1. Both passed after repair. Full public suite: 136 passed, including feedback/native XMind and independent-rule regressions. No new dependency: persistent tests use stdlib; installed MarkdownIt independently parsed two tables. Unmodified actual post-QA candidate now renders 34 lines, first table line 31, zero qa-ref/update-path lines (previous independent probe: 178/172/9/36). Business unknown empty-title scope, repeat-title validity, no result reuse and pause/no-cleanup remain visible.

Root still owns fresh behavior continuation and independent re-review; no whole-ticket acceptance or client-import claim. Older exported files containing the superseded audit layout are retained; structural return handling remains fail-closed and requires explicit chat interpretation rather than silently accepting obsolete layout.


### CR-20261111-204 legacy feedback compatibility repair - 2026-11-12

Baseline fccf2bc48ce747830665463ee6191a7584a3fb14. Preserve the known pre-repair
rule-audit projection only inside exact-baseline feedback mapping. Normal display
keeps effective business rules and clean Markdown blocks. Historical pending
question suffixes are reconstructed together with that layout. Both render
probes use the selected layout; protected rule arrays never become writable leaves.

This supersedes the earlier limitation requiring chat reinterpretation of known
old exported layouts: those exact layouts now accept supported scalar changes.
Unknown topology, audit edits, unbound/stale identities and conflicting shared
data still fail closed. Existing returned files and baseline/history stay intact.

Public old-emitter/new-consumer red test reproduced the structural rejection;
139 public regressions then passed (34.525s). Frozen 294a12a synthetic fixture
covers shared data, audit arrays and old pending-question rows. Old and current
native adapter fixtures both accept the exact operation proposal, retaining the
native bytes; this is format acceptance, not XMind client acceptance. Independent
review's retained old candidate/Markdown now produce exactly the same one-field
proposal as the old consumer, with input bytes unchanged. No MarkdownIt import
or new dependency was added. Root owns natural dialogue and independent re-review.

Changed resources: feedback.py, scoped_review.py, test_legacy_feedback.py,
assets/fixtures/legacy-review-294a12a.json and its provenance note, plus
references/feedback-contract.md. All are mirrored byte-for-byte. Synthetic
fixtures contain no private source documents, live credentials or business data.
Private evidence: compat-red-product.txt, compat-suite.txt,
compat-review-result.json and compat-validation.txt under the existing PRE04
evidence directory. The first test launch had a module-resolution error because
the governed runner sets the worktree root; its log is preserved separately.
Validation remains candidate-only; seven inherited scanner findings are retained.
No global install, real business execution, remote publication or #110 changes.


## Local integration actual evidence - 2026-11-12

Frozen source aff05e6d4bff711948887c40c63152a251b70449 passed independent
compatibility re-review: all three PRE04 findings resolved; exact old-artifact
scalar operation accepted, input hashes/history unchanged, unbound/audit/topology
variants rejected. Three targeted legacy/native-format regressions passed.

Root's observed synthetic dialogue recovered the sole MD, displayed the actual
render_chat result and approved only exact version
e16e9c0f04fa31adeabfca3dfe8db0f102a5fddabc1dd6b131efd34bcf96e110.
Readback equals the saved candidate: approved/formal/not_merged/not_run;
the old version remains pending. Structural rename/two-step editing used the
public authoring clarification route; direct P0 prepare_feedback was not tested.

Separate actual capacity interaction retained all 12 cases, requested explicit
selection after the over-nine request, then displayed nine complete selected
cases once. Unselected case 12's reference remains; capacity cases stay
unapproved. Original catalog cases/data match the frozen baseline. No human-view
file was created. Evidence remains outside the public package in PRE04 actual
recovery-observations.md and quantitative-evidence.json, plus review-pre04.md.

This supersedes earlier natural-dialogue pending statements for these samples.
PRE04 is locally accepted in this bounded simulated scope under Root release.
No new XMind client import, business execution, global install or publication
is claimed. Inherited seven validator findings and all old failures remain.


### CR-20261111-204 / STD-01 final Standards annotation repair (2026-11-12)

Baseline: c3eeef7135460d89b7d118e87ec3251e4f9f9625. The final two-axis review
reported zero new Spec findings and one P3 Standards finding (STD-01).
Added concise right-side explanations in aggregation.py for preparation-sharing
semantics/shape, source ownership and omitted-case block bounds, and in feedback.py
for raw-to-normalized identity evidence. No executable behavior, signatures,
fixtures, QA records or historic evidence changed. This is a minimal-change
annotation repair within CR-204; candidate status stays applied.

Validation: both changed Python files have identical ASTs excluding positional
attributes and identical (type, string) token streams after CRLF/LF normalization,
excluding comments and position/source-line metadata. The initial token comparison
reported only Git LF versus checkout CRLF newline tokens; ASTs and token counts
already matched. The corrected verifier keeps every executable token unchanged.
Source/package byte identity and git diff --check
were checked. Root's seven passed checks on the baseline, including 146 authoring
tests, are reused; no new tests or full-suite rerun are warranted by equivalent
executable content. Only comments and this traceability note were added; manual
diff review found no credentials or private business data. Seven inherited scanner
findings and the separately requested host-promotion gate-contract finding remain;
no scanner/host acceptance is claimed. Issue 110 actual behavior acceptance remains
Root-owned and is not inferred from this repair. External evidence:
evidence/final-comments-equivalence.json and evidence/final-review-fix-handoff.md.
