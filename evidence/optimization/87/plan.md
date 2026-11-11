# #87 实施准备

最初准备基线为 #85。现已合入正式 #86 集成 head，并重核源变更，等待 Root 派 fresh actor 运行实际 RED。产品源码保持该基线，待实际 RED 冻结后才修改。

## 版本与边界

- 工作区为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/87`，分支 `codex/tpd-opt-87`。
- 准备时 HEAD 为 `0fbe08efcb34f42c5b6a72c4c9129018620d95c6`，工作树原本干净。它包含 #85，不包含待合并的 #86。本文件不将 #86 视为已集成。
- 本阶段写集仅为本目录的 plan.md、request.md、input.md 和 rubric.md。尚未执行入口、修改产品或登记通过。
- 限定本地 Skill 指令及必要活跃验收材料。历史结果保持原身份。原 grill Skill、覆盖扩展、工程 Skill、UIT/TCA、全局安装、下游、业务、远程均在本票写集外。

## 本轮核对来源

所有任务路径均从 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107` 起算。

- `CONTEXT.md` 的 Local workflow、Tools and safety，`status.md` 的依赖及 #85 实际引用限制，`exploration.md` 的 #87、活跃验收和 grill 适配部分。
- `inputs/issue-87.md` 的全部六项 AC，`inputs/issue-79.md` 的 US-35—38、42、覆盖与模块推进、TPD-OPT-AC-011 和高层自然语言入口。
- `C:/Users/lenovo/Documents/ChatGPT/ui-test/.scratch/test-point-discovery-research-20261105/优化开发规格-v0.1.md` 的覆盖、模块推进与更新及 AC-011，`优化细节设计-v0.1.md` 第6节。
- 当前工作区 `skills/test-point-discovery/SKILL.md`、`references/module-clarification.md`、`references/writing-review.md`、`references/review-and-progress.md`，以及 `tests/test-point-discovery/progress-request.md`、`clarification-requests.md` 的实际逐轮请求骨架。
- `C:/Users/lenovo/.codex/skills/tdd/SKILL.md`、tests.md、mocking.md，`writing-for-agents/SKILL.md` 和 `create-agent-skill/SKILL.md` 的入口、渐进披露与完成条件要求。统一协议仅用于独立技能回流，无新 develop-system 运行。
- 已实际只读核对 `C:/Users/lenovo/.codex/skills/grill-with-docs/SKILL.md` 的问题格式、事实查证，`references/interview-record.md` 的永久问答与历史，`C:/Users/lenovo/.codex/skill-extensions/grill-with-docs-coverage/extension.md` 第1—4节与 record.md。只适配必要契约。

## 既有行为与待确认缺口

准备基线已有先查事实、保存真实答复、部分回答追问、局部恢复和同一准确 MD 回读。`module-clarification.md` 每轮回查原输入，但没有完整的稳定 B 编号、临时有界覆盖区与永久决定位置契约。`review-and-progress.md` 更新后直接进入下一模块，缺少本轮覆盖复核、永久依据回读、限定清理及清理后编号不复用规则。这是静态缺口，尚无 #87 行为 RED 结果。

原基线的整分支重印属于 #86。本票待合入 #86 后复核，不重复修复已由依赖处理的要求。保留 #82 共用与差异、#83 规则粒度、#84 操作终点、#85 局部回问、#86 聚焦评审与同一路径更新。

## 正式实施预期写集

正式集成后核定逐文件写集，最小候选为 `skills/test-point-discovery/SKILL.md`、`references/module-clarification.md`、`references/review-and-progress.md`、`references/writing-review.md` 及本票活跃请求/rubric。若检索发现同一契约在其他活跃参考中冲突，再记录必要关联修改及理由。本 Skill 不在 skill-packages 的既有三个分发副本中，无需新增副本。

逐轮覆盖与单份过程记录的字段定义集中放在澄清参考，评审推进引用它执行安全收尾。一个过程 MD 同时承载临时覆盖区和区外永久问答/决定，准确测试点 MD 继续只有一个。B 是过程分支编号，Q 是问题编号，二者与业务测试点身份分开。每条永久依据使用实际文件绝对路径、版本和章节，避免 #85 的 source 简写问题。

## RED → GREEN 计划

