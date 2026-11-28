# core-skill-md Change Ledger

## CR-20261118-001 - 原审批证明与明确范围收尾

| Date | Change ID | Section | Change Type | Summary | Status |
|---|---|---|---|---|---|
| 2026-11-18 | CR-20261118-001 | 覆盖与收尾指针 | fixed | 具体用例分支显式绑定范围，旧分支走原关闭入口 | applied |

- Section changed: 原覆盖与范围收尾工作流。
- Before: 合法旧覆盖缺归属，局部反馈保留旧审批后全批版本门拒绝。
- After: 显式 case_ids 与原关闭入口指针；规划无具体稿继续保留。
- Why: REQ-020 / AC-026—028，具体反馈与历史原审批契约。
- Impact: 仅 canonical 与分发镜像，无全局安装或真实业务写入。
- Validation: 同树公开回归、镜像/AST/静态及 require-change-records；准确结果见 detail。
- Detail record: [CR-20261118-001](../entries/2026/2026-11/CR-20261118-001-scope-closure-review-reuse.md)。

- [CR-20261115-006](../entries/2026/2026-11/CR-20261115-006-shared-feedback.md): exact shared-source impact in existing feedback review.

## Purpose

Trace rule Q&A changes in core-skill-md.

## Outline

| Date | Change ID | Section | Change Type | Summary | Status |
|---|---|---|---|---|---|
| 2026-11-17 | CR-20261117-114 | 专业生成入口 | fixed | 先解释材料再构建候选及覆盖 | applied |
| 2026-11-11 | CR-20261111-105 | Rule clarification | changed | Persist complete dialogue | applied |
| 2026-11-11 | CR-20261111-201 | Source semantics | fixed | Goal-bounded authoring and retained constraints | applied |
| 2026-11-11 | CR-20261111-106 | Partial answers | fixed | Retain remaining aspects and dependencies | applied |

| 2026-11-11 | CR-20261111-202 | Aggregation and review repair | fixed | Preserve preparation and answer state | applied |
| 2026-11-11 | CR-20261111-107 | Report intake | changed | Read before asking; retain full P0 checker | applied |

| 2026-11-17 | CR-20261117-101 | Named scalar data | fixed | Lossless display and feedback | applied |

## Detailed Records

### CR-20261117-114 - 专业生成入口

- Section changed: 生成、扩展、反馈、恢复及交付入口。
- Before: 专业规则分散，结构完成容易被当作解释完成。
- After: 入口直接读取专业生成核对，按来源形成逐例目标与关联后生成。
- Why: REQ-007/008/009/012/016/017/018/022。
- Impact: 编写指引；候选schema及执行门槛不变。
- Validation: 公开结构保留检查与Skill静态检查；独立实际生成语义评审待后续。
- Detail record: [CR-20261117-114](../entries/2026/2026-11/CR-20261117-114-professional-generation.md)。

### CR-20261111-105 - Rule Q&A

- Section changed: rule clarification.
- Before: pure state and English labels.
- After: single Markdown event source and Chinese full questions.
- Why: issue 105 answer traceability.
- Impact: existing computation seams preserved.
- Validation: public regression; observed formal/provisional/deferred simulations and independent local integration review completed. Inherited validator findings remain open; no host acceptance.
- Detail record: [CR-20261111-105](../entries/2026/2026-11/CR-20261111-105-rule-qa.md).

### CR-20261111-106 - Partial answers

- Section changed: partial replies and dependencies.
- Before: any reply closed a question.
- After: accumulated aspects and explicit unknown disposition; dependent reopening.
- Why: issue 106.
- Impact: same public Markdown adapter and three business routes.
- Validation: public red-green regressions; actual 16-event dialogue and independent ticket review completed; 114 integrated regressions passed. Inherited validator findings remain.
- Detail record: [CR-20261111-106](../entries/2026/2026-11/CR-20261111-106-partial-answers.md).

### CR-20261111-201 - Source semantics

- Section changed: source interpretation and technical handoff.
- Before: generic source comparison; separate technical handoff dropped by conversion.
- After: explicit authoring checks and candidate-only technical constraints.
- Why: wrong data ownership cannot be repaired by rendering.
- Impact: existing candidate and presentation contracts; no business execution.
- Validation: 97 candidate tests passed; actual multi-turn correction and exact-version public review completed for three simulated cases. Historical missed questions and orchestration failures retained; no host acceptance.
- Detail record: [CR-20261111-201](../entries/2026/2026-11/CR-20261111-201-source-semantics.md).

