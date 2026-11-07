# TPD-01C 自然语言行为请求

每次从仓库根目录以全新执行 Agent 读取真实入口。执行者只读 Skill、它指向的参考、下述输入和逐次实际收到的回答；不要读取 clarification-rubric.md、clarification-red.md 或 fixtures/clarification-continuation.md。模拟对话通过只证明限定材料中的行为，不确认真实业务规则。由主持方按 continuation.md 逐轮发送模拟回答，保存每一轮实际输出、读取记录和源码提交。

## 开始请求

请读取并使用 skills/test-point-discovery/SKILL.md，继续当前模块的业务澄清。资料为 tests/test-point-discovery/fixtures/clarification-prd.md 和 clarification-notes.md（同目录）。这是模拟开发验证，前序确认见说明资料；当前只梳理 M1 及 M3 的跳转接收，不重新画图。请开始这一轮，然后等待我答复。不要调用外部模型、真实业务系统或下游 Skill。

## 后续请求的发送方式

主持方阅读 continuation.md，收到首轮实际提问后才发送第1段回答；执行者作出下一轮响应后再发送第2段，依序进行。每段只给自然语言回答，不附带标准答案、期望产物或评审项。遇到执行者未提及的事项，允许主持方按业务语义直接提出，不能伪造“已回答”的前序问题。未实际发送或处理的轮次记未验证。