1. Root 提供 #86 正式集成 head 后合入 worker，回读相关入口/参考并更新本文件实际基线。
2. 请求 Root 派 fresh 真实入口 actor。actor 只收到 request.md、input.md、准确 Skill 路径与输出目录，rubric 留给主持及独立语义评审。Root 根据实际输出逐轮发送模拟答复。
3. 先观察当前版本。按实际行为登记 RED、已有正确行为或未验证，保留各轮输出和实际文件。发现一个直接缺口后做对应最小指令切片，再用新输出目录真实运行 GREEN，不重写 RED。
4. 分轮检查来源、新条件、漏答/部分/未问、事实与依赖，实际暂停再读文件恢复。具体评审与准确 MD 更新前后保存可观察文件身份。待收尾条件满足后实际先写永久内容并回读，再只删已收尾临时行，并回读其余内容。
5. 双模块继续中引入真实新条件，核对只重开受影响部分、历史及未变决定保留、B/Q 编号递增。主持发送的是本模拟的技术输入。
6. 定向静态检索和格式验证即可，本票不运行全仓聚合。Root 最后统一运行 tools/checks.py。结束前合入最新 integration 并核查必要受影响内容。

## AC 与观察点

| AC | 验证证据 |
| --- | --- |
| 1 | 每轮过程记录真实保存来源、新条件、部分/漏答、事实、依赖；安装参考零修改 |
| 2 | 汇总前回读 input 和永久问答，frontier 空但事实/依赖未完时保留恢复位置 |
| 3 | 当前范围覆盖复核、具体评审、准确 MD 更新、永久记录回读、清理的真实先后文件证据 |
| 4 | 部分评审及暂停时未决仍在；清理后完整产品问题、影响、决定及历史可恢复 |
| 5 | 实际继续范围、后续新条件、限定重开、仍有效决定、B/Q 最大编号与新编号 |
| 6 | 同一交付版本的两模块逐轮模拟及真实文件写/读/清理，失败或限定结果原样保留 |

## 当前结论

准备完成并正式接续。没有执行 #87 RED/GREEN，没有产品修改，没有本票验收通过声明。

## #86 集成后核对

- Root 实际通知正式集成 head 为 `3cae1a783ddf43a0106d7ba6dc5e1072651693be`。worker87 通过受控 runner 执行绝对路径 `git merge --ff-only`，退出0，从 `0fbe08e` fast-forward 至该 head，准备材料保留。
- 已重新读取 `reviews/86.md`、`merges/86.md` 和 `merges/86-materialization.json` 的身份/差异记录，重新核对六个产品 MD 的完整变更。#86 统一聚焦展示与同一路径按规则合入，实际依赖仍完整核查，省略未改内容保留。#87 复用该契约。
- #86 十轮模拟的限定接受、合成 reader 和真实客户端未验证边界保留。59路径物化账中的39项 LF/CRLF 差异保持原证据与 origin 身份，不改原记录。
- 当前正式 RED 源基线固定为 `3cae1a783ddf43a0106d7ba6dc5e1072651693be`。实际 RED 前不改产品。正式预期写集仍为本计划所列四个产品 MD，以及本票活跃请求、fixture、rubric和证据；若 RED/检索显示必要关联项，先记录本轮理由。
- Root 可以使用本目录 request.md/input.md 派发 fresh actor，输出到本目录新建 red/。rubric 不交 actor。等待实际 RED 冻结消息。

## 五轮实际 RED 后的修复选择

已完整回读 red/ 下14份实际文件，包括 session.md、accurate.md v2、三个具体稿及其修订、问题和四份真实模拟答复，源码仍为 `3cae1a7`。前文“等待 RED”保留其当时阶段，本节记录新的实际进展。

RED 正确保留了 R2 同类已答/跨类未答、Q2/Q3 漏答、R3 局部批准及继续 M2、R4 真实暂留和快照事实等待、R5 只合入 M1 的 v2。准确文件仍有完整 Q2 产品影响，M2 未批准/缺快照也未被当作完成。没有观察到误删，不把这些已有正确行为标为 RED。

实际缺口是 R5 的 M1 当前范围已具体评审、准确 v2 已回读，但过程始终是逐轮追加叙述，没有逐轮可恢复的本轮覆盖去向与临时/永久分界，没有执行保存永久依据→回读→限定清理。历史可阅读不等于安全收尾机制已存在。清理后新条件/稳定重开尚未执行，不能声称 RED 已证明它失败。

本轮固定写集为四个产品 MD，即入口、module-clarification、writing-review、review-and-progress，另加三个活跃测试材料 optimization-87-request.md、fixtures/optimization-87-labels.md、optimization-87-rubric.md 及本票证据。澄清参考集中定义过程 MD、覆盖、永久字段和恢复；评审推进集中定义清理顺序；编写及入口接通同一契约。直接使用 Markdown 与 Agent 已有文件操作，无脚本/JSON状态或新框架。#82—86规则保留。

GREEN 由 Root fresh actor 逐轮发送真实模拟答复，必须实际暂停/恢复、部分评审时未处置项保留、M1收尾时实际清理并回读、M2事实缺口保留、实际补交快照、清理后新增关联变化只重开影响部分。Actor接收普通请求和资料，不接收本计划/rubric。定向检查只验证格式/差异保真，语义结论等待实际 GREEN。
