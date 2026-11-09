# CR-20261109-002 - Direct dialogue and single QA

| Field | Value |
| --- | --- |
| Status | validated |
| Target Skill | test-point-discovery |
| Change Type | fixed |
| Scope | core-skill-md / references-and-assets / scripts-and-validation |
| Source | issue90, S5/R22, REQ008 and V14 |
| Baseline | cd9dbd048c63c16212bc66245ee40cd6cda794a0 |
| Author | Codex |
| Related Records | CR-20261109-001 |

## Summary

直接在对话显示问题与选择，跨阶段/模块持续更新唯一问答 MD，准确测试点 MD 保持独立职责。

## Context And Problem

原入口仅称过程 MD，规划材料又要求另存实际答复，跨模块恢复存在平行问答记录歧义。既有漏答、部分回答及明确暂留规则有效，保留并明确状态差异。

## Sections Changed

| File | Section | Change Summary |
| --- | --- | --- |
| SKILL.md | 步骤7、Validation | 对话全文、固定问答身份与实际行为验证 |
| references/module-clarification.md | 同一记录、提问与承接 | 唯一路径、永久问答结构、状态和依赖 |
| references/planning-confirmation.md | 确认后的交接 | 实际答复归唯一问答，规划只引用 |
| references/writing-review.md | 产品区 | 未答状态归唯一问答 |
| references/review-and-progress.md | 安全收尾 | 同一问答永久历史保留 |
| tests/test-point-discovery | flow90与活动澄清/覆盖请求及rubric | 实际两轮以上模拟，记录观察条件 |

## Decision And Alternatives

复用现有过程 MD、Q/B编号与覆盖约定，补齐跨阶段身份和可直接使用的永久问答结构。无需新增框架、业务状态JSON或依赖。18参考及所有活动请求/rubric按问答所有权检查，无关方法与历史证据保持原样。

## Detailed Change

独立问题可同轮提出，依赖主题等实际前提后再问。漏答、部分回答、待查事实、等待前提和不知道后处置未定分别保存。明确延期/转产品保留真实依据与业务未知，不自动形成确定预期。模板中的答复历史留空至实际回复。准确MD、草稿和规划使用引用恢复QA来源。

## Impact Analysis

影响整体业务、模块深入与评审恢复的问答所有权。来源规则、粒度、共用范围、排除、XMind格式及具体评审仍依原契约。下游Skill和全局安装均不修改。CR001及历史冻结材料保留。

## Validation Evidence

| Check | Command or Method | Result | Evidence |
| --- | --- | --- | --- |
| RED | baseline source-contract inspection | ambiguity identified, behavior not evaluated | task evidence/90/red-source-contract.md |
| Structural/privacy/reader | create-skill --require-change-records, links/privacy scan, reader3 | P0/P1=0, scan0, reader3 passed | task evidence/90/create-skill.json, candidate-static.json, check-1.txt; final freeze evidence/90/validation-final/ |
| Interactive | actual entry, host round3 and round4 separately sent after questions | AC1–4 observed in limited fictional SIM | task evidence/candidate-actor/QA.md Actual actor reply turn4/turn5, Actual host reply turn4/turn5, D003 and round6 |

## Safety And Privacy

仅虚构模拟资料。无真实PRD、系统业务、下游执行、外部模型、安装或发布。人工条件为Agent语义工作流，候选不能自授宿主接受。敏感模式扫描零命中。

## Risks And Follow-up

结构和关键词检查不能证明真实问答正确。已核对实际actor两轮记录，等待独立整票审查。无格式变更，XMind客户端未重跑。历史169测试按未改字节复用，针对性读者回归另记。当前为本地 validated-candidate，记录 validated 表示本票限定本地检查完成，不授予真实业务接受。

## Actual Interactive Observations

固定入口SHA256为6f277b1a642d06ef00158d838f28e61c5bbca9c97ba5391e18bc23e6b622bbfe。沿用前票实际确认表图与同一QA，M01中Q005–Q007独立直接对话展示，含选项、例子、推荐和理由。主持round3部分回答计数、称表情不知道、漏答Q006并答复拒绝不同消息重复标题。执行者保留部分与漏答，未直接转产品，实际补问表情处置与Q006。只有重复拒绝前提回答后才实际提出Q008范围和Q009比较方式。

主持round4在第二次真实发送的模拟消息明确暂留表情、补答空白、比较范围和精确比较。执行者保存原文与模拟来源，Q006漏答历史、Q005补问链与Q007→Q008/Q009依赖可追溯；仅此时生成P001产品未决，表情预期仍未知。所有阶段沿用同一QA.md。未生成测试点稿/准确MD，未进入M02，停在M01澄清结束检查之前，符合主持准确暂停要求。

本实现者实际读取上述QA当前内容进行语义核对，未代填actor答复或结果。QA为actor当轮文件与实际主持消息记录，平台全量工具逐字导出未提供。模拟不证明真实产品或系统接受，不替代后续91–93验收。独立merger继续整票审查。
