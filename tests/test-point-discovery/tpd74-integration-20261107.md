# #74 必要集成复核

旧冻结：5a3cb8c9b2dabd2c72b7f887c876d4cd88908a33。合并目标：codex/test-point-discovery-20261107，1095f59f042356de567356169f0537ac2146ae88（#71和#70已由Root集成）。在codex/tpd74-20261107执行真实git merge，不reset/rebase，不改历史证据。新冻结为包含这两个父提交的本地merge提交，准确SHA以git记录及回流消息为准。

唯一手工产品写集：skills/test-point-discovery/SKILL.md。解决description、能力说明和入口组织冲突；保留看板、维护、计算、聊天/MD反馈与异步入口。将旧异步“替换看板步骤”的独立段落并入共同第2/3步，异步实际读取、澄清/编写/自检回查及受理/过程/终局主线保持；第4/5绘图门、第6续接规则、第9评审更新和第10反馈原约定保留。只新增本记录，其他进入分支的文件均来自已集成#70/#71，不手改。

旧行为证据适用性：Root告知旧冻结两轴审查0发现、四AC在限定模拟范围通过。本次不将该结论扩展为新入口独立验收；当前实现者实际回读最终入口，异步仍可到async-exchange.md及其方法、再到通用具体点与评审更新，未添加#72不存在的状态方法链接。原有async-session及唯一准确MD完全不变，因此不重放未变模拟，也不冒充新规划/客户端/真实业务通过。新入口待Root定向独立复核。

已执行必要检查：合并冲突仅SKILL.md；解决后回读全文，冲突标记不存在。Python -X utf8读取14份产品MD，本地Markdown引用均存在。对旧提交中的两个异步参考及8份async材料逐文件比较Git旧blob与当前文件字节，10份完全相同；没有新测试数据/业务调用。

目标Skill使用 `python -X utf8 C:/Users/lenovo/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/test-point-discovery` 返回exit0与“Skill is valid!”。对最终入口相对integration的差异已人工回读，变化限异步触发、能力和第2/3步主线及原模拟指针；其余已集成路由保留。工作区diff检查exit0；冻结时再执行暂存diff检查，未运行历史业务模拟或全仓测试。

保持不变文件SHA256（旧→新相同）：

- async-exchange.md：f3259460db1a448a993bb4e20886a30a3926eea3bd3cc88fc5b6cd1833851fa6
- method-error-guessing-checklist.md：cf7deb4c5c9f4753a7abcae951b4d45a6922276114f25a74d96bb42b1bc0da57
- async-current.md：5eebeab7d885158784ebf098e06c0791c9fbff2caea0344abcdda37c17651b63
- async-red.md：479d6f3ce2bda35cbecb7a85555da80650f12495df8168eb6eef03a11ecff07f
- async-request.md：b07ce65e316dab2e1f08265c840c322b1893378ea2b5b1e8ce9baf4853a875b3
- async-review-v1.md：595225b9771386e3b60ee8acb1d2d558d4b8d56a1ae7b3fe4ac1667053da0b5f
- async-session.md：3de73710df9a63f47a5aae1d19788b9ebd0de9cd12f00fde49c24c5313bc6b88
- async-verification.md：2e925cab17542fe38ee104611201d6f852e237c1a6a2dc19faaef9f6b79e8970
- fixtures/async-notes.md：b4624f3b64bc40f52c529e4d63cf0f7a43b4ef2dd43174cae9411cf248431956
- fixtures/async-prd.md：94802b59ff71b465bdd3d44d3a35639a5703dc06743b02f290eea4241c53cefe

不合入integration、不push，仍由Root复核后集成。原有限定、未决业务规则与未执行项继续有效。
