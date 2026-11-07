# #84 实施与验证计划

## 准备状态与基线

工作树为 `workers/84`，分支 `codex/tpd-opt-84`。准备及实际 RED 源码为 `8369ca577ee6c8e403a2eac0c7bf70c22201fa2d`，依赖 #81 已集成。Root 在 #82、#83 产品修改期间派独立 actor 对此固定基线运行三轮模拟。Root 通知 #83 独立通过后，本轮已 fast-forward 合并最新 integration `fce9509b0fc035136c88828c29b4e45cf567efd7`，退出码0，准备文件与实际 RED 均保留。

## 已核对依据

读取任务根 CONTEXT.md、inputs/issue-79.md 的业务终点及共同交付约束、inputs/issue-84.md 全文、exploration.md 的 #84 与活跃验收条目。读取本工作树入口、module-clarification、writing-review、information-maintenance、async-exchange、workflow-lifecycle，以及 README 和 docs/development/verification.md。遵循 tdd、writing-for-agents、create-agent-skill 与 PowerShell 治理。测试边界沿用 #79 已确认的真实自然语言入口、逐轮实际模拟回答及可见产物。

## 当前证据与修复选择

information-maintenance 已逐操作识别对象、条件、字段和结果，并有同编号改名保存例子。async-exchange 已区分受理与最终结果，要求任务和业务对象关联。workflow-lifecycle 已核对同对象、关键起终点、条件与生效。未发现现行材料直接要求只测按钮可点击。

待补契约是逐项操作各自的本轮终点。明确业务效果直接成候选，仅对尚未明确且影响范围的终点实际提问。保存、取消和送审需保留各自结果、必要条件及同一对象关系，按已决定的范围止步。送审配置不代替送审结果。假设例子的草稿和审核端终点仅演示 Skill 行为，项目范围由对应资料和实际回答决定。

准备时以上仅为静态定位。现已完整回读 `red/round01-reply.md` 至 `round03-reply.md`、`candidate-v0.2.md`、`candidate-v0.3.md` 及 read-log。三轮实际入口已正确分别询问保存/送审终点，复用取消已知效果，按两次分别发送的回答形成同编号草稿及审核端待审核任务。没有已证实的本票核心入口失败，具体逐 AC 结论见 `red.md`。本轮是补充明确契约、限定示例和活跃验收，GREEN 核对既有行为保持，不宣称修复一个已观察失败。

RED 首轮完整候选 v0.1 未及时快照，原 `candidate.md` 已在第二轮更新至v0.2。原首轮回复与问题/来源记录真实保留，v0.2快照及v0.3完整可读。本轮保留该限制，未重建v0.1。

## 预定写集

- `skills/test-point-discovery/SKILL.md` 中分析、编写或完成判定的直接相关入口。
- `references/information-maintenance.md` 作为操作结果与终点的具体指导，含限定假设例子。
- `references/module-clarification.md`、`writing-review.md` 中实际承接问答、写点与自检的必要规则。
- `references/async-exchange.md`、`workflow-lifecycle.md` 中受理、流程与每项操作终点关系的必要说明。
- `tests/test-point-discovery/` 下本票活跃普通请求、模拟资料、独立 rubric，及现存直接相关活跃判据。
- `evidence/optimization/84/` 下计划、普通输入、逐轮实测、身份与验收记录。

已读 #82、#83 plan/verification、reviews/83.md、merges/83.md，并回读合并后的维护、编写、异步及流程材料。#82 已建立共用范围与真实差异，#83 已建立规则级表达。现收窄产品写集为入口 SKILL、information-maintenance、writing-review、async-exchange、workflow-lifecycle 共五份。module-clarification 已有充分的独立/依赖、部分回答、仅不知道及明确暂留规则，本票直接复用。其余活跃材料增加本票 request/input/rubric，并在直接相关流程 rubric 增加操作终点判据。历史 run、session、demo、RED 输出和固定哈希检查保留原身份。产品限定为本地 TPD 指令材料，沿用现有能力，无新增框架、依赖或语义关键词判分器。

## 逐片行为验证

Root 给 actor 的输入仅为普通 request 和 input，rubric 与本计划留给主持和评审。各轮标记 SIMULATION，保留实际请求、回答、展示版本、读取身份、文件和剩余状态。actor 等待真实发送的模拟回答。

第一片先观察当前入口如何承接已知取消效果及未决定的保存、送审终点。Root 仅在 actor 实际询问后发送保存止于同对象草稿产生的选择，并故意暂不回答送审。观察部分回答是否只绑定保存，送审仍保持必要询问。第二片由 Root 实际发送送审止于审核端收到同一任务的选择，再请求形成候选。允许独立问题同轮提出，不固定问题数量或措辞。

实际 RED 已完成且核心行为通过，按上文保留通过事实。GREEN 使用隔离新 actor 在修改后的准确源码版本复走同一普通请求及 input，Root 逐轮发答复。取消明确效果直接进入候选，保存与送审分别展示实际决定的终点，保持任务标识、已知状态和条件，不自行添加审批结束或送达范围。GREEN 每次候选更新前保存已展示的完整版本，新稿使用独立路径。

## 验收与检查

按 issue-84 的五项 AC 对实际输出定位通过、失败或未验证，重点核对结果与对象、每项操作止步位置、明确规则复用、部分回答和未知问答机制、假设身份。候选仍待具体评审，模拟决定保持模拟身份。

定向检查文件 diff、Markdown 结构、链接和引用可达、活跃判据一致性及历史产物保真。最终统一 `tools/checks.py` 由 Root 在集成侧运行。本票不重复触发全仓检查。实现完成提交并合并最新 integration 后返回实际 commit、逐 AC 证据及剩余限制。真实业务和 XMind 客户端均不在本票模拟结果内。

已在上述实际实现基线完成五份产品文件修改及定向检查。产品现按 source-manifest.json 冻结，静态结果和限制见 verification.md。Root已收到GREEN入口及固定manifest，等待实际逐轮输出后补行为结论，期间产品源码保持冻结。

GREEN三轮已完成，已完整回读全部实际response与独立candidate版本。逐AC限定结论、P1超限规则与P5普通草稿的实际表达、源码及输入身份复核和RED快照限制均已补入verification.md。产品冻结期间未修改。当前integration仍为fce9509，提交前后合并该tip并返回实际HEAD。Root已允许唯一未跟踪本地自动治理日志例外，其他本票内容全部提交。
