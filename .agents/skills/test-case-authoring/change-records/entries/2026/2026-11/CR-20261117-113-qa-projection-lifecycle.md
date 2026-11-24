# CR-20261117-113 - 同一 QA 的显示评估、准备归属与业务投影

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | scripts-and-validation / references-and-assets / downstream-and-handoff / safety-and-governance |
| Source | RTA-02；旧 TodoMVC 显示评估 checkpoint 拒绝、公共适用已答仍 pending、来源与长审计进入业务树、空格不可辨 |
| Baseline | worktree 起点 07a9b8556be268940fba3b32acee9e472af102b9；修改期间已 fast-forward 776c82156674ac7344c4f079da75926d90b299d6（RTA-01+RTA-03） |
| Author | Codex |
| Related Records | CR-20261117-112, CR-20261117-114, CR-20261117-101 |

## Summary

显示与准备归属评估通过原 advance_record 写入唯一 QA 并回放；候选仍须与该投影完整一致才能 checkpoint。
已声明来源与审计职责进入现有 Agent 说明，真实复杂业务值保留。公共打开和本例准备分别显式评估，
原 common 步骤不搬不改，展示为特殊时仍可准确反馈回原路径。对象值合行保留生命周期，首尾空格在
闭合引号内保留并标中文计数，真实值和身份不变。

## Context And Problem

只读证据为 本地验收证据 与旧试用 display-api-probe/result.json。
纯 assess_review_projection 可 render/write，而 QA 动作白名单无该评估，checkpoint 因不一致拒绝；
这不是应绕过的检查。旧源还暴露列表叶路径不可评估、typed 来源与任意字典混淆、完整新作者范围被
误作父 P0 的 partial、已知长审计通用展平、含生命周期的单值对象机械拆开等关联原因。

每轮已核已确认 REQ-008/009/010/011/014/015/017/021、AC-009/010/011/013/017/018/021/029/030/031/032/034，
当前实现及实际失败后才修改。复用现有标准库、来源登记、scope、恢复与反馈 seam，不新增 SDK、依赖或
mandatory JSON 包，无需外部 API/平台事实检索。

## Sections Changed

| File | Section | Change Summary |
|---|---|---|
| scripts/qa_record.py, clarification.py, feedback_record.py | 持久化与当前父源评审 | 两个同名评估动作、同记录回放、控制状态保留、真实评审原话 QA 锚点、准确 source_catalog 贯穿 |
| scripts/review_projection.py, review_expression.py | 类型与绑定 | 合法 dict/list 标量路径、原索引投影、业务 owner/实际使用来源绑定、已知控制变更不误开业务、真实漂移局部失效 |
| scripts/preparation_scope.py | 公共和本例归属 | 严格完整新作者范围及准确父源；case_specific 的显式 pre/post 归属保留原源；冲突/未评估保持拒绝或 pending |
| scripts/scoped_review.py, aggregation.py | 同投影正文/对话 | 已知技术/审计外置；公共直属模块、特殊节点保留 source origins；数据字面子树不变关系类型 |
| scripts/authoring.py | 来源校验 | 只解释声明来源类型，真实 data.value 同名键不注入 basis；凭据 guard 仍全树 |
| scripts/data_projection.py, feedback.py | 数据与准确回流 | 单对象值合行、生命周期保留、引号内原空格+计数双向编码；真实 value 的框架同名键可准确回映；已发布旧 metadata 布局精确兼容 |
| scripts/module_handoff.py | 原说明职责 | typed 来源定位、QA/候选精确审计链接、控制说明和同版状态可追溯，不复制长 QA 为第二权威 |
| scripts/test_projection_qa_lifecycle.py, test_projection_full_lifecycle.py | 单份记录及串联 | 生成、评估、评审、物化、真实 MD 反馈、复评、checkpoint 和新进程恢复 |
| scripts/test_authoring_preparation_scope.py, test_typed_projection.py, test_whitespace_projection.py | 直接关联边界 | 新作者/父源界限、special pre/post、复杂业务键、凭据/坏范围拒绝、空格及保留格式碰撞 |
| 现有 authoring/clarification/feedback/scoped/final_repairs tests | 旧断言适配 | 显示位置按新契约；非法反馈实际插非法叶，视觉相同夹具不冒用 digest 多身份；真实守卫不放宽 |
| references/qa-record-contract.md, source-assessed-display.md, aggregation-contract.md, review-expression.md, module-handoff-contract.md, clarification-contract.md | 公开调用与条件 | 明确真实任务方法、父源、特殊归属、恢复、值边界及中文空格说明 |
| .agents/skills/test-case-authoring | 分发镜像 | 与 canonical 同字节同步本次准确写集 |

## Decision And Alternatives

保留唯一 QA、原候选、真实来源和既有审批边界，未把纯评估函数返回物提升为第二答案源。
不放宽 checkpoint 完整相等、source_catalog digest/version、原始回传 digest 唯一性或隐藏消费者保护。
新作者范围须全 add、与父源身份不重叠、原初次基线 hash 正确、当前/初次作者集合完整相等、遗漏集合
恰为完整匹配父源；仅 extension_entry 的自声明布尔不能放行。原 P0 不伪装为新 12 条的例外。

本例特殊归属沿原 preparation_scopes 和同一 QA 事件保存，不另建注册表、不搬源步、不从公共排除自动推断。
新增 aggregation/feedback/authoring/feedback_record 薄适配均为真实消费者根因关联；Root 已核共享 seam，
RTA-01 合入后没有并发源码写冲突。normalize_case/normalize_review_metadata 的控制文字碰撞定位逻辑未改。

## Detailed Change

