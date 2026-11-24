# CR-20261117-114 - 从材料落实专业生成判断

| Field | Value |
| --- | --- |
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed / validation |
| Scope | core-skill-md / references-and-assets / scripts-and-validation / downstream-and-handoff |
| Source | RTA-03；已确认阶段交付v0.3及评审复用/公共操作要求 |
| Baseline | 2202ebc0c5a7b77d9ab02c62284e6dd744828a53 |
| Author | Codex |
| Related Records | CR-20261117-105 / CR-20261116-005 / CR-20261111-201 |

## Summary

把来源解释到候选形成的专业判断集中为可执行流程，直接从所有编写入口触达；
保留现有schema、公开API、唯一问答及专业职责。

## Context And Problem

限定试用中，来源示例被机械搬成英文步骤，准备按预设步数切分；技术阶段成为目录，
逐例分级套用相同风险/频次，独立业务结果折为一个全包方面后宣称覆盖。渲染器无法
补做这些判断；仅重渲染旧候选或加词语过滤均不能解决来源解释缺失。

## Sections Changed

| File | Section | Change Summary |
| --- | --- | --- |
| SKILL.md | 入口、扩展、验证 | 在候选构建前执行专业生成核对 |
| references/professional-generation.md | 新专业流程 | 材料、路径、目标/准备、独立方面、分级、还原回读 |
| references/source-semantics.md | 入口 | 明确先解释完整来源再归属动作/数据/结果 |
| references/goal-preparation.md | 归属 | 逐动作按目标/消费者切分，不用固定前缀 |
| references/extension-contract.md | design构建 | 使用具体观察方面和逐例分级理由 |
| references/chat-delivery.md | 交付前核对 | 比较当前来源、候选及实际文件 |
| scripts/test_generation_inputs.py | 公开接口 | 部分覆盖、逐例理由与准备边界保留 |

## Decision And Alternatives

复用既有结构与检查边界，新增一份直接可达的专业rubric。各参考只放职责相关
指针或必要澄清，不复制流程全文。不新增强制分析JSON、平行问答或自证专业质量包。
程序只能核对结构、关联和已给内容保留，无法判断自然语言方面是否完整；真正质量
由独立上下文从材料完整生成后按REQ/AC审查。未编写关键词或中文字符检测测试。

## Detailed Change

真实功能路径不使用生成阶段/分级分组；保留合法界面原文和数据原值。每例按目标、
初态与终点确定完整准备及操作，在当前消费者处获取本次值；公共范围与例外、空
特殊项省略、无来源不新增后置、P0整步复用及内部完整还原仍依各原契约。
独立结果拆为可观察方面，覆盖缺项具体保留；等级复用有效决定并逐例解释实际影响
和触发频次，实质新变化才回原问答。压缩只合并等价含义，技术来源不变业务操作。

## Impact Analysis

REQ-007/008/009/010/012/014/016/017/018/022，关联AC-008/009/010/014/019/021/022/033。
本票修复编写指引，不改变反馈、聚合、QA或公共适用性实现；canonical与.agents镜像
同步维护。旧试用及内部材料不提交，不更改需求、原P0、全局Skill或历史证据。

## Validation Evidence

| Check | Command or Method | Result | Evidence |
| --- | --- | --- | --- |
| 公开接口 | Python311 -X utf8 -B -m unittest -v test_generation_inputs test_source_semantics test_goal_preparation test_extension test_business_hierarchy | 22/22通过，exit 0 | 本票public-preservation-workspace-temp输出 |
| TDD边界 | 指引与合成保留测试，无生产实现变化 | 无代码red/green声明 | 公开测试不代替语义验收 |
| Skill静态检查 | validate_create_skill.py --require-change-records | exit 1；3项既有合成secret-pattern负例，与实际基线findings完全相同，无新增 | 本票skill-validation与package-check |
| 镜像/链接/差异 | 逐文件字节身份及diff检查 | 本票13个文件canonical/.agents一致；静态链接/记录无新增问题 | 本票package-check；git diff --check |

首次两次测试启动仅因受控运行器固定WorkspaceRoot，模块未加载；记录原输出，不算
产品失败。之后有效运行21/22，CLI在默认App沙盒临时目录替换文件报WinError5，
当前与未改生产代码基线均复现。仅在测试子进程使用本票授权目录作为TEMP/TMP，
同组22/22通过；未改系统环境、测试源码或产品。全部失败与诊断输出保留。

## Safety And Privacy

新增示例仅合成订单，未嵌入真实业务资料、凭据或本机内部材料。未安装、发布、
修改远端工单、运行模型/业务或替换全局Skill；范围确认不变成具体稿通过。

## Risks And Follow-up

仍是applied candidate。独立fresh-context无预期成稿提示的完整生成、逐REQ/AC质量
评审及真实反馈/恢复联验由后续票进行；用户具体稿评审、XMind客户端和业务执行
保持各自边界。结构回归通过不宣称专业质量已通过，不以模拟用户代替真实批准。
