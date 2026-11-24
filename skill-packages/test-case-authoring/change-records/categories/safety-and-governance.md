# safety-and-governance Change Ledger

## CR-20261118-002 - 复核当前来源与收尾保存边界

| Date | Change ID | Section | Change Type | Summary | Status |
|---|---|---|---|---|---|
| 2026-11-18 | CR-20261118-002 | 当前来源及保存一致性 | fixed | 确认实际来源，发现保存冲突时保留临时行并重新读取 | applied |

候选与问答快照在原有原子替换前核对。已生效的合法写入和原审批证据继续保留，重试由当前原问答决定。详见 [CR-20261118-002](../entries/2026/2026-11/CR-20261118-002-scope-closure-current-sources.md)。

## CR-20261118-001 - 原审批证明与明确范围收尾

| Date | Change ID | Section | Change Type | Summary | Status |
|---|---|---|---|---|---|
| 2026-11-18 | CR-20261118-001 | 原审批/永久范围依据 | fixed | 缺归属、未知来源、冲突及越范围仍 fail closed | applied |

- Section changed: 原审批有效证明及关闭参数验证。
- Before: 安全拒绝缺 scope，但无法原样复用局部反馈后有效旧审批。
- After: 不接受 caller unchanged/hash；原审批不改；永久原观察绑定摘要与真实 case_ids。
- Why: 既定 REQ-020 与保存/回读/部分范围边界。
- Impact: 仅工作区候选代码，不授予新审批、执行、安装、发布或全局权限。
- Validation: 负向漂移/缺依赖/外部未绑定、错误范围、原子故障/恢复/幂等；详见 detail。
- Detail record: [CR-20261118-001](../entries/2026/2026-11/CR-20261118-001-scope-closure-review-reuse.md)。

## CR-20261117-119 - 旧候选问题的准确历史索引

| Date | Change ID | Section | Change Type | Summary | Status |
|---|---|---|---|---|---|
| 2026-11-17 | CR-20261117-119 | safety-and-governance | fixed | 复用非空id索引约定，旧建议保留且不给只读例外 | applied |

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
| 2026-11-17 | CR-20261117-118 | safety-and-governance | fixed | 准确已完成技术历史只读复用，本轮业务目标保持本例归属 | applied |

- Before：全部历史目标都作为当前业务写目标检查，合法技术历史阻断无编辑反馈。
- After：共享类型角色识别准确技术历史；新增、重开和实际答复仍拒绝跨例暗写。
- Why：合成公开QA与真实生成MD独立red。
- Impact：单一反馈适配器、直接引用、公开恢复正反例；无新schema或答案权威。
- Validation：定向、恢复及新进程结果见详细记录；历史失败保留。
- Detail record：[CR-20261117-118](../entries/2026/2026-11/CR-20261117-118-feedback-technical-history.md)。


## CR-20261117-113 - QA 与业务投影生命周期

| Date | Change ID | Section | Change Type | Summary | Status |
|---|---|---|---|---|---|
| 2026-11-17 | CR-20261117-113 | safety-and-governance | fixed | 单份答案权威、原审批与 source/digest 守卫、全树凭据保护及历史证据保持 | applied |

- Before：纯评估无法回到唯一 QA；来源、审计和字面业务字段用途混淆，真实公共/特殊归属与空格回流有断点。
- After：单份答案权威、原审批与 source/digest 守卫、全树凭据保护及历史证据保持；沿原候选/QA 保存，同版回放，业务批准与执行边界不升级。
- Why：RTA-02 真实失败与已确认 REQ/AC；共享 seam 经 Root 核准后基于 RTA-01 集成 tip 修改。
- Impact：仅本票包与镜像；原试用、原 P0、全局 Skill、业务执行及发布保持原边界。
- Validation：公开接口先红后绿、真实文件与子进程恢复；full01 失败保留，最终 full-final.txt 与结构扫描按 detail 记录，独立 P2 留给后续 fresh implementer。
- Detail record：[CR-20261117-113](../entries/2026/2026-11/CR-20261117-113-qa-projection-lifecycle.md)。

## Purpose

Track source semantics and technical handoff changes in this category.

## Outline

