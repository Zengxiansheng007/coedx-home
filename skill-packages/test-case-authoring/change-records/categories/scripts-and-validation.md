# scripts-and-validation Change Ledger

## CR-20261119-145

| Date | Change ID | Section | Change Type | Summary | Status |
| --- | --- | --- | --- | --- | --- |
| 2026-11-19 | CR-20261119-145 | 原生回传 | changed | 基于版本的文件定位和问答记录恢复 | applied |

[变更详情](../entries/2026/2026-11/CR-20261119-145-native-feedback.md)

## CR-20261119-143

| Date | Change ID | Section | Change Type | Summary | Status |
| --- | --- | --- | --- | --- | --- |
| 2026-11-19 | CR-20261119-143 | 增量出稿与 Markdown 回传 | added | 版本化布局、稳定编号及明确的回传边界 | applied |

[变更详情](../entries/2026/2026-11/CR-20261119-143-incremental-review.md)

## CR-20261118-002 - 复核当前来源与收尾保存边界

| Date | Change ID | Section | Change Type | Summary | Status |
|---|---|---|---|---|---|
| 2026-11-18 | CR-20261118-002 | qa_record / closure regression | fixed | 复用当前还原，并为永久写入和临时清理绑定核对时的字节 | applied |

新公开入口回归覆盖有效来源、相关和无关漂移、来源缺失、候选变化，以及合法问题在永久写入前后插入。既有测试保留。证据见 [CR-20261118-002](../entries/2026/2026-11/CR-20261118-002-scope-closure-current-sources.md)。

## CR-20261118-001 - 原审批证明与明确范围收尾

| Date | Change ID | Section | Change Type | Summary | Status |
|---|---|---|---|---|---|
| 2026-11-18 | CR-20261118-001 | qa_record / public closure regressions | fixed | 原审批真实重建与完整依赖比较；明确范围保留原汇总 | applied |

- Section changed: close_record_scope 及私有证明辅助、新公开模拟回归。
- Before: 整批 content_version 唯一门拒绝合法保留审批；无补范围无副作用入口。
- After: 同 QA 原评审快照与完整业务/来源/适用/显示比较，显式有据范围绑定。
- Why: scope-closure-audit.md/json 与新公开两例 RED。
- Impact: 仅关闭 seam；原测试原样、canonical/mirror 同步；生成/MD mapper/性能不改。
- Validation: RED、真实文件 GREEN、最终受影响同树和静态；原探针设置错误保留。
- Detail record: [CR-20261118-001](../entries/2026/2026-11/CR-20261118-001-scope-closure-review-reuse.md)。

## CR-20261117-119 - 旧候选问题的准确历史索引

| Date | Change ID | Section | Change Type | Summary | Status |
|---|---|---|---|---|---|
| 2026-11-17 | CR-20261117-119 | scripts-and-validation | fixed | 复用非空id索引约定，旧建议保留且不给只读例外 | applied |

- Section changed：准确已应用历史索引及直接契约。
- Before：合法旧候选无id导致反馈KeyError。
- After：只索引非空id；完整相等、已答、已应用及typed范围门不变。
- Why：338整套两处继承错误及原单例RED。
- Impact：单行产品修复、公开mixed正反回归、镜像；不改旧fixture/CR118。
- Validation：最终受影响24项通过，静态/扫描证据见详细记录。
- Detail record：[CR-20261117-119](../entries/2026/2026-11/CR-20261117-119-legacy-question-index.md)。


## CR-20261117-118 - 历史技术定位与反馈目标分工

| Date | Change ID | Section | Change Type | Summary | Status |
|---|---|---|---|---|---|
| 2026-11-17 | CR-20261117-118 | scripts-and-validation | fixed | 准确已完成技术历史只读复用，本轮业务目标保持本例归属 | applied |

- Before：全部历史目标都作为当前业务写目标检查，合法技术历史阻断无编辑反馈。
- After：共享类型角色识别准确技术历史；新增、重开和实际答复仍拒绝跨例暗写。
- Why：合成公开QA与真实生成MD独立red。
- Impact：单一反馈适配器、直接引用、公开恢复正反例；无新schema或答案权威。
- Validation：定向、恢复及新进程结果见详细记录；历史失败保留。
- Detail record：[CR-20261117-118](../entries/2026/2026-11/CR-20261117-118-feedback-technical-history.md)。


