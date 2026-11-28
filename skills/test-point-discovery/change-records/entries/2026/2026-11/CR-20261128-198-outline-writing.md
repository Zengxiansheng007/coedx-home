# CR-20261128-198 · 按大纲精简编写

| Field | Value |
| --- | --- |
| Status | validated |
| Target Skill | test-point-discovery |
| Change Type | changed |
| Scope | core-skill-md / references-and-assets / downstream-and-handoff / scripts-and-validation |
| Source | #198，父规格 #193 的 AC-007～009 |
| Baseline | 5abc3b4420296cbc81466a82914ccafe8e9ee4af |
| Author | Codex |

## Summary

按当前已确认的大纲集中写出本模块的可观察规则，在说明区保留各输入对应的原执行材料。

## Context And Problem

基线示例将单一上限及超限处理列在并列节点。已有去除业务编号、合并公共规则的约定，未交代如何逐种定位合写输入的样本及既有用例。

## Sections Changed

| File | Section | Change Summary |
| --- | --- | --- |
| SKILL.md | 操作 8 | 进入基于当前大纲的编写参考 |
| references/writing-review.md | 共用表达、短节点与名称标记 | 同一条规则交代阈值及结果，合写时逐种保留输入和执行去向 |
| references/single-file-handoff.md | 同文说明模板 | 接收者沿分支回查样本、方法和编号 |
| tests/test-point-discovery/outline-writing-{request,rubric}.md（仓库根目录） | 合成回归 | 用独立业务场景复查精简稿及执行覆盖 |

## Decision And Alternatives

沿用同文件说明区与既有执行材料。每个真实业务差异在正文有对应条件和预期，合写时将各输入逐一对应到执行条目。现场未知的覆盖去向保留具体缺口。

## Detailed Change

父节点保留共同条件，分支由方式、平台或调用阶段引起的结果差异决定。目标平台预期和其他平台的历史观测各自标明归属。原有用例的样本、取证与比对方法通过映射回查。

## Impact Analysis

影响阶段6编写、局部修订及阶段8说明区。工作流沿用既有具体稿评审、下游执行和未知事项处置约定。

## Validation Evidence

| Check | Command or Method | Result | Evidence |
| --- | --- | --- | --- |
| 基线与修改后示例 | 对示例叶节点检查上限与拒绝结果是否同处一行 | 基线失败，新示例通过 | 基线 5abc3b4 的写作参考示例及本次差异 |
| AC-007～009 局部成稿 | 从已确认业务决定生成局部候选稿，沿父子节点和映射核对；按 id 回读已存在的执行材料 | 上限及提示共处一个节点，输入形态、各方式结果、五种格式及产物一致性可判读；9 个分支的两种方式各自定位，共 18 个原条目 | 本机保留稿件、执行资料版本及校验输出，公开仅记录脱敏结果 |
| 结构与追溯 | validate_create_skill.py，另加 --require-change-records | 两次均 P0=0、P1=0、P2=2 | 当前票保留原描述触发词与脚本目录引用提示；包内索引及分类记录可回查本条 |
| 既有读取器回归 | pytest tests/test-point-discovery/test_xmind_reader.py -q | 3 passed | 仅验证原有读取器 |

## Safety And Privacy

公开回归资料采用虚构的会议席位预约。目标业务的文档、路径、样本、原编号和用户答复保存在项目本机。本票差异按本机账号、绝对路径及凭证模式检查。

## Risks And Follow-up

本票验证文档的表达和执行材料的引用。#199 在实际整批交付版本上独立编写、定标并核对全稿。应用执行需另有设备证据。