| Date | Change ID | Section | Change Type | Summary | Status |
|---|---|---|---|---|---|
| 2026-11-11 | CR-20261111-201 | Source semantics | fixed | Goal-bounded authoring and retained constraints | applied |

## Detailed Records

### CR-20261111-201 - Source semantics

- Section changed: source interpretation and technical handoff.
- Before: generic source comparison; separate technical handoff dropped by conversion.
- After: explicit authoring checks and candidate-only technical constraints.
- Why: wrong data ownership cannot be repaired by rendering.
- Impact: existing candidate and presentation contracts; no business execution.
- Validation: 97 candidate tests passed; actual multi-turn correction and exact-version public review completed for three simulated cases. Historical missed questions and orchestration failures retained; no host acceptance.
- Detail record: [CR-20261111-201](../entries/2026/2026-11/CR-20261111-201-source-semantics.md).

## CR-20261116-008 - Whole-step consistency

- Section changed: semantic signature, local data feedback and reuse contract.
- Before: nested identities erased, formatting inconsistent, mixed data edits could change P0.
- After: retain nested business identity, normalize only operation outer whitespace, route mixed-source data through explicit shared review.
- Why: TAS-08 / AC-014, AC-015 and AC-021.
- Impact: existing public generation, reconstruction and feedback paths; candidate-only.
- Validation: three public red/green regressions and 23 focused checks passed; broader evidence in ticket record.
- Detail record: [CR-20261116-008](../entries/2026/2026-11/CR-20261116-008-whole-step-consistency.md).

## CR-20261116-003 - Shared stage adapter

| Date | Change ID | Section | Change Type | Summary | Status |
| --- | --- | --- | --- | --- | --- |
| 2026-11-16 | CR-20261116-003 | safety-and-governance | changed | Shared dialogue and distinct continuation | applied |

- Section changed: TCA stage routing and linked public-entry instructions.
- Before: duplicated parent dialogue and automatic application after summary agreement.
- After: host-resolved test-grill-me interaction; confirm-only note waits; explicit continuation applies existing API.
- Why: TAS-03 and parent AC-001/002/003/004/006/024/025.
- Impact: existing candidate and sole MD authority; no production API or execution-layer change.
- Validation: 34 targeted public tests passed; actual changed-route dialogue and client unverified.
- Detail record: [CR-20261116-003](../entries/2026/2026-11/CR-20261116-003-stage-adapter.md).

### CR-20261116-004 - scoped-recovery-closure

- Section changed: Recovery and scoped closure
- Before: Upgrade recovery/cleanup gap
- After: Actual-file recovery, permanent basis before bounded cleanup
- Why: TAS-04 AC-007/026/027/028
- Impact: Isolated candidate only; existing authority retained
- Validation: Public API tests passed; dialogue pending
- Detail record: [CR-004](../entries/2026/2026-11/CR-20261116-004-scoped-recovery-closure.md)


## CR-20261117-115 - 准确 typed 反馈与来源职责

| Date | Change ID | Section | Change Type | Summary | Status |
|---|---|---|---|---|---|
| 2026-11-17 | CR-20261117-115 | safety-and-governance | fixed | 控制行按准确源字段归一化；实际输入/产出保留同名业务叶；每个typed来源完整绑定 | applied |

- Section changed：本记录对应脚本、反馈与显示来源契约。
- Before：文字/键名被误当框架角色，业务编辑丢失或同胞source被篡改；混合片段/未分辨引用漏绑。
- After：瞬时owner/源行绑定与共享typed角色贯穿显示、反馈和应用；未分辨来源保守失效，明确未用来源局部复用。
- Why：独立Spec/Standards四项P2及既有REQ-008/017、AC-034。
- Impact：canonical与镜像；无全局安装、真实业务执行、旧trial修改或发布。
- Validation：RED-01/02/03/04保留；targeted-02共25项通过；93项通过后补整例省略偏移修复，最终受影响25项通过；175文件同字节、87 Python语法通过，三继承扫描无新增；见detail与外部证据。
- Detail record：[CR-20261117-115](../entries/2026/2026-11/CR-20261117-115-typed-feedback-source-roles.md)。
