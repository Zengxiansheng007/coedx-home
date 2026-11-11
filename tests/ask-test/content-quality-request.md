# AT03 actor请求（仅模拟）

主持分别开启独立咨询，替换 WORKTREE 与明确安装路径。actor只读本请求和指定fixture，不得读rubric。实际提问后主持才发送模拟回答；无提问不预填对话。Root统一记录实际输入、输出、引用、工具动作和前后文件/状态hash。以下不是预写答复。

1. 使用 WORKTREE/.agents/skills/ask-test/SKILL.md 的 ask-test 咨询。适用规则明确为 C:/Users/lenovo/.codex/skills/test-point-discovery/SKILL.md（只读）。请看 WORKTREE/tests/ask-test/fixtures/quality/shared.md，渠道下标题检查太重复，粒度也太细，怎样调整比较清楚？只咨询。
2. 使用同一 ask-test 入口及同一 TPD 规则，只读 WORKTREE/tests/ask-test/fixtures/quality/unknown.md。两个“说明”字段是不是能合在一起？我只想解决这一处组织问题。
3. 使用同一 ask-test 入口。适用规则为 C:/Users/lenovo/.codex/skills/test-case-authoring/SKILL.md（只读）。请看 WORKTREE/tests/ask-test/fixtures/quality/expectation.md，这条手写P0的预期怎么表达才可核对？只给局部建议。

禁止业务改稿、状态更新、原Skill改动、下游启动或消息发送。模拟结论不能成为业务评审/执行通过证据。
