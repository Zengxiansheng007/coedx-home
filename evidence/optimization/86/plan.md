# #86 实施计划

SIMULATION 开发验证。2026-11-07，尚未运行 RED，尚未开始产品修改。

## 固定基线与资料

- 工作区为 taskroot/workers/86，分支 codex/tpd-opt-86，HEAD 0fbe08efcb34f42c5b6a72c4c9129018620d95c6。读取时工作区干净。
- 需求来自 taskroot/inputs/issue-79.md 与 issue-86.md，局部验收为 TPD-OPT-AC-010。已核对 CONTEXT.md、exploration.md、仓库 docs/development/verification.md、tdd 及 tests/mocking 参考、writing-for-agents 与 create-agent-skill。
- #82 共用规则与 #85 局部澄清已合入基线。其原证据保持原身份。本票新基线从真实入口生成候选，由 Root 实际发送具体评审答复后创建，不预填通过状态。
- 已读反馈入口、feedback-review、review-and-progress、xmind-feedback。现有“展示保留后的完整分支”“未改检查也保留，不能只贴差异”“完整受影响分支”构成静态根因证据，实际 RED 须另由隔离使用者运行。

## 写集与复用

产品限定 skills/test-point-discovery/SKILL.md 及直接相关 feedback-review、review-and-progress、xmind-feedback、roles-entitlements、workflow-lifecycle 等参考，按实际扫描处理同根因实例。同步相关活跃 request/rubric，新增本票请求、fixture、独立 rubric 与证据。历史 *-run、history、demo、固定旧产物及其保真脚本不改。

沿用 Agent 自然语言语义核对、同一路径 Markdown 直接更新、现有 read_xmind.py。无新运行时、框架、泛化 MD 导入器或语义关键词判分器。合成单 sheet XMind 明标 SIMULATION，只证明受支持格式的输入解析与反馈行为。真实 XMind 26.4 客户端往返由 #88 同版闭环另证，本票未跑时报告未验证。

## 实际入口与步骤

1. Root 派不接收本计划及 rubric 的独立 actor，只给普通 request、fixture、目标 Skill 路径和输出目录。actor 等 Root 逐轮发送答复，不得自编整场决定。
2. 初次候选来自新小型表单及不受影响列表，模拟已确认规划只作接续前提。每次实际展示保存独立版本。Root 对具体候选实际批准后形成 current.md v1。
3. Root 逐轮给聊天、局部 MD、合成 native XMind 反馈，实际候选、歧义提问、答复、具体评审与读回独立保存。RED 冻结后才改源码。
4. GREEN 复用同类输入，Root 主持同样分轮交互。对共用规则完整核查适用对象、真实差异和业务依赖，评审只展示变化及必要上下文。未展示内容保留，未知规则局部回问，具体评审后更新同一 current.md。
5. 定向静态一致性、reader 既有单元测试与文件保真检查分列。最终聚合 checks.py 由 Root 统一运行。

## 六项验收与证据

独立 rubric 覆盖版本/范围/含义、聚焦展示与完整影响、省略/歧义删除、未知局部澄清、同MD评审后更新读回、三入口实走及解析/客户端分证。语义验收依据真实对话与文件，不以字串、节点数、文件存在代替。

## 本轮状态

Root 已实际主持并冻结 red/ 四轮。已回读全部输入、候选、回复、sources.md及current.md。表单和列表分别具体通过后形成current.md v2，聊天改两个渠道上限后仍保持v2，时点行为有效；round-04-form-candidate-v2.md 和回复同时全文重印无关正文及取消检查，构成聚焦展示 AC2 的实际 RED。

实现收敛共同反馈契约并同步入口、具体评审、XMind、角色、流程及活跃反馈/流程rubric、可读性/XMind请求。重点是完整影响核查和聚焦展示分别约束，具体修改按路径合入，省略的同分支检查继续保留。未增加helper或改变旧保真脚本。

定向验证见 verification.md。源码准备冻结，等 Root 另派 fresh GREEN 三入口交互。未运行真实业务、下游或全局安装。
