# CR-20261128-175 · 批量评审与完整单例交接

| 字段 | 记录 |
| --- | --- |
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | changed |
| Scope | core-skill-md, references-and-assets, scripts-and-validation, downstream-and-handoff |
| Source | [规格 #175](https://github.com/Zengxiansheng007/coedx-home/issues/175)，工单 #176 至 #182 |
| Baseline | `460cb6ee782b9c52a7110933089e327fc5adf1a7`，技能 Git 树 `bd74a909c705f0da8670b0f1425cd1a7aa2ec938` |
| Author | Codex |

## Context And Problem

完整候选保存执行所需的输入、动作和逐步判据。批量评审需要在一条用例内辨认实际测试点、相对同版 P0 的差异、异常分叉与本例终点。独立执行者需要取得本次用例的全部操作和取证要求。

## Decision And Alternatives

同版候选作为业务定义的来源。先依据来源核对适用对象、时机和例外，再生成评审展示。单例使用自己的数据和状态。旧版整步引用继续通过既有的来源检查。

## Impact Analysis

覆盖首次混合稿、经授权的扩写、范围节选和按编号交接。业务执行使用当次的页面与接收端观测。对照中的上传方法、工位名称和样本计数仅用于验收。

## Validation Evidence

基线在 Windows 使用 `python -B -m unittest discover -s .agents/skills/test-case-authoring/scripts -q` 通过 203 项。规格对照的原 194 条候选文件 SHA-256 为 `ea352bfb632efffc0708901a5920621df162f5238251b361d9f17bf8446014a3`。两份仓库技能在基线各有 162 个文件。

## Safety And Privacy

用例运行由执行环境注入接收地址。验收记录使用合成数据与脱敏观测。
