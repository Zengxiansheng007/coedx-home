# CR-20261117-115 - 准确控制字段、字面业务反馈与来源漂移

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | scripts-and-validation / references-and-assets / safety-and-governance / downstream-and-handoff |
| Source | 独立 SPEC-RTA01-001、Standards RTA02 typed inputs、Spec RTA02 source binding 与 literal step_reference 四项 P2 |
| Baseline | ed7672f16a26e90b7744fd2769058a85334c0296；tree 3fc7606dc5a203c1af69e4315e1b7978aab1fbb4（git rev-parse已核） |
| Author | Codex |
| Related Records | CR-20261117-112, CR-20261117-113, CR-20261117-114 |

## Summary

通过原公开反馈入口保留合法业务叶；只按准确控制 owner/源字段兼容旧评审显示。
每个实际 typed 来源都纳入漂移核验，无法分辨的引用保守绑定全部注册；不扩大明确未用来源影响。

## Context And Problem

先读本轮 CONTEXT、plan、REQ/AC矩阵、既有feedback/review_expression显示来源和独立评审探针后实施。
case.text“最终评审：pending”被按文字归一化，业务编辑吞成零变化；inputs.source可见却不可编辑，
只改同胞label还会把真实source篡成user_decision；data.value.step_reference被不分职责跳过。
source_binding在另一个recording已匹配时漏掉带片段、结构体或其他未分辨typed引用。
这四项均是既有框架对象与实际业务字面子树的职责边界遗漏，属于本次必要关联修复。

复用标准库与既有渲染源偏移、唯一候选/QA、来源注册、公开prepare/apply和preparation scope接口；
不新增schema、持久索引、依赖或平台调用，无需外部事实查询。Python311 -X utf8 -B复用现有运行时。

## Sections Changed

| File | Section | Change Summary |
|---|---|---|
| scripts/scoped_review.py、aggregation.py、feedback.py | 评审控制行与反馈 | 渲染派生准确owner/根字段flat偏移；树匹配后只去掉该字段可信行；flat探针沿同一源偏移 |
| scripts/review_expression.py、scoped_review.py、feedback.py | 共享typed角色 | 声明actual value/input/output贯穿全部后代；枚举、chat/MD回映、source更新用同一职责 |
| scripts/review_expression.py | 来源绑定 | 每个typed来源独立匹配，明确片段绑定注册材料；结构体/其他未解析保守全部注册；未用来源不重开 |
| scripts/test_feedback_control_owner.py、test_feedback_literal_roles.py、test_source_binding_roles.py | 公开回归 | 原始/旧格式同文编辑、noedit、literal保留、框架拒绝/claim来源刷新、mixed来源与公共项局部失效 |
| references/feedback-contract.md、source-assessed-display.md | 既有调用契约 | 准确控制字段与字面键贯穿入口；来源保守绑定与局部复用边界 |
| change-records/index.md与四分类、本文 | 可追溯记录 | 原失败和验证口径保留；不自授业务或宿主验收 |
| .agents/skills/test-case-authoring | 同源分发镜像 | 仅本次准确写集同字节同步 |

## Decision And Alternatives

不按显示文本Counter消费业务行，也不新增全树字段黑名单。控制行来源为准确渲染器瞬时偏移，不写入候选，
实际raw摘要在任何归一化前仍必须唯一、同版、有实际答复。无法唯一对齐控制与业务内容时拒绝并澄清。
actual字面子树不再继承框架的source/id/reference职责；边界外真实来源、身份、关联、控制字段仍不可直接编辑。
仅真实框架step/claim的来源改为user_decision；data仅更新根溯源，实际value.source完整保持。
对片段仅支持准确注册ref/path/source_ref的明确定位；结构体不猜字段含义，按既有契约保守绑定全部注册。

## Detailed Change

