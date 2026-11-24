# CR-20261117-118 - 历史技术定位与本轮反馈目标分工

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | scripts-and-validation / references-and-assets / safety-and-governance |
| Source | 实际生成期间的历史来源疑点，经独立合成公开入口确认 |
| Baseline | e7ed8787ca894d578b22797e927a7e039d7e8fd2；tree b14e717aa46d0e1a34a081d30fe39929979b9efc |
| Author | Codex |
| Related Records | CR-20261117-113, CR-20261117-115, CR-20261117-117 |

## Summary

唯一 QA 中正常澄清已完成的跨用例技术来源目标，在反馈时被全部重新解释为本轮可编辑业务目标，阻断无编辑及仅本例的业务反馈。本轮保留准确历史，只对已声明技术来源位置作只读复用，不扩展本轮写权限。

## Context And Problem

当轮核对 CONTEXT.md、plan.json、req-ac-matrix.json、REQ-006/016/017、AC-007/019/020/021/034、反馈/唯一 QA/恢复契约及既有 typed field_role/source-binding 实现。合成两例经 start_record → append_questions → respond → summarize → apply_summary 保存来源导航成功，随后真实生成 MD 无编辑反馈与本例标题反馈均抛出 Feedback answer target must belong to its affected case，且失败前后 QA 字节一致。真实生成问答及旧试用未读写。

## Sections Changed

| File | Section | Change Summary |
|---|---|---|
| scripts/feedback_record.py | transition 与瞬时目标检查 | 只复用原样、已答、未重开且当前路径可恢复的已声明技术历史；新问题/实际答复仍按本例目标绑定 |
| scripts/test_feedback_history.py | 公开持久化正反例 | 无编辑/有编辑、typed来源、同名字面业务、跨例拒绝、反馈后续写入、checkpoint/resume与新进程 |
| references/feedback-contract.md | Same-task review chapter | 历史只读目标与新写集分工、来源/版本及隐藏消费者守卫 |
| change-records | 索引与受影响分类 | CR118可追溯证据及限制 |

## Decision And Alternatives

复用 review_expression.field_role 与 PROVENANCE_FIELDS，准确识别用例 technical_handoff 根和 case/step/claim 来源位置。data.value、input/output 子树的同名键保持业务字面值，未知结构不能自报技术身份。仅与当前 QA 历史问题完全相同、已完成且未列入重开依赖闭包的问题可保留跨例技术目标。旧答案不再次应用。不删除target_paths、不伪造case_id、不按question.field字符串白名单、不允许任意跨例、不新增schema或答案账本。

## Detailed Change

新、变更、开放和重开问题继续使用原用例归属门。已完成技术历史仅可保留读取；pending反馈期间的respond纠正及append_questions新发现同样执行本例目标门，防止旧只读技术目标变成暗写权限。正常clarification仍支持准确已声明的多例来源核验。

检索全部生产target_paths消费点：clarification的separate_impact空目标契约及respond更新范围、extension的分级建议目标、feedback的空目标新问题与feedback_record目标归属检查。qa_record._replay、read_record、checkpoint_record、resume_record共用同一transition，恢复没有第二种历史目标解释。其余消费点无需源码修改；定向公开测试覆盖其必要关联。

## Impact Analysis

只修改反馈记录适配器；纯feedback计算、来源注册、原始digest、内容版本、身份、共享数据隐藏消费者及完整依赖恢复均保持原门。永久事件和原问题/答复/目标身份完整保留。普通本例业务目标照常可用。需变更跨例技术事实时回正常澄清按准确范围记录。

## Validation Evidence

| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| 独立公开复现 | 合成QA正常clarification后进入反馈 | 无编辑MD与本例chat均失败，QA字节不变 | run/evidence/rta08-feedback-history/red-public-probe.json |
| RED | 新公开历史反馈回归，原源码 | 5测试中4处入口错误；原负例通过 | red-tests.log |
| 定向GREEN | 反馈、恢复、来源、字面值、控制owner模块 | 结果见最终验证附记 | green-targeted-verified.log |
| 消费点核对 | 全生产target_paths检索及QA回放调用链 | 唯一目标解释；无第二答案/恢复入口规则 | consumer-audit.json |
| 结构/记录/敏感扫描 | create-skill --require-change-records | 结果见最终验证附记；继承三负例不改 | create-skill.json |
| 镜像/语法/差异 | 字节比较、AST、git diff --check | 结果见最终验证附记 | static.json |

## Safety And Privacy

仅工作区合成入口、既有Python311 -B及本地静态检查。无网络、模型、UI、安装、发布、全局Skill、原P0、真实新生成QA/candidate、旧trial或Root计划写入。源/main及历史失败证据保留。PowerShell状态经既有受控runner，1800秒调用上限不改默认值。

## Risks And Follow-up

本轮只证明适配器和恢复契约，不等于真实生成具体稿或原生XMind客户端验收。独立双轴审核及整批真实反馈仍由Root安排；复用source117已通过408检查，最终只跑受影响模块，不重复整仓。一次测试启动误写不存在的test_cross_stage_recovery，改为实际test_recovery；随后恢复fixture使用不存在来源占位被守卫正确拒绝，改为真实隔离来源文件，均保留原失败日志，不修改产品来源门。

Refs: REQ-006/016/017；AC-007/019/020/021/034；本轮CONTEXT/plan/req-ac-matrix；references/feedback-contract.md；references/qa-record-contract.md。

## 本轮定向结果

- 独立 RED：正常澄清保存两例技术导航后，无编辑 MD 与本例标题反馈均准确失败，QA 原字节保持；red-public-probe.json。
- 新回归基线 RED：5 项中 4 处错误，均为原目标归属拒绝；red-tests.log。
- 受影响 9 模块：42/42，44.714 秒；green-targeted-42.log。此版本之后只增加“须与已应用 batch.questions 完全相同”的历史资格条件。
- 最终历史模块：6 项含新增 answered-unapplied 负例，green-history-final.log；其余 36 项结果按影响复用，不冒称最终整仓。
- 接口消费点核对：consumer-audit.json；QA read/checkpoint/resume 共用 transition；新解释器公开 resume 正例和真实来源漂移负例均覆盖。
- 最终镜像、AST、差异、create-skill 结构/记录/敏感扫描见 static.json / create-skill.json / diff-check.log。继承负例三项单列，不能当作扫描零发现。
- 当前轮次为本轮 CR118 一次修复；不新增项目数值额度限制，实际测试启动按上述三次受影响尝试与最终历史检查分别保留。无模型、网络、UI、安装、真实 QA/候选/旧 trial/全局写入。

- 最后仅收紧为“原样且已应用到 batch.questions 的历史”；最终新 6 项全部通过，12.384 秒，含未应用答复拒绝和两种恢复；green-history-final.log。此前42项结果不冒称最终整树重跑。
- 最终静态：180 文件镜像同字节，89 Python AST 通过，git diff --check 通过；static.json。
- create-skill --require-change-records 返回1：P0=3/P1=0/P2=0，仅继承 test_authoring/test_clarification/test_handwritten 三条模拟凭据负例，无新增；create-skill.json。未改扫描器或负例。
- target_paths消费审计见consumer-audit.json；正常clarification声明/答复和extension建议不修改，feedback空目标自动问答沿原规则，QA read/checkpoint/resume统一回放适配器。真实生成v4主作者独立公开反例归Root，不当作此合成回归的输入。
