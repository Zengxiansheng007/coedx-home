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

## Summary

批量阅读与单独执行共用候选版本和用例身份。评审稿标明同版 P0 的共用段、目标用例自己的变更及分叉后的步骤。

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

## Sections Changed

| 位置 | 职责 |
| --- | --- |
| SKILL.md 及其编写、范围与交接参考 | 进入来源评估、批量评审和点名单例 |
| scripts/review_segments.py | 以候选和源数据绑定连续 P0 段，保留本例的完整业务步骤 |
| scripts/source_preparation.py | 核对全模块适用关系，输出公共定义、例外和受影响用例 |
| scripts/run_evidence.py | 按本次可关联的证据区分业务失败与待取证 |

## Risks And Follow-up

XMind 桌面导入需要人工核对。真实设备的判定依赖本次页面和接收端观测。历史基线的三个负向测试文件会触发 create-skill 扫描器的模拟凭据模式，基线与交付版分别记录扫描结果。
