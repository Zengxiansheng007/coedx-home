# CR-20261109-005 - Local reopening

| Field | Value |
| --- | --- |
| Status | validated |
| Target Skill | test-point-discovery |
| Change Type | fixed / validation |
| Scope | core-skill-md / references-and-assets / scripts-and-validation |
| Source | issue93, confirmed S5/R22, REQ008/012/019, design V16 |
| Baseline | ecd54495c96b900c8614c582c8b90b99a41069d3 |
| Author | Codex |
| Related Records | CR-20261109-001, CR-20261109-002, CR-20261109-003, CR-20261109-004 |

## Summary

现稿、自检、评审和后续模块新事实统一沿同一问答 MD 局部回流，相关问题明确处置并复核后集中修订，再具体重审。

## Context And Problem

前四票已有问答、集中生成和评审推进基础。跨模块caller将产品新答复描述为候选，缺少显式相关处置及复核前提，入口和收尾例句未共同绑定原准确版本与无关评审。来源RED是文档契约歧义，未冒充已观察到的行为失败。

## Sections Changed

| File | Section | Change Summary |
| --- | --- | --- |
| SKILL.md | 执行10、验证 | 后续事实与统一回流入口 |
| references/module-clarification.md | 成稿与后续模块的新疑问回流 | 复用来源、只重开影响、部分答复保留、处置复核与集中修订 |
| references/writing-review.md, feedback-review.md | 回流caller | 新缺口进入统一流程 |
| references/workflow-lifecycle.md, roles-entitlements.md, review-and-progress.md | 后续事实与评审/例子 | 产品答案先记录依据，相关处置复核后候选，具体通过后更新 |
| tests/test-point-discovery | flow93及85/87/lifecycle活动标准 | 实际后续新事实、部分答复及拒绝/通过观察 |

## Decision And Alternatives

复用原始自然语言入口、唯一QA、同一路径准确MD、共享生成条件及聚焦评审。新增一处共享回流步骤，由实际触发分支直接引用。无新增运行框架、依赖或语义裁决程序。保留当前模块推进门槛和明确风险范围。

## Detailed Change

绑定现稿和准确版本，仅受影响内容暂停，其他明确依据继续分析。新问题使用新编号并关联旧决定，有效答案和来源复用。部分答复期间旧稿与准确内容保持，明确暂留只是处置完成且业务仍未知。相关来源、事实、部分答复与依赖复核并保存回读后集中出受影响修订，具体拒绝/修改保持准确版本，通过后仅合入实际通过范围并回读。无关内容、状态、永久问答、产品问题和历史确认保留。

## Impact Analysis

18参考及活动请求/rubric按回流分支核对。专项方法、XMind reader/格式和单文件交接复用共享规则。无assets目录，模板及示例位于参考中，相关收尾例子同步。历史运行及冻结99保持原字节，受保护目录、其他Skill、全局和下游未改。完整来源读取与写集见TASK/evidence/93/plan.md。

## Validation Evidence

| Check | Command or Method | Result | Evidence |
| --- | --- | --- | --- |
| RED | baseline source-contract review before edits | caller ambiguity identified | TASK/evidence/93/red-source-contract.md |
| Static | create-skill validator, links/privacy/table/identity and reader3 | P0/P1 zero, links/privacy zero, reader3 passed,230 dependencies identical, contiguous tables passed | TASK/evidence/93/validation-ready/ and validation-final/ |
| Interactive | same actual actor, separately sent fictional fact and actual host replies | four AC supported within actual later-fact/partial/defer/recheck/revision/approval scope | TASK/evidence/93/behavior-review.md and TASK/evidence/candidate-actor/QA.md turns14–17 |
| Preservation | compare actual raw histories and meaningful business sections | oldv2 exact, unaffectedM01 exact, changedM01/M02 equal approved candidate, four old drafts exact | TASK/evidence/93/artifact-comparison.json |

## Safety And Privacy

仅虚构模拟和本地候选，不读真实PRD，不调用外部模型、业务、下游，不安装或发布。工作流由Agent遵循，未宣称宿主强制或accepted。

## Risks And Follow-up

实际新事实和规则答复由主持在真实问题后另发，部分答复期间准确v2与旧稿保持；明确暂留后先复核再集中生成局部稿，另收实际具体批准后才合入准确v3。旧v2原字节、未受影响字段/保存/取消/重复/P001与旧批准保留，P001和新P002业务答案仍未知。准确v3 SHA256为CB83C4362F7D953EB3AC947A870348D7C2514CF456540F573636627691EE0547。

本票实际局部候选直接获批准，没有新拒绝/修改循环，flow93 rubric此分支未执行。此前issue92真实模拟拒绝属于不同运行证据，不改记成本票。新事实来自后续M02复核，仅当前两模块范围，没有未获准模块推进注入。未强制注入保存/回读失败。过程记录非平台全量工具转录，历史捕获限制和失败保持。真实XMind客户端、真实业务和宿主接受均未验证，格式未变不重复客户端往返。静态保留两项既有P2启发式提示。validated仅本地候选证据，独立整票审查、合并及最终冻结链观察另行完成。