显示评估记录合法列表叶并按原路径递归投影，删除叶不移动后续绑定。新记录按实际 owner 使用的来源注册核对；
无法分辨映射时保守。已知 case 评审控制字段不使未变业务显示失效，语义/数据版本和真实内容仍参与摘要。
业务实质变化后重新评估受影响部分。partial 的准确父源仍由调用方提供并在评审/物化/恢复重核。

typed 来源只用于 context claim、step/expected/verification、data 根等声明位置。data.value 的
source/source_ref/id/text/lines/case_ids/final_review/user_rule 等实际键和值显示及反馈保持字面语义，
不转用例名称，不外置为审计；用户实际业务规则同样保留。源校验与全树凭据保护独立。

## Impact Analysis

本票影响候选生成、显示元数据持久化、公共/特殊归属、Markdown/受支持原生共用映射、模块说明与新进程恢复。
无业务执行、原 P0 更新、全局安装、发布或远端变更。默认反馈仅影响当前明确业务集合；隐藏消费者仍待扩大评审。
定义只显示一次不减实际执行频次；缺来源、未评估、冲突或漂移保留 pending，并保留未受影响有效记录。

## Validation Evidence

| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| 原持久化缺口 | 单一公开动作测试先红后绿 | Unknown Q&A action 被复现；相等门不变后 checkpoint/resume 成功 | run/rta02/red01.txt、green01.txt |
| scope 与来源/列表 | 公开 QA/纯评估切片 | 两动作回放、局部 source/owner 漂移与非法索引拒绝 | source-and-lifecycle.txt、green04.txt |
| 新作者/本例准备 | 实际 build_extension + review_preparation_scope + MD 回流 | 原 P0 仅源核验；common/special 原路径回映；未评估/冲突/漂移仍待核 | green08b.txt、combination-final.txt |
| typed 业务值 | 实际转换、展示、反馈、应用 | 同名键和值保持，声明坏范围仍拒，嵌套凭据在现有 authoring 安全用例中拒绝 | green09.txt、full01-affected.txt |
| 空格双向及历史稿 | 实际 Markdown 物化、no-edit/edit、引号/控制/碰撞反例 | 精确原值，旧 metadata 布局及 RTA-01 反馈守卫保持 | green07.txt、combination-final.txt |
| 完整串联 | QA 评估→具体稿评审→物化→实际 MD 反馈→复评→checkpoint→新 Python 进程 resume | 已通过，无第二答案文件，原数据与无关评审不变 | full-lifecycle-first.txt、source-and-lifecycle.txt |
| 首次完整回归 | unittest discover | 314项，4失败+1错误；已保留并分类为旧断言/视觉完全相同夹具，未改严格守卫 | full01.txt；36项 affected 已通过 |
| 当前完整回归 | 同一入口、票内 TEMP/TMP | 314项，313通过+1个旧 Agent 状态断言失败；之后生产源码未变，只补强该断言验证只读状态、跨批次更新、准确候选版本和旧字节保留 | 本地验收证据 |
| 最终定向回归 | external_handoff、notes_lifecycle、technical_notes、完整串联、RTA-01 grouped | 24项全部通过；依 Root 指示不为单一旧断言重复314套件，最终整仓回归由 Root 后续固定树覆盖 | 本地验收证据 |
| 包/语法/镜像 | 本轮 package_checks.py + 原 create-skill --require-change-records | 171文件 canonical/mirror 同字节；84 Python 语法通过；原扫描 exit1、P0=3/P1=0/P2=0，无新增/移除发现 | 本地验收证据、create-skill.json |
| 结构/记录/敏感扫描 | create-skill --require-change-records | 与 Root 三个继承合成凭据负例对照；最终结果见扫描证据 | run/rta02/create-skill-final.json |
| 镜像及写集 | 字节比较、git diff --check、当前树清单 | 最终检查结果随冻结回执保存 | run/rta02/freeze.json |

首次模块启动被 runner 工作目录重置影响，之后 payload 显式 Set-Location；该初次准备失败留在工具记录与自动 incident。
首个 red01 日志路径被随后真实 red 复用，未伪称该文件保存最初 ModuleNotFoundError。系统 sandbox TEMP 的
WinError5 保留在 green03.txt，改为票内 run/rta02/tmp 后通过；生产原子写不为测试放宽。所有 expected red、
fixture 准备失败及 full01 结果按实际保留，数值由 Root 合并现有项目记录，不创建第二执行账本。

## Safety And Privacy

仅本地明确合成输入及本票隔离工件，原试用、用户真实总用例、原 P0、全局 Skill 只读。未安装依赖/环境，
固定 C:/DevelopTool/Python311/python.exe -X utf8 -B。未运行外部模型、业务页面、远端写入或客户端自动审批。
继承三个安全负例原样保留；新的嵌套凭据验证沿现有 authoring 安全测试，不更改扫描器以制造全绿。

## Risks And Follow-up

状态 applied candidate；独立两轴审查和从原材料完整重生成由 Root 后续阶段执行，未冒充用户业务批准。
本票当前精确全套口径为313通过+1个已定向更新/验证的旧断言，不把最终24项或此前整套结果冒充当前整树全套全绿。
已收到独立 Spec 的 RTA-01 控制文字碰撞 P2，定位在 feedback.py 的 normalize_case/normalize_review_metadata；
依 Root 要求留给 fresh implementer，原逻辑未顺手修改，也不宣称消除该问题。XMind 客户端由用户导入验证；
本票仅公共计算/文件/恢复回归。静态扫描的三个继承合成负例不等于新增真实凭据。

Refs: RTA-02；本轮 plan.json；已确认 REQ/AC 与 CONTEXT.md；run/rta02/discovery.md；独立 Spec 的 spec-preliminary.md/json。
