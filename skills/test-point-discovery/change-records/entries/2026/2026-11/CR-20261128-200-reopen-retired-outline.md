# CR-20261128-200 - 清空后恢复模块大纲

| Field | Value |
| --- | --- |
| Status | validated |
| Target Skill | test-point-discovery |
| Change Type | fixed / validation |
| Scope | references-and-assets / scripts-and-validation / safety-and-governance |
| Source | #193 整批评审，#197 的已确认范围修订 |
| Baseline | b4e15df2d912bcf90c235464c319e7504790c258 |
| Author | Codex |
| Related Records | CR-20261128-197 |

## Summary

完成最后一叶的清空确认后，可用原决定展示下一次新增差异。两个渠道写入第一叶前仍须取得对新增版本的确认。

## Context And Problem

校验程序允许针对最后所有旧叶确认删除；下轮恢复历史时却要求旧树非空，无法得到可展示的差异。

## Sections Changed

| File | Section | Change Summary |
| --- | --- | --- |
| scripts/check_outline.py | 历史决定验证 | 复核空版本对应的清空差异和用户答复 |
| references/outline-gate.md | 已采用范围的修订 | 说明清空后恢复与新增叶确认的顺序 |
| tests/test-point-discovery/test_outline_revision.py | 命令行接续 | 用连续决定验证空基线、第一叶与下一次续写 |

## Decision And Alternatives

沿用旧清空决定内已引用的原展示和用户答复，旧决定文件可直接作为 `previous_decision`。本修复采用 minimal-change，保留现有记录格式。

## Detailed Change

仅在回查历史且记录明确为 `branches: []` 时验证清空依据。该确认须引用本模块从另一版本变更到本空版本、并列出移除叶的展示。当前新树和拟写范围仍按原规则检查。

## Impact Analysis

已清空的模块只能用该历史作差异比较。新增正文的本轮确认、阶段前提和非空范围要求继续生效。其他模块的决定和仅有空标题的初稿不能恢复清空状态。

## Validation Evidence

| Check | Command or Method | Result | Evidence |
| --- | --- | --- | --- |
| RED | 以原版本 CLI 接续真实生成并确认的清空差异（合成会话） | 复现 | 返回阻断，缺少新增差异 |
| GREEN | `python -B -m unittest discover -s tests/test-point-discovery` | 32 项通过 | 清空待确认 → 确认删除 → 新增待确认 → 确认写入 → 使用最新决定续写；无清空依据、缺答复及错模块等均阻断 |
| 结构与追溯 | `validate_create_skill.py skills/test-point-discovery` 及其 `--require-change-records` 模式、`git diff --check` | 通过 | P0/P1 均为 0，保留包级原有中文触发措辞 P2 提示 |

## Safety And Privacy

回归使用临时目录、合成分支和模拟用户消息。检查本次差异，未发现凭据、真实业务附件、原始会话或本机路径。

## Risks And Follow-up

文字对应的业务含义仍由执行者回读原会话确认。本次验证固定程序；交付入口的独立实稿验收归 #199。