### CR-20261111-202 - Aggregation
- Section changed: rendering and feedback projection.
- Before: repeated per-case trees.
- After: semantic paths and shared preparation with source ownership.
- Why: keep bulk reviews readable without changing execution meaning.
- Impact: batch, scoped and feedback public interfaces.
- Validation: 99 public regressions passed; actual XMind r1 import and complete 127-topic comparison passed. Limited independent re-review closed R1/R2/S1; actual repair-client 110/110 full-tree comparison passed. The 106-test run passed 105, then all 3 affected tests passed after assertion correction; inherited validator findings remain.
- Detail record: [CR-20261111-202](../entries/2026/2026-11/CR-20261111-202-aggregation.md).

PRE-02 review repair: answered/non-stale questions are historical, explicit empty-preparation notes stay in their group. Public regression and affected client sample are recorded in CR-20261111-202.

### CR-20261111-203 - Chinese identity
- Section changed: public presentation and feedback.
- Before: visible English IDs supplied feedback identity.
- After: Chinese business names and explicitly clarified internal return bindings.
- Why: rename and same-name cases must preserve stable records.
- Impact: ordinary/scoped views, Markdown and supported native returns.
- Validation: public TDD and feedback regressions; independent dialogue/client validation pending.
- Detail record: [CR-20261111-203](../entries/2026/2026-11/CR-20261111-203-presentation-identity.md).
### CR-20261111-107 - Report reconciliation

- Section changed: P0 report intake and sole task record.
- Before: no file intake or report-context record entry.
- After: authorized report and attachment reads, readable gaps, existing target reuse, additive MD context/notes.
- Why: issue 107.
- Impact: existing P0 checker and rule transitions preserved.
- Validation: public tests; actual two-round dialogue and independent ticket review completed; 114 integrated regressions passed. Inherited validator findings remain.
- Detail record: [CR-20261111-107](../entries/2026/2026-11/CR-20261111-107-report-reconciliation.md).

### CR-20261111-108 - coverage-review

- Section changed: coverage, scope and persisted discovery.
- Before: registered-question closure and display-limited approval.
- After: original-source review and preserved full approval.
- Why: Issue 108 source omission and range requirements.
- Impact: same MD and existing workflow boundaries.
- Validation: public TDD regressions; actual dialogue pending.
- Detail record: [CR-20261111-108](../entries/2026/2026-11/CR-20261111-108-coverage-review.md)

### CR-20261111-109 - Feedback clarification

- Section changed: persisted feedback entry and focused rule follow-up.
- Before: pure feedback and rebuilt questions.
- After: same-record proposals, partial replies, targeted reopening and exact-version review.
- Why: preserve actual answers and approval scope.
- Impact: candidate feedback only; no execution or merge.
- Validation: 116 public-interface regressions passed; natural simulation pending.
- Detail record: [CR-20261111-109](../entries/2026/2026-11/CR-20261111-109-feedback-clarification.md).

2026-11-12 repair follow-up: CR-20261111-203 / CR-20261111-108 / CR-20261111-109 retain prior evidence and add typed-reference, explicit impact disposition, atomic conflict and feedback-discovery corrections. Candidate review remains pending; see each detail record.

## 2026-11-12 local integration evidence

Frozen candidate 6679a11172b35a2810d6fe419390f5a0d76021f3 fast-forwarded from ef5d4b4 under Root authorization. This follow-up changes evidence records only.

CR-20261111-203/109 actual-path evidence and independent repair review are complete; CR-20261111-108 remains pending_behavior_validation. See detail records.

Independent re-review closed three P1 findings and the composition issue; six focused tests passed. Reuse 129 full tests before the optional-metadata fix and 24 affected tests afterward, without repeating unchanged suites. Private actual/review evidence stays outside the package; historical versions/failures remain. Seven inherited scanner findings (3 P0 / 3 P1 / 1 P2) remain, not a clean scan. No publishing, Issue closure, installation or business execution.

## CR-20261111-204 - Requested chat delivery

