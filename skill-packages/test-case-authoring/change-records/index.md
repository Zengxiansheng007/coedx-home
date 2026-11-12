# Change records

## Latest Changes

- 2026-11-12 CR-20261111-110 repair: prior-stage question IDs are reserved at feedback admission while current-stage answer history remains valid. Public red/green, 7 recovery and 137 full tests pass; actual QA108/109 replay remains compatible. Inherited seven scanner findings remain; independent repair review and combined actual behavior are pending. See [repair detail](entries/2026/2026-11/CR-20261111-110-cross-stage-recovery.md).

- CR-20261111-203: [Chinese identity](entries/2026/2026-11/CR-20261111-203-presentation-identity.md), applied; client and actual dialogue validation pending.

- CR-20261111-107: [Report reconciliation](entries/2026/2026-11/CR-20261111-107-report-reconciliation.md), applied; actual two-round report reconciliation and independent ticket review completed; 114 integrated regressions passed.


- CR-20261111-106: [Partial answers](entries/2026/2026-11/CR-20261111-106-partial-answers.md), applied; actual 16-event dialogue and independent ticket review completed; 114 integrated regressions passed.

- CR-20261111-105: [Rule Q&A](entries/2026/2026-11/CR-20261111-105-rule-qa.md), applied; three-route actual simulation and independent local integration review completed; inherited validator findings retained.
- CR-20261111-201: [Source semantics](entries/2026/2026-11/CR-20261111-201-source-semantics.md), applied; actual correction dialogue and exact-version simulated public review completed.

- CR-20261111-202: [Semantic aggregation](entries/2026/2026-11/CR-20261111-202-aggregation.md), applied; R1/R2/S1 closed by limited independent re-review; actual repair-client 110/110 full-tree comparison passed.

## Category Index

- CR-20261111-109: [Feedback clarification](entries/2026/2026-11/CR-20261111-109-feedback-clarification.md), applied; public-interface regressions complete, natural simulation and independent review pending.

- [core-skill-md](categories/core-skill-md.md)
- [references-and-assets](categories/references-and-assets.md)
- [scripts-and-validation](categories/scripts-and-validation.md)
- [safety-and-governance](categories/safety-and-governance.md)
- [downstream-and-handoff](categories/downstream-and-handoff.md)

## Open Risks

Inherited structural-validator findings remain open; applied is not host acceptance.
Cross-stage append belongs to issue 110. Historical simulation corrections remain recorded.
No installation or execution acceptance.

PRE-02 original client r1 evidence remains intact; this repair changes pending-question and explicit-preparation display. Preserve its separate affected-client evidence.

## CR-20261111-108 - Coverage review

- Status: applied; independent dialogue pending.
- Detail: [source coverage](entries/2026/2026-11/CR-20261111-108-coverage-review.md)

2026-11-12 repair follow-up: CR-20261111-203 / CR-20261111-108 / CR-20261111-109 retain prior evidence and add typed-reference, explicit impact disposition, atomic conflict and feedback-discovery corrections. Candidate review remains pending; see each detail record.

## 2026-11-12 local integration evidence

Frozen candidate 6679a11172b35a2810d6fe419390f5a0d76021f3 fast-forwarded from ef5d4b4 under Root authorization. This follow-up changes evidence records only.

CR-20261111-203 and CR-20261111-109: actual paths, compatibility and independent repair review passed. CR-20261111-108: repaired code and independent review passed; pending_behavior_validation. PRE04 may start; 110 still waits for 108 actual behavior.

Independent re-review closed three P1 findings and the composition issue; six focused tests passed. Reuse 129 full tests before the optional-metadata fix and 24 affected tests afterward, without repeating unchanged suites. Private actual/review evidence stays outside the package; historical versions/failures remain. Seven inherited scanner findings (3 P0 / 3 P1 / 1 P2) remain, not a clean scan. No publishing, Issue closure, installation or business execution.

## CR-20261111-204 - Requested chat delivery

- Section changed: canonical output and same-version chat projection.
- Before: persistent human-view files and automatic P0 chat display.
- After: XMind scope by default; explicit 1–9 complete cases in chat.
- Why: approved PRE-04 delivery and semantic-preservation requirements.
- Impact: authoring, scope, dependency and extension regeneration; source retained.
- Validation: public red/green and affected regressions; natural actor pending.
- Detail record: [CR-20261111-204-chat-delivery.md](entries/2026/2026-11/CR-20261111-204-chat-delivery.md).
### 2026-11-12 CR-20261111-108 actual repair dialogue completed

Fresh actual synthetic dialogue completed 21 events and 21 successful readback checks; exact version 882c4c8fdb0748fd7aa7bcab3c161aa3e4ccbe70d851f9ce3617a30a3bd2fab5 approves only MEMO-001, formal/not_run/not_merged. This supersedes the earlier pending_behavior_validation entry for that sample and releases #110 under Root authorization. Old failed/rejected versions remain historical. No complete approved P0 baseline or XMind client import exists for this sample; earlier public P0-scope regressions are separate evidence. See CR-20261111-108 detail for boundaries. Product code unchanged; inherited seven scanner findings remain.

### CR-20261111-204 review repair — 2026-11-12

Separate actual Markdown table blocks and project effective business rules without audit/history duplication. Preserve provisional/product/deferred meaning and all source history. 136 public regressions passed; independent MarkdownIt probe reports two tables and actual candidate 34 lines with no machine paths. Natural continuation and independent re-review remain Root-owned; see CR-20261111-204 detail.


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
## CR-20261111-110 - Cross-stage recovery

- Section changed: same task recovery and stage transition.
- Before: no actual candidate/source recovery comparison.
- After: same-MD checkpoint/readback, scoped difference diagnostics and existing P0-gated extension transition.
- Why: fresh contexts need actual materials and traceable decisions.
- Impact: candidate authoring only; prior stages and approvals preserved.
- Validation: 5 new / 135 full public regressions pass; actual conversation and independent review pending.
- Detail record: [CR-20261111-110](entries/2026/2026-11/CR-20261111-110-cross-stage-recovery.md).


### CR-20261111-204 / CR-20261111-110 final pair integration

PRE04 actual synthetic dialogue/capacity and all independent repair findings are accepted within the detail-record limits. Issue 110 F-110-01 is independently resolved; whole-ticket combined behavior remains pending. Sources: aff05e6d4bff711948887c40c63152a251b70449 and bbea7c9351c85a3057cba4de0568411c090ac5bf. Old evidence and inherited seven scanner findings remain. See both detail records for precise scope.


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
