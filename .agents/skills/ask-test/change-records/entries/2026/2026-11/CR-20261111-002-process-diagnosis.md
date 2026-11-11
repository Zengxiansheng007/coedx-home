# CR-20261111-002 - Process diagnosis

| Field | Value |
| --- | --- |
| Status | applied |
| Target Skill | ask-test |
| Change Type | added |
| Scope | core-skill-md / references-and-assets / scripts-and-validation |
| Source | user-authorized #101 REQ-004/008 AC-006/010 |
| Baseline | c39fe70aa5511acce9c58818b00a30cf61095f13 |
| Author | Codex |
| Related Records | none; AT01 created package |

## Summary

新增按实际规则和记录诊断流程偏离的咨询分支。

## Context And Problem

基础导航尚未指导未问即暂留及历史版本不明时的差异核对与四类判断。

## Sections Changed

| File | Section | Change Summary |
| --- | --- | --- |
| SKILL.md | pointer / validation | 接通诊断与行为请求 |
| references/process-diagnosis.md | all | 规则对照、归因、局部恢复 |
| tests/ask-test/process-request.md / process-rubric.md / fixtures/process-records.md | all | 有依据偏离与证据不足模拟 |

## Decision And Alternatives

按需参考替代长主入口模板；动态读规则替代缓存。真实actor由Root主持，静态词命中不能证明行为。

## Detailed Change

以实际版本、记录边界、差异及影响支持判断，保留有效工作，仅建议局部恢复。

## Impact Analysis

只扩展ask-test及必要测试；四个原Skill、业务状态和外部系统不变。共享入口由独立集成处理。

## Validation Evidence

| Check | Command or Method | Result | Evidence |
| --- | --- | --- | --- |
| structure / records | create-skill validator --require-change-records | see actual run | tests/ask-test/at02-validation.md |
| behavior | fresh actor via Root | not run by implementer | process-request.md / process-rubric.md |
| sensitive data | review added synthetic text / diff | no credentials or business data | marked synthetic fixture |

## Safety And Privacy

虚构资料，无凭据、外部模型、安装或业务写入。只读是行为约束，不声称独立宿主强制能力。

## Risks And Follow-up

实际语义及宿主调用待独立验证，不提前宣称通过。A规则身份由主持提供；B历史身份未知保留。

Refs: #101; spec REQ-004/008 AC-006/010.
