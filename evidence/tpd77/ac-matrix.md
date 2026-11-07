# TPD-AC-001—024 同版本判定

产品源提交2f2eea538dc096a2e1dbcc4ada44af5a58f4fa54，Skill tree d062c25c3db45175a71654945724f425074ef7f0。所有“通过”只指下列限定模拟开发行为，非真实业务确认/执行，不承诺任意输入、全部XMind版本或下游程序接入。当前287份不可变raw身份见source-bindings-r2.json，原source-bindings.json保留R1时点288份捕获（含一份行政状态，R2仅保留旧捕获元数据、不验证现日志）；语义适用性见reuse-analysis.md。旧证据不是本票重跑，跨票片段不伪称单次连续执行。

## 可回读证据索引

路径前缀repo表示本仓库；DEV表示开发根C:/Users/lenovo/Documents/ChatGPT/ui-test/.scratch/tpd-development-20261107。历史receipt原worktree路径保持不动，当前repo位置与raw hash另绑定。

|ID|当前证据位置与范围|
|---|---|
|E01|DEV/context/holdout-dashboard-{prd,user}.md；DEV/evidence/tpd65-holdout/{actual-output,boundary-output,execution}.md：看板原始输入及入口理解|
|E02|repo/tests/test-point-discovery/planning-demo.md第一轮；repo/.archify/architecture-planning-20261107-020000/；DEV/evidence/tpd66-confirmed-output.md；DEV/context/acceptance-adjustment-20261107.md：真实表图与原版选择，调整版未采用|
|E03|DEV/evidence/tpd67-fresh/及tpd67-r2/{actual-output,execution}.md；tpd67-review.md：独立/依赖/冲突/部分回答、R1失败与R2关闭|
|E04|repo/tests/test-point-discovery/{writing-demo,two-chart-writing-demo}.md及fixtures；DEV/evidence/tpd68-client/{observations.md,import-source.md,imported-review.xmind,format-receipt.json}：具体检查及真实中文层级导入|
|E05|repo/tests/test-point-discovery/progress-run/{session,accurate,m1-d2,m2-d1}.md：拒绝、通过后建v1、下一模块答疑不升级、具体评审后v2|
|E06|repo/tests/test-point-discovery/feedback-run/{session,accurate,chat-d1,md-returned,md-d2}.md：聊天/MD、删除歧义、两端影响与无关保留|
|E07|repo/tests/test-point-discovery/maintenance-calculation-run/{session,department-d1,calculation-d1,calculation-d2,accurate}.md及fixtures/maintenance-calculation-prd.md：操作/单位精度阈值/叠加舍入/拒绝后更新|
|E08|repo/tests/test-point-discovery/workflow-lifecycle/全部实际round/answer/current/impact/lifecycle材料；repo/.archify/architecture-procurement-20261107/；fixtures/procurement-{prd,notes}.md与lifecycle-prd.md：流程先行、反向影响、单对象状态|
|E09|repo/tests/test-point-discovery/roles-run/及roles-demo.md、fixtures/roles-{prd,notes}.md：四类条件、完整分支、80/90变化、替代目录建议/拒绝/采用；DEV/evidence/tpd73-eol-review.md保留字节修复|
|E10|repo/tests/test-point-discovery/{async-session,async-review-v1,async-current}.md与fixtures/async-{prd,notes}.md：受理/过程/终局、对象对应、未知能力|
|E11|repo/tests/test-point-discovery/xmind-run/{conversation,accurate,historical-v1,historical-v2,historical-v3,chat-candidate,md-candidate,xmind-candidate}.md及两native-read.json/candidate-receipt.json；DEV/evidence/tpd75-client/{observations.md,returned-review.xmind,return-receipt.json}：同一准确路径v1—v4三入口完整链，真实客户端另存/文字/层级回传|
|E12|repo/evidence/tpd76/current.md v4及其两引用；DEV/evidence/tpd76-receiver-v4.md：只MD恢复交接；v3歧义与v4修正保留|
|E13|repo/evidence/tpd77/serial-run/{planning,questions,review-d1,review-d2,session,current,handoff-offer}.md；repo/.archify/architecture-roles-20261107/：最终入口从原始角色资料到实际图、Root逐轮模拟表图确认/部分回答/拒绝修订/具体通过/同MD及交接决定|
|E14|repo/skills/test-point-discovery/references/全部方法与方案参考：实际逐份读源，官方与产品实例/项目适配区分；应用由E03/E07/E08/E09/E10证明，非仅文件存在|
|E15|DEV/evidence/tpd77-receiver.md：全新接收者仅新角色current.md v2及两引用独立恢复；Root实际阅读后判接收行为通过，#77已回读原报告，不借E12冒称此文已接收|

## 逐条语义结论

