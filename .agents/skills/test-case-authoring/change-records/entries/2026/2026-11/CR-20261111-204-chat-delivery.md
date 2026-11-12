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
