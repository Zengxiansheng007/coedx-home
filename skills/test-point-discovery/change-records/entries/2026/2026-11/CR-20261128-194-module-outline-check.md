# CR-20261128-194 - 首次调用核对模块大纲

| Field | Value |
| --- | --- |
| Status | validated |
| Target Skill | test-point-discovery |
| Change Type | changed / validation |
| Scope | core-skill-md / references-and-assets / scripts-and-validation / safety-and-governance |
| Source | #194，父规格 #193，AC-002～004 |
| Baseline | 5abc3b4420296cbc81466a82914ccafe8e9ee4af |
| Author | Codex |
| Related Records | CR-20261110-001 |

## Summary

首次调用逐模块运行同一固定程序，引用原范围与用户实际采用或确认，允许就绪模块进入后续前提核对。

## Context And Problem

原入口以阶段 3 的规划和阶段 5 的业务复核支持集中编写，缺少对当前大纲的独立校验。

## Sections Changed

| File | Section | Change Summary |
| --- | --- | --- |
| SKILL.md、references/stage-entry.md | 首次调用 | 转到逐模块固定程序 |
| references/outline-gate.md | 正式输入和行为 | 树、拟写范围、原话、原答复和受阻停点 |
| scripts/check_outline.py | 只读命令 | 输入核对、作用域、版本和可回查的用户证据 |
| tests/test-point-discovery/test_outline_gate.py、.github/workflows/check-skills.yml | CLI 测试 | CI 在两种操作系统发现测试 |

## Decision And Alternatives

分开保存本次请求和当时的用户决定。固定程序核对字节、角色标记、原文、模块、结构和路径；实际消息含义、别名和层级归属需逐项读原件。历史自然语言答复可直接引用。

## Detailed Change

同一结果用于聊天和文件。缺少树、资料、真实采用依据、当前模块或版本对应时保留读资料和提问。程序不写文件。

## Impact Analysis

大纲属于当前模块编写前提之一，仍需阶段 3 规划和阶段 5 来源覆盖复核。CI 中独立运行本目录标准库测试。

## Validation Evidence

| Check | Command or Method | Result | Evidence |
| --- | --- | --- | --- |
| RED | 通过实际 Python 命令调用新入口 | 基线缺少程序；新增负例曾发现跨模块、越范围、无真实引文等错误放行 | CLI 返回码及断言 |
| GREEN | python -B -m unittest discover -s tests/test-point-discovery | 19 项通过，16 个门禁测试及 3 个既有 XMind 测试 | 直接分派子进程读取临时原始记录 |
| 历史问答兼容 | 本地两份原问答 | 三处不同格式的真实用户答复均可原样定位 | 限原件定位能力，内容与原文仅留本地 |
| 包结构和变更记录 | validate_create_skill.py --require-change-records | P0=0、P1=0、P2=1，validated-candidate | 既有中文 description 的英文触发措辞提示 |

## Safety And Privacy

提交仅含借阅等虚构样例、测试代码、过程约定和匿名验证数量。原始业务资料及用户确认留在本机。

## Risks And Follow-up

本条登记固定程序开发验证。Agent 仍负责读原件并解释实际用户意图；本地证据索引本身无法签发宿主许可。自然语言正式入口的聊天及文件阻断和最终稿独立业务对照，在 #199 绑定整合后的交付版本验收。
