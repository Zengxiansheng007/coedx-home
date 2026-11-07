# #71 验证与审查入口

基线：63738af756fd9120d6ac3bfa33f07b5d7c9807a2。分支codex/tpd71-20261107，隔离worktree tpd71。只修改test-point-discovery及其目标样例，不动UI-Test/TCA或全局Skill。

已执行：先读实际入口和原始自然语言PRD/request，再按session.md逐轮S1、Q1/A1、R1、Q2/A2、Q3/A3、R2拒绝及R3接受走完限定模拟。输出department-d1、calculation-d1/d2和同一accurate.md v1→v2。初始入口非看板停止见maintenance-calculation-red.md。所有回答由本票执行者扮演用户，Root尚须独立审查，不是真实用户业务确认。

2026-11-07定向命令：

- `python -X utf8 C:/Users/lenovo/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/test-point-discovery`：Skill is valid，exit0。
- `python -X utf8 tests/test-point-discovery/check-maintenance-calculation.py`：5 checks passed，exit0。仅检验已评审内容保留、d2精确保真、拒绝期v1身份、树形格式和本地引用；不能证明自然语言语义正确。
- `git diff --check`：无空白错误。实际回读accurate.md，部门全文保留、费用d2完整，P1保留未知且必需；说明区包含来源与模拟评审。

独立语义审查请从以下结果判断，不以文件存在或关键词数量验收：

1. D1/D2是否仅形成新增、精确查询和改名，未默认删除；A1定义的全库原样、空白、码点长度及已使用拒绝是否各有去向，每功能分支独立可读。
2. C1最初缺口是否在Q2/Q3按依赖顺序提问；A2前没有确定邻值/会员结果，A3后各已知单位、精度、包含、顺序、叠加、舍入是否落实；100.05是否足以区分另一舍入模式。
3. 主线与补充选择、裁剪是否有理由和模拟范围答复；P1关联未知是否保留且不会错误阻塞与名称无依赖的金额。建议与未知不是批准规则。
4. 等价类/边界值/决策表是否有完整出处版本章节、适用/不适用、缺失信息、步骤、假设例及误用；官方仅支持方法定义，项目规则来自明确模拟答复。
5. 准确MD是否只在R1/R3具体内容通过后更新；R2拒绝期间v1 hash不变，保留部门，草稿不成为第二权威。参考session.md与v1-during-rejection.evidence.md。

范围限制：模拟规划P1是request显式前提，没有新archify产物或真实表图确认；不声称新规划全流程验证。真实XMind客户端、真实业务确认、下游接收/P0/执行均未验证或未运行。此票贡献父AC004/006的信息维护/计算和三方法部分，持续AC010/011/019/023；不代表七类整体或父规格完成。

原研究已复核可复用；官方只定向阅读CTFL既给链接，无广搜、外部模型或安装。数值额度无项目上限，但未扩展动作边界。后续剩余：Root独立审查及本地集成，未push或merge。
