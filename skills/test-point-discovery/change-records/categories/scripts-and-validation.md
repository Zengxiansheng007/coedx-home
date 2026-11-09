# Scripts And Validation Change Ledger

## Purpose

追踪活动验证入口、独立行为证据及未验证限制。

## Outline

| Date | Change ID | Section | Change Type | Summary | Status |
| --- | --- | --- | --- | --- | --- |
| 2026-11-09 | CR-20261109-001 | 初始请求与审查rubric | validation | 原始资料启动并逐轮等待主持答复 | applied |
| 2026-11-09 | CR-20261109-002 | 对话与唯一问答 | fixed | 明确所有权与逐轮状态 | validated |

| 2026-11-09 | CR-20261109-003 | 当前模块集中生成 | fixed | 处置、来源补漏和依赖复核绑定生成 | validated |

## Detailed Records

### CR-20261109-001 - business-before-planning

- Section changed 为 tests/test-point-discovery 下活动 requests/rubric、workflow-lifecycle 请求/审查和新增flow89夹具与请求。
- Before 为部分请求先要求规划，已有接续场景不能覆盖新入口。
- After 为独立演员由未规划资料启动，问题先于依赖答案的规划。
- Why 为 issue89 AC4，拒绝关键词检查冒充行为通过。
- Impact 不变更读取器或测试框架，不覆盖冻结历史证据。
- Validation 详细记录分别链接实际静态、语义和未执行项。
- Detail record [CR-20261109-001](../entries/2026/2026-11/CR-20261109-001-business-before-planning.md)。

### CR-20261109-002 - dialogue-and-single-qa

- Section changed 为入口、澄清/规划/编写/收尾参考及活动验证。
- Before 为跨阶段记录身份和规划答复所有权存在歧义。
- After 为直接对话全文、同一路径问答及分别保存状态和实际来源。
- Why 为落实 issue90 与 S5/R22。
- Impact 限本票问答行为及必要验证，运行时与格式未改。
- Validation 本地结构/隐私/reader3通过，实际actor host round3/4语义核对见详情与 task evidence/90；独立整票审查待执行。
- Detail record [CR-20261109-002](../entries/2026/2026-11/CR-20261109-002-dialogue-and-single-qa.md)。

### CR-20261109-003 - module-collective-generation

- Section changed 为当前模块生成条件、编写及关联活动验证。
- Before 为明确规则与部分答复可即时成稿，来源复核未绑定生成。
- After 为先保存编写依据，问题明确处置及来源补漏/依赖复核后集中出稿。
- Why 为落实issue91与已确认S5/R22。
- Impact 限当前模块及受影响关联入口，格式与下游边界保持。
- Validation 本地结构/隐私/reader3通过，实际同一actor D004/D005补漏及D006修复v2语义核对完成，证据见详情与task evidence/91。
- Detail record [CR-20261109-003](../entries/2026/2026-11/CR-20261109-003-module-collective-generation.md)。