当前新布局已外置控制元数据，业务同文不获得豁免。历史布局仍接受可信同版评审前/后稿，准确case根字段
review_status、final_review、review_history具有源行身份；optional历史行的对齐如产生不同业务形状即fail-closed。
标量探针沿原业务节点offset定位；完整case缺省不移动其他owner的相对绑定。
共享field_role/path_role只表达现有case/context/step/claim/literal职责，不成为第二权威或新schema。
来源绑定逐引用要求映射，matched A不能掩盖unresolved B；literal输入内同名source_ref不扩大框架来源范围。

## Impact Analysis

影响当前候选的Markdown/chat反馈、支持native适配的共用映射、显示评估与公共适用性消费者。
保留实际source_catalog digest/version、raw返回唯一性、凭据全树保护、未展示消费者、实际claim来源更新。
原试用、全局Skill、原P0、实际UI与外部发布均未写。共享入口变更需Root最终固定树全仓回归及独立复核。

## Validation Evidence

| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| 原始碰撞RED | unittest test_feedback_control_owner | 真实raw binding仍changes=[]，失败保留 | run/evidence/rta05-review-fix/red-01.txt |
| 旧metadata碰撞RED | 同一公开入口旧布局 | 现代稿先绿，旧稿仍吞改；失败保留 | red-02.txt |
| literal丢失/篡改RED | test_feedback_literal_roles | source不可定位、label改写source、step_reference不可定位；失败保留 | red-03.txt |
| mixed来源RED | test_source_binding_roles | 片段、结构体、未注册三反例旧readable继续生效；失败保留 | red-04.txt |
| 初次扩大针对性 | 六模块unittest | 25项，旧pending noedit错误2项及1个不符既有claim来源契约的测试输入；原证据保留 | targeted-01.txt |
| 当前针对性 | 同一六模块 | 25项全部通过，实际claim校验门未放宽 | targeted-02.txt |
| 直接关联/公开文件实证 | 20模块unittest及实际MD保存读回→prepare/confirm | 93项全部通过，92.584s；此后只补整例省略偏移修复；实际文件精确改cases/EDIT/text，其他LINK不变 | final-targeted.txt、public-probe.json |
| 最终偏移影响回归 | control-owner、legacy-feedback、feedback、feedback-loop | 25项全部通过，32.284s，包含新增整例省略反例；不把此前93项冒称最终树全量 | final-offset-targeted.txt |
| 结构/记录/敏感扫描 | create-skill --require-change-records | exit1，P0=3/P1=0/P2=0，与baseline三项rule/file完全一致，无新增；原负例字节不变 | create-skill-final.json、validator-comparison.json |
| 镜像/语法/写集 | 同字节、AST、git diff --check | canonical/mirror各175文件同字节、87 Python语法通过、diff --check通过；15路径双份，本轮一次提交冻结 | package-checks.json、freeze.json |

red-01后首次green-01测试期望未包含公开changes的before/accepted字段，实际已能定位；纠正为逐项业务字段断言，
原失败日志未覆盖。PowerShell原生rg未展开通配符路径的一次只读诊断失败保留，后改用rg -g。
93项之后只读自检发现控制flat偏移须固定原owner块起点，新增整例省略测试先红（red-05.txt）后修正，
最终受影响25项通过。源码此后冻结；14项新增公开测试覆盖三类根因，不冒称当前整仓328项已执行。
实际次数按这些外部日志交Root统一累计，不维护第二执行/额度账本。

## Safety And Privacy

全部材料与回复均为明确合成；无真实凭据、网络、模型或UI调用，无安装依赖/环境、全局目录或旧trial写入。
三个继承扫描负例保持原字节；不改扫描器以制造通过。新代码中文说明，稳定机器身份不翻译。

## Risks And Follow-up

applied candidate，未声明宿主accepted或用户业务通过。最终完整整仓检查由Root在CR115合入后运行；
实际完整重新生成与独立专业语义审查属于后续阶段。XMind客户端仍由用户导入验证，本票未自动操作。
结构体typed来源暂保守全注册绑定，可能扩大重新评估范围；这是已声明保守边界，不冒称精确解析。

Refs: 本轮plan/CONTEXT/req-ac-matrix；已确认REQ-008/017、AC-034；run/evidence/review四项独立finding与探针。