- Section changed: canonical output and same-version chat projection.
- Before: persistent human-view files and automatic P0 chat display.
- After: XMind scope by default; explicit 1–9 complete cases in chat.
- Why: approved PRE-04 delivery and semantic-preservation requirements.
- Impact: authoring, scope, dependency and extension regeneration; source retained.
- Validation: public red/green and affected regressions; natural actor pending.
- Detail record: [CR-20261111-204-chat-delivery.md](../entries/2026/2026-11/CR-20261111-204-chat-delivery.md).
### 2026-11-12 CR-20261111-108 actual repair dialogue completed

Fresh actual synthetic dialogue completed 21 events and 21 successful readback checks; exact version 882c4c8fdb0748fd7aa7bcab3c161aa3e4ccbe70d851f9ce3617a30a3bd2fab5 approves only MEMO-001, formal/not_run/not_merged. This supersedes the earlier pending_behavior_validation entry for that sample and releases #110 under Root authorization. Old failed/rejected versions remain historical. No complete approved P0 baseline or XMind client import exists for this sample; earlier public P0-scope regressions are separate evidence. See CR-20261111-108 detail for boundaries. Product code unchanged; inherited seven scanner findings remain.

## CR-20261111-110 - Cross-stage recovery

- Section changed: same task recovery and stage transition.
- Before: no actual candidate/source recovery comparison.
- After: same-MD checkpoint/readback, scoped difference diagnostics and existing P0-gated extension transition.
- Why: fresh contexts need actual materials and traceable decisions.
- Impact: candidate authoring only; prior stages and approvals preserved.
- Validation: 5 new / 135 full public regressions pass; actual conversation and independent review pending.
- Detail record: [CR-20261111-110](../entries/2026/2026-11/CR-20261111-110-cross-stage-recovery.md).


### CR-20261111-110 actual combined acceptance completed - 2026-11-12

The agreed synthetic behavior acceptance is now complete on reviewed product
6d6c88e49e194967b87a7d11020db313c70bf7c8: independent Spec review passed all
10 issue-110 ACs with zero new findings. This supersedes prior pending behavior
and review statements for this bounded simulation; historical entries remain.
The sole Q&A has 58 events and 15 unique answer anchors. Public read_record and
resume_record independently confirm full candidate equality, unchanged Q&A bytes
and no final recovery conflicts. Final exact version
3fec851c420c882f88d46bca7d3e77e15c31d62c76484cd623f19ae05cc0a591 has two
approved/not_run/not_merged synthetic cases. Candidate status remains applied;
this is not host acceptance, execution readiness, installation or publishing.
See CR110 detail and external evidence/qa110/final-review/acceptance.md and
final-inspection.json under the local task evidence root, outside this repository.

## CR-20261114-001 — Module handoff partition

- Section changed: review projection and feedback.
- Before: hidden provenance and repeated process metadata.
- After: direct-owner module instruction branches; business applicability remains visible.
- Why: #113 / REQ-015-016 / AC-023-024.
- Impact: scoped, ordinary and chat views; supported markdown/native feedback.
- Validation: public red/green; 149 synthetic regressions passed; real client unverified.
- Detail record: [CR-20261114-001](../entries/2026/2026-11/CR-20261114-001-module-handoff.md).


### CR-20261114-002 - Review expression

- Section changed: graded review titles and repeated expectations.
- Before: ungraded titles and repeated expected/check text.
- After: one-space graded titles, exact deduplication, stable source feedback.
- Why: issue 114.
- Impact: same-version total/scoped/chat views.
- Validation: public-entry TDD and regression; external test-output/rr02.
- Detail record: [CR-20261114-002](../entries/2026/2026-11/CR-20261114-002-review-expression.md)
## CR-20261115-003 — Whole-step P0 reuse

- Section changed: static P1/P2 authoring, dependency snapshots, review and isolated merge.
- Before: every step required duplicated complete fields.
- After: assessed complete source designs may become version-bound whole-step references; one resolver verifies order, fixed data and endpoint.
- Why: #115 / AC-026 and AC-028.
- Impact: existing complete candidates remain valid; execution dependencies and permissions unchanged.
- Validation: public authoring, difference, corruption, review, feedback, selection and merge tests; client acceptance remains unverified.
- Detail record: ../entries/2026/2026-11/CR-20261115-003-step-reuse.md
### CR-20261115-005 - Local referenced-step feedback