|AC|结论|对应实际行为与完整性边界|
|---|---|---|
|TPD-AC-001|通过|E01/E03/E04/E13：原PRD+说明+实际回答形成检查与独立未答，不只复述；R-A1确认事件而保留时区/状态更新|
|TPD-AC-002|通过|E02/E08/E13：三主例各有实际表图/PNG，#77重读旧图、实际新图并Root一起确认；原看板顺序选原版，未选调整不冒批准|
|TPD-AC-003|通过|E05/E08/E13：M1通过后才M2、流程通过才模块；未决继续依据实际模拟决定，答疑/拒绝不升级|
|TPD-AC-004|通过|E01/E07/E08/E09/E10/E13：三主例+四小例七类均实际选择；维护仅现有操作、状态局部辅助、费用规则主线、采购多角色仍流程优先、角色广泛差异主线、异步非单对象模板；小例采用已标模拟接续规划，不冒新图|
|TPD-AC-005|通过|E08：从同一申请与金额接力主动提F及付款关联，预算仅建议背景；纳入由模拟用户决定，不等用户逐项提醒|
|TPD-AC-006|通过|E14各方法有来源/版本章节或无编号在线、适用及不适用、缺失信息、应用、假设、误用；E07分类/实际邻值/四规则及舍入，E08状态，E10错误推测/检查表，E03协作澄清实际使用；外部产品规则不移植|
|TPD-AC-007|通过|E01/E03/E10：权限性能风险仅建议或排除，导出未决定不入基线；编号错配与批次行关联建议经模拟纳入，非缺陷事实|
|TPD-AC-008|通过|E03/E07/E10/E13：先读资料、独立同轮、叠加/重试前提回答后追问，实际回答可回读，推荐/未答分离；保留#67R1而非回写通过|
|TPD-AC-009|通过|E03/E05/E13：问题和具体检查评审，无额外长篇需求批准；R-P1表图一次确认，R-D1具体拒绝再R-D2评审|
|TPD-AC-010|通过|E03/E07/E10/E13：访问次数/人数冲突、阈值精度、目标重复/幂等、权益生效到期均提问，不从页面/PRD推测裁决|
|TPD-AC-011|通过|E04/E07/E11：必要条件/边界/已知结果有依据，真实XMind26.4.1327导入中文层级及回传；仅限定双图稿，角色新稿未导入，不扩大兼容结论|
|TPD-AC-012|通过|E04/E10/E13：顶部人工/产品问题分开，R-A1部分回答只更新确认事件；纳入不清除U1/U2/U3；交接人工已决同步关闭|
|TPD-AC-013|通过|E04/E11/E12/E13同文来源到分支、实际决定/未知映射集中；E15全新接收者仅新角色v2与两引用独立恢复来源、部分答复/评审/范围及身份，未读旧聊天不影响所需信息恢复；不能独立审计旧hash/图原件的限制保留|
|TPD-AC-014|通过|E11独立同链：tests/test-point-discovery/xmind-run/accurate.md由v1→聊天v2→局部MD v3→真实XMind v4，候选未提前改、具体评审后同路径更新；不是E06案例A与E11案例B拼接|
|TPD-AC-015|通过|E04/E05/E11/E13：局部副本有待评审范围、真实导入、未展示模块保留，只有具体点通过后建/改准确MD；R-D1拒绝无基线，R-D2批准后v1|
|TPD-AC-016|通过|E06/E08/E09/E11/E13：明确反馈候选、歧义删除问后恢复、受影响完整分支重审、普通/其他模块不机械改；R-D2只移范围叙述到说明区，无源码修改/下游更新|
|TPD-AC-017|通过|E10/E12/E13：纳入必需检查与未知规则分开；资格Q1/昨日Q2及U1/U2/U3保留，不填旧单价或时区|
|TPD-AC-018|通过|E12原v4跨依赖恢复、E13实际依赖分析后R5选A、其余保留；E15新角色MD仅两完整订单分支交接/其他保留、U1-U3依赖及理由均正确恢复，不默认整模块阻塞，不追加用户清单或借旧文档接收证据|
|TPD-AC-019|通过|E04/E07/E09/E10/E13：按来源/维度/关联逐项有检查或未知/排除，角色旧d1遗漏先自检补，最终R-D1范围叙述经拒绝修正；不以数量代覆盖|
|TPD-AC-020|通过|E05/E10/E11/E12/E13：全部限定文档与模拟，不执行下游业务导入或业务测试、不宣称P0通过、保留整轮P0实际报告证据与人工启动；真实XMind导入另按客户端证据核对，不冒程序直导|
|TPD-AC-021|通过|E09/E13：两用户完整商品/结算/本人他人/预约及变化，默认模块优先；替代目录经拒绝/明确采用，仅组织小例，非角色端完整业务|
|TPD-AC-022|通过|E09/E13：客户角色/权益/有效状态/归属分离；VIP改价影响本分支、不机械改普通或旧单；隐藏不证明拒绝操作已测试|
|TPD-AC-023|通过|E04/E07：双图各有筛选/日期/图例及各自去重/按记录差异，功能分支独立重复适用检查，不用公共引用|
|TPD-AC-024|通过|E08：先流程澄清/具体评审，等待时不进入模块；通过后M1/M2；财务复核新事实先候选完整资格分支重审再更新，不补未定重提/复核重试|

24AC在上述限定模拟开发范围内均通过；E15接收行为已由Root实际读报告判断通过，#77已回读核对。整批仍须Root安排本票及全分支最终全新上下文双轴审查，不能把执行者矩阵代替独立审查。角色新稿XMind兼容、下游程序接入与真实业务仍未验证，均单列边界。
