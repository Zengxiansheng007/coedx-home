# downstream-and-handoff Change Ledger

## CR-20261119-145

| Date | Change ID | Section | Change Type | Summary | Status |
| --- | --- | --- | --- | --- | --- |
| 2026-11-19 | CR-20261119-145 | 原生回传 | changed | 基于版本的文件定位和问答记录恢复 | applied |

[变更详情](../entries/2026/2026-11/CR-20261119-145-native-feedback.md)

## CR-20261119-143

| Date | Change ID | Section | Change Type | Summary | Status |
| --- | --- | --- | --- | --- | --- |
| 2026-11-19 | CR-20261119-143 | 反馈定位 | added | 版本化布局、稳定编号及明确的回传边界 | applied |

[变更详情](../entries/2026/2026-11/CR-20261119-143-incremental-review.md)

## CR-20261117-113 - QA 与业务投影生命周期

| Date | Change ID | Section | Change Type | Summary | Status |
|---|---|---|---|---|---|
| 2026-11-17 | CR-20261117-113 | downstream-and-handoff | fixed | 同版 render/write/feedback/checkpoint/resume，准确 data_refs/原步 origins 与父 P0 边界 | applied |

- Before：纯评估无法回到唯一 QA；来源、审计和字面业务字段用途混淆，真实公共/特殊归属与空格回流有断点。
- After：同版 render/write/feedback/checkpoint/resume，准确 data_refs/原步 origins 与父 P0 边界；沿原候选/QA 保存，同版回放，业务批准与执行边界不升级。
- Why：RTA-02 真实失败与已确认 REQ/AC；共享 seam 经 Root 核准后基于 RTA-01 集成 tip 修改。
- Impact：仅本票包与镜像；原试用、原 P0、全局 Skill、业务执行及发布保持原边界。
- Validation：公开接口先红后绿、真实文件与子进程恢复；full01 失败保留，最终 full-final.txt 与结构扫描按 detail 记录，独立 P2 留给后续 fresh implementer。
- Detail record：[CR-20261117-113](../entries/2026/2026-11/CR-20261117-113-qa-projection-lifecycle.md)。

- [CR-20261115-007](../entries/2026/2026-11/CR-20261115-007-handoff-revalidation.md): restore transient complete meaning using actual same-version evidence; no downstream execution claim.

## Purpose

Track source semantics and technical handoff changes in this category.

## Outline

| Date | Change ID | Section | Change Type | Summary | Status |
|---|---|---|---|---|---|
| 2026-11-17 | CR-20261117-114 | 语义交付核对 | fixed | 当前来源完整还原与同版实际文件回读 | applied |
| 2026-11-11 | CR-20261111-201 | Source semantics | fixed | Goal-bounded authoring and retained constraints | applied |

| 2026-11-17 | CR-20261117-017 | Agent notes lifecycle and display | fixed | Ready-owner cleanup, exact candidate binding and Chinese display | applied |

| 2026-11-17 | CR-20261117-109 | Complete data consumer impact | fixed | Full-parent ownership and application recheck | applied |

## Detailed Records

### CR-20261117-114 - 语义交付核对

- Section changed: chat-delivery及professional-generation交付步骤。
- Before: 投影规则可被误用为完成来源解释的替代。
- After: 交付前按当前来源还原并比较实际文件，技术/来源保留在既有权威位置。
- Why: REQ-014/016/017及旧稿不能替代完整重新生成。
- Impact: 只改变编写及检查指引，不执行用例、不新增人工展开稿。
- Validation: 当前结构保留检查；独立完整生成、用户具体稿/XMind验收待后续。
- Detail record: [CR-20261117-114](../entries/2026/2026-11/CR-20261117-114-professional-generation.md)。

### CR-20261111-201 - Source semantics

- Section changed: source interpretation and technical handoff.
- Before: generic source comparison; separate technical handoff dropped by conversion.
- After: explicit authoring checks and candidate-only technical constraints.
- Why: wrong data ownership cannot be repaired by rendering.
- Impact: existing candidate and presentation contracts; no business execution.
- Validation: 97 candidate tests passed; actual multi-turn correction and exact-version public review completed for three simulated cases. Historical missed questions and orchestration failures retained; no host acceptance.
- Detail record: [CR-20261111-201](../entries/2026/2026-11/CR-20261111-201-source-semantics.md).

## CR-20261114-001 — Module handoff partition

- Section changed: review projection and feedback.
- Before: hidden provenance and repeated process metadata.
- After: direct-owner module instruction branches; business applicability remains visible.
- Why: #113 / REQ-015-016 / AC-023-024.
- Impact: scoped, ordinary and chat views; supported markdown/native feedback.
- Validation: public red/green; 149 synthetic regressions passed; real client unverified.
- Detail record: [CR-20261114-001](../entries/2026/2026-11/CR-20261114-001-module-handoff.md).
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

## CR-20261115-011

- Before: recursive history and lost referenced instructions.
- After: flat complete snapshots and checked handoff resolution.
- Why: final standards P2 findings.
- Impact: candidate-only; existing historical content retained.
- Validation: public TDD and full regression, external test-output/final-repairs.
- Detail record: entries/2026/2026-11/CR-20261115-011-final-repairs.md

## CR-20261116-003 - Shared stage adapter

| Date | Change ID | Section | Change Type | Summary | Status |
| --- | --- | --- | --- | --- | --- |
| 2026-11-16 | CR-20261116-003 | downstream-and-handoff | changed | Shared dialogue and distinct continuation | applied |

- Section changed: TCA stage routing and linked public-entry instructions.
- Before: duplicated parent dialogue and automatic application after summary agreement.
- After: host-resolved test-grill-me interaction; confirm-only note waits; explicit continuation applies existing API.
- Why: TAS-03 and parent AC-001/002/003/004/006/024/025.
- Impact: existing candidate and sole MD authority; no production API or execution-layer change.
- Validation: 34 targeted public tests passed; actual changed-route dialogue and client unverified.
- Detail record: [CR-20261116-003](../entries/2026/2026-11/CR-20261116-003-stage-adapter.md).

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

### CR-20261117-112 - 同版已审与未审业务稿回传

- Section changed: raw/物化 Markdown 与原生适配器共用反馈解释层。
- Before: 已审元数据因业务分组深度而破坏完整用例匹配。
- After: 同版可信元数据按用例归一化，原返回摘要和所有业务叶仍准确核对。
- Why: 无编辑零变更及实际预期编辑须跨入口一致。
- Impact: 显示层不改候选数据、data_refs、隐藏记录或来源版本保护。
- Validation: 原始文件只读探针和公开接口正反例；实际客户端未验收。
- Detail record: [CR-20261117-112](../entries/2026/2026-11/CR-20261117-112-grouped-feedback.md)。


## CR-20261117-115 - 准确 typed 反馈与来源职责

| Date | Change ID | Section | Change Type | Summary | Status |
|---|---|---|---|---|---|
| 2026-11-17 | CR-20261117-115 | downstream-and-handoff | fixed | 控制行按准确源字段归一化；实际输入/产出保留同名业务叶；每个typed来源完整绑定 | applied |

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

## CR-20261128-175

按版本和编号交付独立执行者。[变更记录](../entries/2026/2026-11/CR-20261128-175-review-and-case-handoff.md)

## CR-20261128-184

按同版编号读取完整单例及反馈交接。[详细记录](../entries/2026/2026-11/CR-20261128-184-reader-views.md)