## CR-20261117-117 - 有效规则解释的来源投影

| Date | Change ID | Section | Change Type | Summary | Status |
|---|---|---|---|---|---|
| 2026-11-17 | CR-20261117-117 | scripts-and-validation | fixed | 规则解释同源投影、原始缺失判断、同 QA 全链及直接生成来源要求 | applied |

- Before：规则正文绕过逐叶评估，治理解释仍混入业务规则。
- After：解释及条件用当前投影，原始身份/状态/缺失保持；生成解释与复用过程分工。
- Why：独立公开 API 复现与实际新稿缺陷。
- Impact：共享渲染、对应测试与直接引用；无新 schema 或权限变化。
- Validation：红→绿、同 QA 文件反馈及新进程恢复，见详细记录。
- Detail record：[CR-20261117-117](../entries/2026/2026-11/CR-20261117-117-rule-source-projection.md)。


## CR-20261117-116 - coverage 准确父源上下文

| Date | Change ID | Section | Change Type | Summary | Status |
|---|---|---|---|---|---|
| 2026-11-17 | CR-20261117-116 | scripts-and-validation | fixed | coverage 与首次生成/QA反馈/恢复采用同一准确父源，缺口及局部阻塞保持 | applied |

- Before：正文与 coverage 的还原上下文不同，已核归属误报 gap。
- After：传递调用方完整父源；QA 串联核对 partial/complete/gap，保留缺失、漂移和非法链接拒绝。
- Why：公开 API 与实际 QA 回放独立复现。
- Impact：extension 直接消费者与对应调用参考；无新 schema 或审批状态。
- Validation：行为红→绿及受影响公开回归，证据见详细记录。
- Detail record：[CR-20261117-116](../entries/2026/2026-11/CR-20261117-116-coverage-source-context.md)。


## CR-20261117-113 - QA 与业务投影生命周期

| Date | Change ID | Section | Change Type | Summary | Status |
|---|---|---|---|---|---|
| 2026-11-17 | CR-20261117-113 | scripts-and-validation | fixed | 同一 QA 两种评估动作、typed 源/值/身份、公共与本例归属、完整串联及新进程恢复 | applied |

- Before：纯评估无法回到唯一 QA；来源、审计和字面业务字段用途混淆，真实公共/特殊归属与空格回流有断点。
- After：同一 QA 两种评估动作、typed 源/值/身份、公共与本例归属、完整串联及新进程恢复；沿原候选/QA 保存，同版回放，业务批准与执行边界不升级。
- Why：RTA-02 真实失败与已确认 REQ/AC；共享 seam 经 Root 核准后基于 RTA-01 集成 tip 修改。
- Impact：仅本票包与镜像；原试用、原 P0、全局 Skill、业务执行及发布保持原边界。
- Validation：公开接口先红后绿、真实文件与子进程恢复；full01 失败保留，最终 full-final.txt 与结构扫描按 detail 记录，独立 P2 留给后续 fresh implementer。
- Detail record：[CR-20261117-113](../entries/2026/2026-11/CR-20261117-113-qa-projection-lifecycle.md)。

- [CR-20261115-007](../entries/2026/2026-11/CR-20261115-007-handoff-revalidation.md): checkpoint/resume current qualification, exact active closure and stale-decision regressions.

- [CR-20261115-006](../entries/2026/2026-11/CR-20261115-006-shared-feedback.md): exact shared-source impact in existing feedback review.

## Purpose

2026-11-12 CR-20261111-110 repair follow-up: qa_record feedback admission now rejects newly introduced prior-stage IDs before writing; current-stage same-ID questions retain answer versions. Public red/green, 7 recovery and 137 full tests pass; actual QA108/109 records remain unchanged and replay exactly. Seven inherited scanner findings remain. Independent repair review and combined actual behavior are pending; [detail](../entries/2026/2026-11/CR-20261111-110-cross-stage-recovery.md).

Trace rule Q&A changes in scripts-and-validation.

## Outline

| Date | Change ID | Section | Change Type | Summary | Status |
|---|---|---|---|---|---|
| 2026-11-17 | CR-20261117-114 | 专业输入结构保留 | validation | 独立方面缺项及逐例理由/准备边界公开检查 | applied |
| 2026-11-11 | CR-20261111-105 | Rule clarification | changed | Persist complete dialogue | applied |
| 2026-11-11 | CR-20261111-201 | Source semantics | fixed | Goal-bounded authoring and retained constraints | applied |
| 2026-11-11 | CR-20261111-106 | Partial answers | fixed | Retain remaining aspects and dependencies | applied |