- Section changed: candidate feedback and reference projection.
- Before: inherited actions could not accept local scalar feedback.
- After: chat, Markdown and native feedback materialize only the changed local step.
- Why: #117 / AC-030.
- Impact: source snapshots and unrelated cases remain unchanged; existing review gates apply.
- Validation: 162 tests passed; external test-output/rr05/tests.txt; actual client not tested.
- Detail record: entries/2026/2026-11/CR-20261115-005-local-feedback.md

## CR-20261116-005 - Business hierarchy

- Section changed: core-skill-md.
- Before: only module hierarchy projected.
- After: explicit source-assessed groups retain case identity and scoped omissions.
- Why: TAS-05 AC-008/022/024.
- Impact: public projections and feedback; no business execution.
- Validation: 21 targeted public tests passed; final checks in detail/external completion.
- Detail record: [CR-20261116-005](../entries/2026/2026-11/CR-20261116-005-business-hierarchy.md).


### CR-20261116-009 - Ordered whole-case references

- Section changed: dependency authoring
- Before: P0-only special placement.
- After: actual ordered whole reference with endpoint and source checks.
- Why: TAS-09 AC-016/021.
- Impact: local dependency review, source preserved.
- Validation: 31 public regression tests passed; actual interaction unverified.
- Detail record: [CR-20261116-009](../entries/2026/2026-11/CR-20261116-009-whole-case-references.md)

## CR-20261116-003 - Shared stage adapter

| Date | Change ID | Section | Change Type | Summary | Status |
| --- | --- | --- | --- | --- | --- |
| 2026-11-16 | CR-20261116-003 | core-skill-md | changed | Shared dialogue and distinct continuation | applied |

- Section changed: TCA stage routing and linked public-entry instructions.
- Before: duplicated parent dialogue and automatic application after summary agreement.
- After: host-resolved test-grill-me interaction; confirm-only note waits; explicit continuation applies existing API.
- Why: TAS-03 and parent AC-001/002/003/004/006/024/025.
- Impact: existing candidate and sole MD authority; no production API or execution-layer change.
- Validation: 34 targeted public tests passed; actual changed-route dialogue and client unverified.
- Detail record: [CR-20261116-003](../entries/2026/2026-11/CR-20261116-003-stage-adapter.md).


### CR-20261116-007 - Reviewed preparation scope

- Section changed: preparation applicability and generated scope.
- Before: automatic semantic extraction.
- After: reviewed full-group scope and conservative invalidation.
- Why: TAS-07 AC-011/012/013/021.
- Impact: source-bound rendering and feedback; no execution.
- Validation: public regression and synthetic scope checks; candidate only.
- Detail record: [CR-20261116-007](../entries/2026/2026-11/CR-20261116-007-preparation-scope.md).

### CR-20261116-004 - scoped-recovery-closure

- Section changed: Recovery and scoped closure
- Before: Upgrade recovery/cleanup gap
- After: Actual-file recovery, permanent basis before bounded cleanup
- Why: TAS-04 AC-007/026/027/028
- Impact: Isolated candidate only; existing authority retained
- Validation: Public API tests passed; dialogue pending
- Detail record: [CR-004](../entries/2026/2026-11/CR-20261116-004-scoped-recovery-closure.md)

### CR-20261116-011 - current-source restoration

- Section changed: integrated review/recovery and package distribution.
- Before: eager whole-catalog failure and partial source restoration.
- After: case-local blockers, actual-source approval and selective persisted artifacts.
- Why: TAS-11 AC-019 through AC-022.
- Impact: preserved candidate identity, whole P0 gate and project-only mirror.
- Validation: see evidence/tas-11 final report; candidate only.
- Detail record: [CR-20261116-011](../entries/2026/2026-11/CR-20261116-011-current-source-restoration.md).

### CR-20261116-013 - Final review repairs

- Section changed: applicable candidate scope, display, restoration and native return contracts.
- Before: ancestor scope and nested references rejected; governance remained in business prose; native generated link rejected.
- After: explicit source-bound adaptation with conservative failure handling.
- Why: confirmed final Spec findings and actual client baseline.
- Impact: package and identical repository mirror only.
- Validation: public red-green and final checks; actual-client acceptance separate.
- Detail record: [CR-20261116-013](../entries/2026/2026-11/CR-20261116-013-final-review-repairs.md).

