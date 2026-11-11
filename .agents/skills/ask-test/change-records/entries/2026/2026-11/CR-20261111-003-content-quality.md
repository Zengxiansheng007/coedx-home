# CR-20261111-003 - 局部质量咨询

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | ask-test |
| Change Type | added |
| Scope | core-skill-md / references-and-assets / scripts-and-validation / downstream-and-handoff |
| Source | #102 / spec #99 REQ005/008 AC007/010 |
| Baseline | c39fe70aa5511acce9c58818b00a30cf61095f13 |
| Author | Codex |
| Related Records | AT01基础入口 |

## Summary

增加按需质量参考和独立请求/fixture/rubric，咨询止于建议。

## Context And Problem

基础入口没有测试点组织、共同子规则、粒度与用例预期的局部判断操作。

## Sections Changed

| File | Section | Change Summary |
|---|---|---|
| SKILL.md | 针对性质量咨询 | 条件指针 |
| references/content-quality.md | 全文 | 共同依据、差异、粒度、预期与边界 |
| tests/ask-test/content-quality-*、fixtures/quality | 全文 | 三个隔离模拟场景及独立评审 |

## Decision And Alternatives

复用实际TPD writing-review.md（共用子规则、必要条件与已知结果、表达不等于次数）及TCA batch-contract.md（预期与可观察验证、未知不填默认），按需查实时适用规则，不复制完整流程。无脚本或新框架。

## Detailed Change

先核共同依据再建议共用与真实差异；同名不自动合并。组织和预期仅局部示意；覆盖建议保留待用户决定。正式修改与评审返回原入口。

## Impact Analysis

只影响用户明确调用后的质量咨询分支；原四Skill、业务与状态不变。无安装、模型外发或发布。AT02共享入口指针由集成者协调。

## Validation Evidence

结构与引用检查待实际validator结果；真实行为由Root统一组织actor并独立评审，当前未验证。见 tests/ask-test/at03-validation.md。

## Safety And Privacy

fixtures全部虚构无凭据。检查源码及测试新增内容；前后业务/Skill与状态由Root动作记录+hash比较。无硬门或宿主接受声明。

## Risks And Follow-up

候选包；宿主触发未验证。实际行为与独立审查完成后由Root更新证据状态。

Refs: #102；docs/specs/testing-skill-navigator-v0.1.md。

