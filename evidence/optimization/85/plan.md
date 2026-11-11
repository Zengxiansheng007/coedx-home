# #85 准备计划

状态为准备。2026-11-07，worker 分支 codex/tpd-opt-85，读取基线 8369ca577ee6c8e403a2eac0c7bf70c22201fa2d，初始工作树干净。等待 Root 通知 #82—84 集成后，先合并当前 integration，再核对实际差异和写集，随后执行 red → green。当前未执行入口，未修改产品，未判通过。

2026-11-07 前置复核更新。Root 已在原 8369ca577ee6c8e403a2eac0c7bf70c22201fa2d 运行三轮入口，真实产物保存在 red/，详见 baseline-review.md。前述“未执行入口”只描述准备时点。当前 worker 已通过受控 runner fast-forward 至 fce9509b0fc035136c88828c29b4e45cf567efd7，包含 #82/#83。仍未修改产品，等待 #84 集成与 Root 源码写入通知。

2026-11-07 实施前重核。Root 已明确授权本票唯一产品写入，worker fast-forward 至已接受 #84 的 922493c2403b3fb8f11ab73e391df39c3915db41。重读已提交 writing-review 操作结果契约、reviews/84.md，并核对其五份产品文件均与此前只读 source-manifest.json 的冻源物理 SHA256 相同。#84 已承担逐操作结果/终点，本票只补写作中新缺口的局部往返与核源。产品准确写集收敛为 SKILL.md 与 references/writing-review.md，不改 module-clarification.md 或另三份操作参考。

活跃材料新增 tests/test-point-discovery/optimization-85-request.md、optimization-85-rubric.md、fixtures/optimization-85-input.md，并在原 writing-request.md 与 rubric.md 的编写入口处连接本票判据。实际 fresh GREEN 仍用原 evidence/optimization/85/request.md 与 input.md，输入不预补编辑保存结果。原三轮 baseline 保留，正向行为不改称失败。实施后冻结19份产品MD及原请求/输入物理身份，定向格式/本地引用/空白检查后通知 Root 派fresh actor。当前额度为一次三轮baseline，fresh GREEN未执行，无数值限制。

## 依据与现有缺口

已读任务根 CONTEXT.md、inputs/issue-79.md、inputs/issue-85.md、exploration.md 的 #85/七类参考/活跃验收条目，以及 tdd 的 SKILL.md、tests.md、mocking.md、writing-for-agents、create-agent-skill 和 PowerShell 治理。直接规格沿用 .scratch/test-point-discovery-research-20261105/优化开发规格-v0.1.md 的 AC-009。

当前 #81 已实现真实问答、明确暂留及唯一产品区。writing-review.md 的首段、自检和同文结构仍缺写作中新缺口如何局部回到澄清、暂留引用怎样定位、后续答案怎样只恢复受影响内容的具体步骤。入口第8步仍以完成澄清后编写为主。以上是静态缺口观察，行为是否失败待实走入口，不冒充 red 执行。

## 本票写集与复用

预定产品写集为 skills/test-point-discovery/SKILL.md、references/writing-review.md、references/module-clarification.md。后两份承担具体往返与产品问题结构，入口只保留触发指针。合并后重核七类组织参考及活跃 tests/test-point-discovery/writing-request.md、rubric.md，发现直接相反要求时限定同步修正。历史 demo、session、run 和旧 hash 检查保持原身份。

新增本票普通请求、模拟输入及隔离评审标准复用既有 Markdown 入口，不增加框架、解析器或语义关键词判分。行为测试切入点已在 #79 确认，观察实际问答、展示范围及文件。Root 派隔离 actor，actor 只读实际产品与普通请求/输入，逐轮等待 Root 真正发出的模拟回答。

## 定向验证与逐项验收

1. 初始输入提供已确认范围及明确规则，让 actor 实际编写。随后 Root 根据实际稿件提供真实的新增写作检查材料，观察重叠成员计数缺口是否实际回问，只暂停人数相关预期，其余标题、选择和保存结果继续保持待评审身份。
2. Root 依据实际问题答复。明确暂留前，未知保持未答。明确转产品后，核对对应模块顶部完整问题、受影响条件及分支、真实决定，正文短引用可双向定位且没有去重等猜测预期。
3. Root 后续明确答复计数规则，核对只恢复受影响分支，永久原问题/答复与有效规则保留，未重问所有已确认项。该答复仅授权候选修改，具体评审、准确 MD 和交接仍按用户实际决定分别处理。
4. 对照 #85 五项 AC 逐项语义审查，同版证据标明通过/失败/未验证。执行 git diff --check 及受影响文件结构检查，Root 最终执行 tools/checks.py。真实 XMind 客户端、真实业务、全局安装、下游与远程操作均在本票行为验证范围外。

写作材料的新信息由 Root 在前一轮完成后实际发送，不预填会话或最终产物，不要求 actor 故意漏读可见材料。若 actor 在初始写作中已识别人数歧义，Root 直接按其实际问题推进，记录实际发现时机。

## 额度与结束条件

此优化任务无数值额度。本准备轮仅创建计划和测试材料，入口执行次数为0，产品修改次数为0。完成需保留真实 red/green 及逐AC证据，定向验证通过、提交实际写集，并合并最新 integration 后交 Root 独立评审。

2026-11-07 完成核对更新。实际累计为baseline三轮与fresh GREEN三轮各一次入口会话，产品源码一次冻结，冻源后无新增产品修改。GREEN三轮的五AC核对与静态/身份结果见verification.md、static-checks.json、post-green-identity.json。所有21份冻源产品及原输入匹配。Root最终全仓验证与独立整票审查另行执行，当前准备提交实际写集并核对集成祖先。