| 2026-11-11 | CR-20261111-202 | Aggregation and review repair | fixed | Preserve preparation and answer state | applied |
| 2026-11-11 | CR-20261111-107 | Report intake | changed | Read before asking; retain full P0 checker | applied |

| 2026-11-17 | CR-20261117-017 | Agent notes lifecycle and display | fixed | Ready-owner cleanup, exact candidate binding and Chinese display | applied |

| 2026-11-17 | CR-20261117-101 | Named scalar data | fixed | Lossless display and feedback | applied |

| 2026-11-17 | CR-20261117-109 | Complete data consumer impact | fixed | Full-parent ownership and application recheck | applied |

## Detailed Records

### CR-20261117-114 - 专业输入结构保留

- Section changed: scripts/test_generation_inputs.py。
- Before: 既有测试覆盖一般部分覆盖与数据保留。
- After: 具体业务观察缺项保持partial；同级不同理由及不同准备边界分别保留。
- Why: 明确公开API仅验证已给含义的结构，不用关键词冒充专业质量判断。
- Impact: 仅合成测试，无新增生产API或状态格式。
- Validation: 运行相关公开回归、静态链接/敏感信息及镜像检查。
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
- Detail record: [CR-20261111-110](../entries/2026/2026-11/CR-20261111-110-cross-stage-recovery.md).


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

### CR-20261115-008 - Handoff applicability

- Section changed: step technical instructions and contract.
- Before: sourceless step policies lost applicability.
- After: group, ordinal and operation bind every policy.
- Why: independent #113 review finding.
- Impact: human/tree generated views and unchanged feedback.
- Validation: 151 tests passed; test-output/rr01-fix/tests.txt.
- Detail record: ../entries/2026/2026-11/CR-20261115-008-handoff-applicability.md
# CR-20261115-004 dynamic data

- Section changed: dynamic whole-step contract and current data projection.
- Before: only fixed bindings could be selected.
- After: explicit rules allow independent runtime values with full binding checks.
- Why: issue #116, AC-027.
- Impact: whole-step resolver and scoped review; no execution authority.
- Validation: 160 tests passed; corrected fixture fails on baseline.
- Detail record: ../entries/2026/2026-11/CR-20261115-004-dynamic-data.md
### CR-20261115-005 - Local referenced-step feedback

- Section changed: candidate feedback and reference projection.
- Before: inherited actions could not accept local scalar feedback.
- After: chat, Markdown and native feedback materialize only the changed local step.
- Why: #117 / AC-030.
- Impact: source snapshots and unrelated cases remain unchanged; existing review gates apply.
- Validation: 162 tests passed; external test-output/rr05/tests.txt; actual client not tested.
- Detail record: entries/2026/2026-11/CR-20261115-005-local-feedback.md

# CR-20261115-009

Before: shared data edits failed frozen-binding checks. After: precise current consumers materialize full steps and refresh target digests; P0 snapshots stay frozen. Why: #117 / AC-030. Validation: reproduced failure and 22 passing targeted tests; dynamic isolation added. Detail: ../entries/2026/2026-11/CR-20261115-009-data-feedback.md.

CR-20261115-010: Before source data stale; after immutable version bindings. Public red/green. Detail: ../entries/2026/2026-11/CR-20261115-010-data-version-binding.md

## CR-20261115-011

- Before: recursive history and lost referenced instructions.
- After: flat complete snapshots and checked handoff resolution.
- Why: final standards P2 findings.
- Impact: candidate-only; existing historical content retained.
- Validation: public TDD and full regression, external test-output/final-repairs.
- Detail record: entries/2026/2026-11/CR-20261115-011-final-repairs.md

CR-20261115-009 record correction: completed required metadata and sections from rr05-fix/results.md (transcribed), merge-tests.txt (168 passed), and merge-repro.txt. Documentation only; no product tests rerun.


## CR-20261116-008 - Whole-step consistency

