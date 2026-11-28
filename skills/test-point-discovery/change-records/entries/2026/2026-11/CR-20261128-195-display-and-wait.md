# CR-20261128-195 - 展示当前模块大纲并等待答复

| Field | Value |
| --- | --- |
| Status | validated |
| Target Skill | test-point-discovery |
| Change Type | changed / validation |
| Scope | core-skill-md / references-and-assets / scripts-and-validation / safety-and-governance |
| Source | #195、父规格 #193 的 AC-001、AC-002、AC-003 |
| Baseline | 8a2a5bfb62a793e78f8ea39c0deb4a6216357447 |
| Author | Codex |
| Related Records | CR-20261128-194 |

## Summary

资料足够时展示完整拟用的树，资料无法决定归属时聚焦澄清。对新增、删去或移动分支的整理版取得用户决定后才能继续出稿。

## Context And Problem

首次校验已经能拒绝缺失的大纲、答复及不匹配的模块。会话中即便“确认”早于展示，原程序也能同时找到这两段文字。只在工具返回值中出现过的树也曾被当成展示依据。

## Sections Changed

| File | Section | Change Summary |
| --- | --- | --- |
| SKILL.md | 使用阶段与入口 | 将需要起草、解释或纠漏的输入转到展示与等待 |
| references/outline-gate.md | 起草与展示、采用依据 | 规定对照原件、展示实际完整层级、变更重展及两条出稿路径的停点 |
| scripts/check_outline.py | 会话原文定位 | 同一 JSON/JSONL 会话按消息角色与顺序核对实际展示和后续答复 |
| tests/test-point-discovery/test_outline_gate.py | 固定程序命令行测试 | 同一会话的顺序正反例、整份及逐行定位、内部工具输出反例 |

## Decision And Alternatives

程序核对可确定的会话角色、消息顺序、原文和当前范围；执行者结合上下文判断用户是否肯定本版及资料是否漏项。自然语言判断沿用既有职责分工，无需用户回复固定口令。

## Detailed Change

先运行门禁，等待期间可核源和澄清。只给例子、不能定位层级或补入明确遗漏时，展示范围，在聊天与文件两处停在正文前。若用户要求修改，展示更新后的版本。明确指定、结构和资料均合格的原树可直接采用。

## Impact Analysis

沿用原来请求、决定和证据格式。来自同一会话的确认增加顺序检查；历史问答和跨原件确认维持可回查的来源核对。阶段 3 规划、阶段 5 来源复核和阶段 7 评审继续生效。

## Validation Evidence

| Check | Command or Method | Result | Evidence |
| --- | --- | --- | --- |
| RED | 新负例经原 CLI 运行 | 出现 4 个错误放行 | 旧答复先于展示的 JSON、JSONL 及逐行 JSONL 各 1 个，内部工具输出 1 个 |
| GREEN | python -B -m unittest discover -s tests/test-point-discovery | 全部 21 项通过 | 调用真实 CLI，覆盖先展示后确认、旧答复和工具输出 |
| 包结构与记录 | validate_create_skill.py skills/test-point-discovery --require-change-records | validated-candidate，P0=0、P1=0、P2=1 | 保留既有中文描述触发措辞提示 |
| 新增内容检查 | git diff --check 与新增公开内容检查 | 缩进正常，未引入原件、用户身份或密钥 | 全部样例使用虚构模块 |

## Safety And Privacy

引用原始会话的位置、用户原话、业务原件与材料索引留在本机。公共记录仅列虚构场景、检查项和结果。

## Risks And Follow-up

固定程序无法判定业务树是否完整，也不能从 Markdown 中验证宿主身份。阶段行为覆盖按整批 #199 的实际 Skill 入口单独验证，CLI 结果只覆盖本票列出的命令行行为。
