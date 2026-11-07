# #81 实施与验证计划

准备基线为 `475b924a753a27437ea22664126b8a00edfe9543`，分支 `codex/tpd-opt-81`。产品源码尚未修改。#80 集成后先合并当前 integration，回读受影响源与实际 HEAD，再记录 RED 与实现版本。

## 依据与根因

已核对任务根 CONTEXT.md、inputs/issue-79.md、inputs/issue-81.md、exploration.md #81 条目，现行入口、module-clarification、writing-review、dashboard-intake、planning-confirmation 及 clarification 请求/rubric。

当前 module-clarification 将场景已纳入但预期未知直接列为产品事项，将业务规则、矛盾与未答归入产品区，保留两个未决类别。writing-review、规划图注与活跃 rubric 重复了相反要求。每题已有选项、推荐、理由和例子，但缺少代价。部分答复的对象/行为核对可复用，需要补实际追问与仅不知道的处置询问。

只读适配已安装 grill-with-docs 的提问段、interview-record，以及 coverage extension 的逐轮真实答复、部分答复与依赖核对。保留 TPD 自己的过程记录和具体点评审边界，不复制工程路由或需求长文批准门。

## 写集与边界

- `skills/test-point-discovery/SKILL.md` 和受相反问答/双标签要求影响的 `references/*.md`。
- `tests/test-point-discovery/` 下活跃请求与 rubric 中相关相反要求。
- 本目录新增计划、普通请求、模拟输入、独立语义 rubric、逐轮实际证据与验收记录。

不修改历史 run/session/demo/red 证据、helper、全局 Skill、grill 原 Skill/extension、下游、远程或 UIT/TCA 资产。共用表达、粒度、操作终点、局部展示、模块清理等后续票行为仅消除本票问题去向冲突，保留其独立范围。

## 预先确认的测试边界

复用 #79 已确认的真实自然语言 Skill 入口，以实际逐轮回复与文件观察。Root 派隔离 actor，只接收 request 与 fixture。Root 实际逐轮发送 SIMULATION 回答，执行者不编用户答复。rubric 和主持方情景不给 actor。

RED 先跑第一片问答，观察旧版双标签/自动产品化/每题代价，明确静态定位与实际入口结果的区别。GREEN 再用新 actor 从普通请求开始，按实际提问发送回答，覆盖未问依赖、漏答、部分回答、仅不知道、明确暂留及明确解答。若发现后续片缺陷，先留该片失败再做最小修复。

## 验收与验证

每题含选项与自定义、假设例子、推荐及理由和代价。独立同轮，依赖等真实前提。未问/漏答保持未答，部分回答只绑定实际对象、条件、行为并追剩余。仅不知道先问处置，真实明确暂留才入唯一产品区。明确规则仅形成候选，具体点评审仍等待。逐轮保留实际问答、范围、来源和当前状态。

每片核对实际对话/文件，最终做针对性格式、链接、diff 与来源保真检查。Root 已说明统一 tools/checks.py 在 #80 基线及最后集成执行，本票不重复触发相同沙箱故障。语义由独立 reviewer 核对。本票不触及工程检查实现，不新增框架、语义关键词验证或依赖。

最终提交并合并最新 integration tip，返回每项 AC 证据与限制。模拟验证不构成真实业务或 XMind 客户端验收。

## #80 集成后本轮核对

已用 ff-only 将 `82c3ae0bba575a15340e0d1f914d89b9a404fea4` 合并进 worker81，准备文件完整保留，HEAD 即此版本。已回读 #80 产品 diff、module-clarification 及 verification。#80 已建立可查事实、明确规则候选、冲突/过时实际提问、额外风险选择和项目排除沿用，并在多个方案中消除自动转产品句。本票保留这些能力，改动按最新源重新收窄。

最新根因仍为 module-clarification 独立【待确认】类别、两类顶部模板、仅不知道未规定处置、部分答复尚缺持续必要追问，以及每题代价未覆盖全部问题类型。writing-review、planning-confirmation、information-maintenance、workflow-lifecycle、roles-entitlements、single-file-handoff 与活跃 rubric 仍有相反双区要求。已由 #80 修复的 async/feedback/decision-table 条款不重复改写。Root 将运行当前源 RED 首轮，冻结实际失败后才开始产品修改。

物化工作树文件 hash 与 Git 原始 blob 身份分开记录。core.autocrlf 造成的 CRLF/LF 差异不当作同一字节身份，也不修改全局 Git 配置。