- Section changed: semantic signature, local data feedback and reuse contract.
- Before: nested identities erased, formatting inconsistent, mixed data edits could change P0.
- After: retain nested business identity, normalize only operation outer whitespace, route mixed-source data through explicit shared review.
- Why: TAS-08 / AC-014, AC-015 and AC-021.
- Impact: existing public generation, reconstruction and feedback paths; candidate-only.
- Validation: three public red/green regressions and 23 focused checks passed; broader evidence in ticket record.
- Detail record: [CR-20261116-008](../entries/2026/2026-11/CR-20261116-008-whole-step-consistency.md).

## CR-20261116-005 - Business hierarchy

- Section changed: scripts-and-validation.
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
| 2026-11-16 | CR-20261116-003 | scripts-and-validation | changed | Shared dialogue and distinct continuation | applied |

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


## CR-20261116-006 - Semantic projection

- Section changed: shared projection and source-semantics review.
- Before: fragment dedupe could erase independent result text; scalar data used a child level.
- After: whole claims compared; singleton data direct; unknowns retained.
- Why: TAS-06 AC-009/010/021/022.
- Impact: candidate presentation and feedback only.
- Validation: red/green public tests, 191 regression tests; 35 integration checks.
- Detail record: [CR-20261116-006](../entries/2026/2026-11/CR-20261116-006-semantic-projection.md).

### CR-20261116-010 - external module notes

- Section changed: external technical delivery
- Before: inline technical branches
- After: stable module documents and direct entrance
- Why: TAS-10
- Impact: public delivery and feedback
- Validation: synthetic public and regression tests; candidate only
- Detail record: [CR-20261116-010](../entries/2026/2026-11/CR-20261116-010-external-module-notes.md)

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

### CR-20261116-014 - Final visible duplicate retention

- Section changed: duplicate projection and endpoint guidance.
- Before: source existence alone accepted disappearing equivalents.
- After: exact equivalent must survive both business renderings; invisible chains rejected.
- Why: final P2 against REQ-008/009 and AC-009/010.
- Impact: local projection and mirrored package only.
- Validation: public red-green, drift/feedback regression and frozen checks; actual acceptance separate.
- Detail record: [CR-20261116-014](../entries/2026/2026-11/CR-20261116-014-projection-retention.md).

### CR-20261116-015 - Local companion link delivery

- Section changed: local delivery links and native/Markdown return binding.
- Before: relative local href opened as HTTP in actual client.
- After: materialized file URI; exact original delivery base binds feedback; portable historical returns preserved.
- Why: actual companion click failure against AC-017/018/021/023.
- Impact: TCA package and identical repository mirror; no extra index, copy, server or global changes.
- Validation: 11 targeted regressions and unchanged actual v2 return; required checks recorded in detail; client evidence separate.
- Detail record: [CR-20261116-015](../entries/2026/2026-11/CR-20261116-015-companion-links.md).

### CR-20261116-016 - Technical note object identity

- Section changed: technical note grouping and public artifact contract.
- Before: rendered text grouping, case-title fallback and repeated applicability.
- After: full original path/text grouping, readable object identities and conservative ambiguity.
- Why: confirmed duplicate scopes against AC-017/018/021/023.
- Impact: canonical and mirrored TCA; candidate and business authority unchanged.
- Validation: public TDD and preservation tests; full checks in detail; independent acceptance separate.
- Detail record: [CR-20261116-016](../entries/2026/2026-11/CR-20261116-016-technical-notes.md).

### CR-20261117-017 - Agent notes lifecycle and display

- Section changed: module persistence, Agent display and delivery contract.
- Before: stale note-free sections, ambiguous candidate location and shared English display.
- After: ready-owner retirement, per-section source/version, source-overwrite refusal and dedicated Chinese labels.
- Why: user-authorized four linked repairs, AC1–AC4.
- Impact: canonical and mirror only; original candidate/data and business feedback unchanged.
- Validation: public red/green, full checks and traceability results in detail.
- Detail record: [CR-20261117-017](../entries/2026/2026-11/CR-20261117-017-notes-lifecycle.md).

