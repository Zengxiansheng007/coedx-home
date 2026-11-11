# scripts-and-validation Change Ledger

## Purpose

追踪AT02与AT03对本分类的必要关联变更。

## Outline

| Date | Change ID | Section | Change Type | Summary | Status |
| --- | --- | --- | --- | --- | --- |
| 2026-11-11 | CR-20261111-002 | diagnosis | added | 流程诊断与验证 | applied |
| 2026-11-11 | CR-20261111-003 | 局部质量咨询 | added | 按需参考和验证 | applied |

## Detailed Records

### CR-20261111-002 - process-diagnosis

- Section changed: scripts-and-validation.
- Before: 基础导航，无专项诊断参考或行为材料。
- After: 实际版本对照、四类判断及局部恢复建议。
- Why: #101 REQ-004/008 AC-006/010。
- Impact: 仅ask-test及必要测试，不改原Skill。
- Validation: 见at02-validation.md；行为待Root验证。
- Detail record: [CR-20261111-002](../entries/2026/2026-11/CR-20261111-002-process-diagnosis.md).

### CR-20261111-003 - content-quality

- Section changed: scripts-and-validation
- Before: 基础导航无局部质量咨询操作。
- After: 条件入口、质量参考、模拟请求/独立rubric及返回原入口建议。
- Why: #102 AC。
- Impact: 只读咨询，不执行下游。
- Validation: 见详情与tests/ask-test/at03-validation.md；行为待Root。
- Detail record: [CR-20261111-003](../entries/2026/2026-11/CR-20261111-003-content-quality.md)