### CR-20261117-102 - Module common preconditions

- Section changed: common preparation definition, projection, feedback and restoration.
- Before: whole-list group-scoped extraction and per-case common references.
- After: module-direct definitions, per-item versioned scope, visible pending content and exact feedback origins.
- Why: #136, AC-030/031/032 preconditions and AC-033 lifecycle.
- Impact: canonical and mirror only; no execution or new authority.
- Validation: public TDD, save/read and frozen legacy feedback; see detail.
- Detail record: [CR-20261117-102](../entries/2026/2026-11/CR-20261117-102-common-preconditions.md).

### CR-20261117-101 - Named scalar data

- Section changed: core-skill-md
- Before: object/value split; one-leaf feedback.
- After: named scalar projection with bound compound feedback and legacy compatibility.
- Why: #135 AC-029 and AC-034 data portion.
- Impact: original identities and candidate data retained.
- Validation: eight public tests; external evidence/tco-01/result.md.
- Detail record: [CR-20261117-101](../entries/2026/2026-11/CR-20261117-101-simple-data.md).

### CR-20261117-105 - Goal/preparation ownership

- Section changed: authoring purpose guidance and preservation tests.
- Before: mixed preparation could retain an unrelated independent check.
- After: source/goal/consumer assessment, existing-goal lookup and current-value preservation.
- Why: TCO-05 / AC-033.
- Impact: steps-only guidance and public test coverage, no classifier or execution change.
- Validation: ticket evidence; actual authoring and public tests distinguished.
- Detail record: [CR-20261117-105](../entries/2026/2026-11/CR-20261117-105-goal-preparation.md).

### CR-20261117-103 - Common postconditions

- Section changed: directional post operation contract and consumers.
- Before: post fields dropped or unrecognized.
- After: source-bound module definitions, complete sequence and legacy absence.
- Why: #137 acceptance.
- Impact: generation, scope, render, feedback, saved recovery.
- Validation: public red/green tests and required repository checks in external evidence/tco-03.
- Detail record: [CR-20261117-103](../entries/2026/2026-11/CR-20261117-103-common-postconditions.md)

### CR-20261117-104 - Scope lifecycle

- Section changed: common operation scope lifecycle.
- Before: subset and changed member invalidation could hide valid operations.
- After: explicit reviewed module scope, actual parent checks and local per-item membership.
- Why: #138 full acceptance criteria.
- Impact: render, save and restoration; no business execution.
- Validation: public lifecycle tests and repository checks; candidate status.
- Detail record: [CR-20261117-104](../entries/2026/2026-11/CR-20261117-104-scope-lifecycle.md).

### CR-20261117-106 - feedback-loop

- Section changed: current feedback and recovery contract.
- Before: partial probes lost full source; shared ordinals and numeric values rejected edits.
- After: actual-parent context, full shared impact, typed edits and legacy signature reuse.
- Why: #140 and confirmed early findings.
- Impact: candidate only; hidden parent protected.
- Validation: public red/green and final repository checks, external tco-06 evidence.
- Detail record: [CR-20261117-106](../entries/2026/2026-11/CR-20261117-106-feedback-loop.md).
## CR-20261119-149 Write formal Human View from validated input

| Date | Change ID | Section | Change Type | Summary | Status |
| --- | --- | --- | --- | --- | --- |
| 2026-11-19 | CR-20261119-149 | Write formal Human View from validated input | changed | Local implementation and regression | applied |

[Detail](../entries/2026/2026-11/CR-20261119-149-formal-human-view.md)

## CR-20261119-153

| Date | Change ID | Section | Change Type | Summary | Status |
| --- | --- | --- | --- | --- | --- |
| 2026-11-19 | CR-20261119-153 | Use the incremental layout from the standard extension entry | changed | Integrated contract verification | applied |

[Detail](../entries/2026/2026-11/CR-20261119-153-integration-review-layout.md)

## CR-20261128-175

批量评审及点名执行单例的编写入口。[变更记录](../entries/2026/2026-11/CR-20261128-175-review-and-case-handoff.md)

## CR-20261128-184

两种读者与常规交付入口。[详细记录](../entries/2026/2026-11/CR-20261128-184-reader-views.md)