- CR-20261117-017 R2 review repair: shared case-marker identity and intent annotations; existing source binding, delivery and business contracts unchanged. Validation and limitations: [detail](../entries/2026/2026-11/CR-20261117-017-notes-lifecycle.md#independent-review-repair-r2--2026-11-17).
- R2 validation: eight stages / 328 tests passed, lifecycle 6/6; no contract changes; validator retains three inherited synthetic findings. Applied candidate, independent review pending.

### CR-20261117-102 - Module common preconditions

- Section changed: common preparation definition, projection, feedback and restoration.
- Before: whole-list group-scoped extraction and per-case common references.
- After: module-direct definitions, per-item versioned scope, visible pending content and exact feedback origins.
- Why: #136, AC-030/031/032 preconditions and AC-033 lifecycle.
- Impact: canonical and mirror only; no execution or new authority.
- Validation: public TDD, save/read and frozen legacy feedback; see detail.
- Detail record: [CR-20261117-102](../entries/2026/2026-11/CR-20261117-102-common-preconditions.md).

### CR-20261117-101 - Named scalar data

- Section changed: scripts-and-validation
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

### CR-20261117-109 - data-consumer-impact

- Section changed: complete shared-data feedback impact.
- Before: hidden independent consumers could be missed.
- After: exact-parent owners and application recheck, operation exclusions preserved.
- Why: final Spec P2 and Standards P3.
- Impact: candidate feedback only.
- Validation: external red/green and final checks; candidate status.
- Detail record: [CR-20261117-109](../entries/2026/2026-11/CR-20261117-109-data-consumer-impact.md).

### CR-20261117-110 - Chat scope provenance

- Section changed: selected chat delivery.
- Before: selected case incorrectly supplied as original scope parent.
- After: current complete membership and exact original parent stay distinct.
- Why: actual public acceptance defect.
- Impact: bounded common pre/post rendering and extension delivery.
- Validation: public synthetic regression and required checks; candidate only.
- Detail record: [Detail](../entries/2026/2026-11/CR-20261117-110-chat-scope-provenance.md).

- CR-20261117-111: stable pre/cases/post module order, chat and legacy feedback; [detail](../entries/2026/2026-11/CR-20261117-111-module-order.md).

### CR-20261117-112 - 业务分组反馈身份与空格保真

- Section changed: aggregation/feedback 及真实文件公开接口回归。
- Before: 按 flat 深度归一化导致已审分组稿无编辑也拒绝，树解析丢尾空格。
- After: 原始摘要先核对；按实际 case 直属节点归一化；新值保真并准确识别旧 emitter 布局。
- Why: 固定候选和旧 Persona 实际回传均复现同一根因。
- Impact: 候选反馈共用层及镜像，不修改来源或隐藏消费者。
- Validation: 红绿记录、实际 raw/物化文件及最终回归证据；applied candidate。
- Detail record: [CR-20261117-112](../entries/2026/2026-11/CR-20261117-112-grouped-feedback.md)。


## CR-20261117-115 - 准确 typed 反馈与来源职责

| Date | Change ID | Section | Change Type | Summary | Status |
|---|---|---|---|---|---|
| 2026-11-17 | CR-20261117-115 | scripts-and-validation | fixed | 控制行按准确源字段归一化；实际输入/产出保留同名业务叶；每个typed来源完整绑定 | applied |

- Section changed：本记录对应脚本、反馈与显示来源契约。
- Before：文字/键名被误当框架角色，业务编辑丢失或同胞source被篡改；混合片段/未分辨引用漏绑。
- After：瞬时owner/源行绑定与共享typed角色贯穿显示、反馈和应用；未分辨来源保守失效，明确未用来源局部复用。
- Why：独立Spec/Standards四项P2及既有REQ-008/017、AC-034。
- Impact：canonical与镜像；无全局安装、真实业务执行、旧trial修改或发布。
- Validation：RED-01/02/03/04保留；targeted-02共25项通过；93项通过后补整例省略偏移修复，最终受影响25项通过；175文件同字节、87 Python语法通过，三继承扫描无新增；见detail与外部证据。
- Detail record：[CR-20261117-115](../entries/2026/2026-11/CR-20261117-115-typed-feedback-source-roles.md)。
## CR-20261119-144

| Date | Change ID | Section | Change Type | Summary | Status |
| --- | --- | --- | --- | --- | --- |
| 2026-11-19 | CR-20261119-144 | Mixed incremental review and isolated merge | changed | Show the five treatment types, place materials under the appropriate modules, and keep blank inputs and shared applicability readable | applied |

[Detail](../entries/2026/2026-11/CR-20261119-144-mixed-review.md)
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
