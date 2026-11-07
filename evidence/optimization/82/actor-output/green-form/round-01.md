# 消息草稿本轮对话 v0.1

SIMULATION，模拟开发记录。此轮仅提出组织范围问题，尚未收到主持者答复，尚未进行具体测试点评审。

## 本轮实际请求

来源为 `tests/test-point-discovery/optimization-82-form-request.md`。

> SIMULATION。请使用本仓库 skills/test-point-discovery/SKILL.md，读取 tests/test-point-discovery/fixtures/optimization-82-form.md，继续已选择的消息草稿模块，整理本轮局部待评审测试点。沿用资料中给出的模拟规划前提，本轮无需重画规划图。
>
> 请把具体待评审内容和资料说明保存到主持者指定的本轮输出目录，并在对话中说明本轮状态。需要我决定的事情请先问，我会逐轮回复。这里先授权待评审材料，具体测试点评审尚未发生。公告资料可帮助理解关联，本轮先处理消息草稿。
>
> 所有资料和后续答复均为开发模拟。请保存每轮实际请求、显示版本和答复身份，等待主持者发送下一轮答复。

## 本轮实际显示回复 v0.1

消息草稿资料 v1 的规则已明确，可沿用“创建表单→字段”整理。当前范围是站内信、短信、推送三个发送维度，终点为保存一条草稿并在列表显示相同标题。

联系人与公告的规则相同，是否提升为跨模块公共规则，需要你决定。

- A．本轮保留在消息草稿模块内表达，推荐。公告现行片段保留原状，后续整理公告时仍需维护相同规则。
- B．本轮提为消息草稿与公告共用的联系人规则。可减少重复维护，但会增加公告分支及公共规则引用的评审范围。
- C．自定义共用范围或组织方式。

例如，选择 A 时，消息草稿表单下写“联系人必填、11位0至9数字”；选择 B 时，把这条规则放入公共分支，并明确适用消息草稿与公告创建。推荐 A，因为本轮已选择消息草稿，公告尚未决定整理范围。

请回复 A、B 或自定义安排。收到答复后继续保存局部待评审测试点。

## 资料与Agent交接说明

- 当前展示版本为本文件“本轮实际显示回复 v0.1”。答复身份为隔离执行 Agent，问题面向模拟主持者。当前没有主持者答复，不将推荐视为决定。
- 规划前提来自资料 F0，属于模拟接续前提。三个发送维度来自 F1。送审、发送、送达、编辑、删除均在本轮范围之外。
- F2 的标题必填、计数、空值及不同上限将进入标题字段候选。F3 的联系人同一输入框及相同校验将进入联系人字段候选。F4 的备注规则可共用表达，控件是否复用仍未知，不能据共用表达认定实际只验证一次。
- F5 的两个说明含义不同，将按“用户可见补充文本”与“内部备案原因”区分适用维度及规则，避免因字段同名混用。F6 对应保存与列表同条草稿、相同标题的结果检查。
- F7 是本轮关联建议的依据。跨模块公共提取尚未决定，当前公告片段保持现行身份。消息草稿不依赖公告发布。
- 当前问题属于组织与范围决定，不是业务规则缺口，没有获得明确暂留的产品问题。等待实际模拟答复后继续，准确 MD 尚未创建或更新，尚未交接。
- 本轮未运行真实业务、外部模型、下游流程或 XMind 客户端。

## 读取清单

- `tests/test-point-discovery/optimization-82-form-request.md`
- `tests/test-point-discovery/fixtures/optimization-82-form.md`，消息草稿资料 v1，F0—F7及公告现行片段 v1
- `skills/test-point-discovery/SKILL.md`
- `skills/test-point-discovery/references/information-maintenance.md`
- `skills/test-point-discovery/references/module-clarification.md`
- `skills/test-point-discovery/references/writing-review.md`
- `C:/Users/lenovo/.agents/skills/codex-powershell-governance/SKILL.md`，只用于本轮只读 PowerShell 操作约束
