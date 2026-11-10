# Scripts And Validation Change Ledger

## Purpose

追踪活动验证入口、独立行为证据及未验证限制。

## Outline

| Date | Change ID | Section | Change Type | Summary | Status |
| --- | --- | --- | --- | --- | --- |
| 2026-11-10 | CR-20261110-003 | 模块循环 | changed | 八阶段模块及局部回流 | applied |
| 2026-11-10 | CR-20261110-002 | 阶段1～3规划过渡 | changed | 当前表图确认与实际推进 | applied |
| 2026-11-10 | CR-20261110-001 | 八阶段入口 | changed | 默认阶段1及用户接续 | applied |
| 2026-11-09 | CR-20261109-006 | 最终修复验证与CR001证据 | validation | 实际有限模拟归档与静态回归复核 | validated |
| 2026-11-09 | CR-20261109-005 | flow93与活动重开请求 | fixed | 局部回流、集中修订与实际具体重审 | validated |
| 2026-11-09 | CR-20261109-004 | flow92与活动推进请求 | validation | 逐轮具体意见、通过与准确回读先后观察 | validated |
| 2026-11-09 | CR-20261109-001 | 初始请求与审查rubric | validation | 原始资料启动并逐轮等待主持答复 | validated |
| 2026-11-09 | CR-20261109-002 | 对话与唯一问答 | fixed | 明确所有权与逐轮状态 | validated |
| 2026-11-09 | CR-20261109-003 | 当前模块集中生成 | fixed | 处置、来源补漏和依赖复核绑定生成 | validated |

## Detailed Records

### CR-20261110-002 - planning-transitions

- Section changed 为首次阶段1～3推进、规划确认及自然语言验证入口。
- Before 为已有先业务规划，缺少连续动作集中说明与当前表图版本绑定。
- After 为成果简述后实际推进，修改表图重新展示，确认当前版本后进入4。
- Why 为issue96与父005/006规划段/012。
- Impact 限入口、规划参考、本票虚构开发场景，沿用七类和唯一问答MD。
- Validation 静态与行为分证，当前applied，实际证据见详情。
- Detail record 为[CR002](../entries/2026/2026-11/CR-20261110-002-planning-transitions.md)。

### CR-20261109-006 - final-review-closeout

- Section changed 为最终修复验证记录与CR001证据路径和范围。
- Before 为actor-green89占位路径和pending状态未承接已完成技术证据。
- After 为引用真实QA初始turns1–3、独立评审补充和图形回执，保留历史检查点。
- Why 为最终Standards评审的当前追踪发现。
- Impact 验证脚本仅在TASK/evidence/final-fix，产品脚本及历史测试不变。
- Validation 为实际RED文档契约、GREEN结构/引用/隐私/表格/依赖身份、reader3与完整仓库检查；行为证据沿用已检查初始模拟，最终单运行时待执行。
- Detail record 为[CR006](../entries/2026/2026-11/CR-20261109-006-final-review-closeout.md)。

### CR-20261109-005 - local-reopening

- Section changed 为flow93与活动重开请求。
- Before 为缺少已通过双模块后的实际局部重开观察。
- After 为实际逐轮部分答复、明确暂留、拒绝与通过观察。
- Why 为issue93及已确认S5/R22。
- Impact 限本次受影响流程及必要活动验证，保留无关评审和历史字节。
- Validation 静态P0/P1零、reader3通过，实际turn14–17部分/暂留/复核/集中修订/具体批准及保真支持四AC；本票新拒绝循环未执行，见详情与TASK/evidence/93。
- Detail record 为[CR005](../entries/2026/2026-11/CR-20261109-005-local-reopening.md)。

### CR-20261109-004 - reviewed-module-advance

- Section changed 为flow92请求/rubric及progress、optimization87、feedback活动标准。
- Before 为旧接续请求未证明初始到双模块完整新流程。
- After 为接续真实已产生QA及集中稿，主持分别发意见，观察实际版本、读回和M02问题先后。
- Why 为issue92四项AC。
- Impact 为历史证据和99freeze不改写，静态与语义分别报告。
- Validation 见本次详情与TASK/evidence/92。
- Detail record 为[CR004](../entries/2026/2026-11/CR-20261109-004-reviewed-module-advance.md)。

### CR-20261109-001 - business-before-planning

- Section changed 为 tests/test-point-discovery 下活动 requests/rubric、workflow-lifecycle 请求/审查和新增flow89夹具与请求。
- Before 为部分请求先要求规划，已有接续场景不能覆盖新入口。
- After 为独立演员由未规划资料启动，问题先于依赖答案的规划。
- Why 为 issue89 AC4，拒绝关键词检查冒充行为通过。
- Impact 不变更读取器或测试框架，不覆盖冻结历史证据。
- Validation 当前有限初始模拟见TASK/evidence/candidate-actor/QA.md turns1–3及TASK/evidence/89/independent-review.md green补充，静态复核见CR006；原applied检查点保留在原提交。
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

### CR-20261110-001 - stage-entry

- Section changed 为本分类直接入口、资料前提或入口验证。
- Before 为旧内部操作序号及直接接续分流。
- After 为共享八阶段定义，入口先核对，接续等待真实同意。
- Why 为#95及父#94的入口需求。
- Impact 限目标Skill及入口模拟请求，下游仅同步引用条件。
- Validation 为静态检查与独立行为分证，结果见详情。
- Detail record 为[CR-20261110-001](../entries/2026/2026-11/CR-20261110-001-stage-entry.md)。

### CR-20261110-003 - module-stage-cycle

- Section changed: 模块阶段4～7、三反馈及本期验证入口
- Before: 已有业务机制，阶段过渡与模块动作未集中对应
- After: 明确5原始来源复核、6集中编写、7评审/回读/收尾及下一模块4，局部4→5→6→7
- Why: #97及父007—010的八阶段一致性
- Impact: 仅本Skill及必要本期测试，reader格式与下游保持原契约
- Validation: TASK/ticket97-static.json及reader/structure/diff log，行为pending
- Detail record: [CR-20261110-003](../entries/2026/2026-11/CR-20261110-003-module-stage-cycle.md)
