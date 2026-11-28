# CR-20261128-184 · 人工评审与 Agent 执行视图

| 字段 | 内容 |
| --- | --- |
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | changed |
| Scope | core-skill-md, references-and-assets, scripts-and-validation, downstream-and-handoff |
| Source | [规格 #184](https://github.com/Zengxiansheng007/coedx-home/issues/184)，工单 #185 至 #191 |
| Baseline | 主线提交 `654bdc663ad276d0e54093cbcdee5180a2977d2d`；两个技能目录的树均为 `e8615bed8383fd06ba21abb7481c4092137cee67` |
| Related Records | CR-20261128-175 |

## Summary

全量、编写中和合入前交付分别列出本轮用例，人工在评审稿中阅读操作、输入和预期，执行者按同版编号取得完整单例。

## Context And Problem

原评审稿把对象拆成字段行，复制到输入框时需要重新拼装。复用操作段和复用调用输入也有不同的适用范围，异常调用有自己的终点。

## Decision And Alternatives

每次调用提供可独立复制的 JSON 子主题。评审者从注明的 P0 调用复制并按变化修改，执行者读取当前用例的完整输入。两者共用候选中的动作、数据和判据。

## Sections Changed

| 范围 | 职责 |
| --- | --- |
| 技能入口与交付参考 | 选择两种读者视图、对应调用和同版单例 |
| 投影、保存与反馈脚本 | 生成调用输入、引用、运行资料索引和编辑建议 |
| 公开入口回归 | 分别检查交付范围、输入结构、编辑作用范围和异常回传 |

## Detailed Change

见规格的 REQ-011 至 REQ-017。范围和反馈按实际交付来源核对，运行中的临时输入仅属于本次操作。

集成审查修复在同一版本中核对直属用例编号、原业务目录和真实子树绑定。正文修改复用原有可编辑字段映射；新增与保留入参键分别核对所指的 P0 输入。明确本轮排除的记录仍保存在候选，交付的两种视图同步收窄。

## Impact Analysis

评审稿的显示格式和 Agent 交付入口发生变化。原来的按候选取单例接口继续服务已有调用者。

## Validation Evidence

基线技能回归 229 项通过。[双入口复制验收](https://github.com/Zengxiansheng007/coedx-home/blob/feat/184-reader-views/evidence/spec-184/191-copy.md)记录实际导入的三个版本及用户回传。

修复阶段通过日常 Markdown 回传入口核验改名、角色、独立验证点、原测试点、乱序与同名、旧稿澄清和整例省略；三个交付阶段核对当轮排除。另在真实的完整候选上读取编号 056 的范围稿，将第二步预期的演练改动准确定位到该步第一项预期，原稿保留。

技能脚本回归 258 项通过，仓库两份目录的 187 个文件逐项一致。`validate_create_skill.py --require-change-records` 仍报告基线已有的三处测试夹具 secret-pattern，状态为 rejected。本次修复未修改这些夹具。

## Safety And Privacy

对外证据仅记录已核实的行为、统计和脱敏标识。原始业务候选、复制文本、实际接收地址及截图保存在本机。

## Risks And Follow-up

客户端核验适用于本轮 Windows XMind 的导入和文字编辑操作。客户端或主题格式变化后需重新核验剪贴板结果。
