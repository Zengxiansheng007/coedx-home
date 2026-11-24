# CR-20261117-119 - 旧候选问题的准确历史索引

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | scripts-and-validation / references-and-assets / safety-and-governance |
| Source | CR118整套检查发现两处继承执行错误，同一旧恢复回归 |
| Baseline | bcd163b999e9da4501029789732caa658e0b722e；tree 8d98ad6d0661db6c1463ec1bfbd61b7ed045b449 |
| Author | Codex |
| Related Records | CR-20261117-118, CR-20261111-110 |

## Summary

反馈适配器构建已应用问题索引时无条件读取 id，合法生成候选中的无编号建议导致 KeyError。复用 clarification.start_grill 的非空编号筛选约定；只索引能够按明确身份准确匹配的问题。

## Context And Problem

本轮读取 CONTEXT.md、plan.json、req-ac-matrix.json、REQ-006/016/017、AC-007/019/020/021/034，核对反馈与唯一QA恢复契约、extension生成及clarification旧问题处理。原338检查中两处错误来自test_recovery同一测试及其handoff继承执行；独立原树单例再次复现KeyError id。原旧QA、测试fixture和CR118记录原样保留。

## Sections Changed

| File | Section | Change Summary |
|---|---|---|
| scripts/feedback_record.py | applied索引 | 仅非空id参与索引，一行产品改动 |
| scripts/test_feedback_history.py | 公开mixed回归 | 真实build_extension无编号建议与具名问题混合；空编号兼容、合法反馈回放及新跨例拒绝 |
| references/feedback-contract.md | 历史资格 | 无编号和空编号不获只读历史例外、不补号 |
| change-records | 本CR及索引/分类 | 本次根因、验证和范围追踪 |

## Decision And Alternatives

直接复用现有truthy-id约定；不改生成schema、不补编号、不改旧fixture、不忽略整个问题树或扩大跨例权限。只有id索引成员才可能与唯一QA当前问题、已应用问题完整相等，并且仍须已答且未重开。

## Detailed Change

缺失或空id的原候选建议被保留，但不能用来证明某具名问题已应用。精确历史相等、已答、未重开以及typed目标、当前路径和本例写目标检查继续执行；找不到准确已应用身份时，跨例问题仍按普通范围门拒绝。

## Impact Analysis

唯一生产改动在feedback_record；QA read/checkpoint/resume共用同一transition。原extension无id输出不变，已有clarification处理不变。原真实业务、unknown、data字面值、未apply、changed/reopened及反馈后续写负例全保留；最终同树执行整个recovery/handoff_revalidation/feedback_history三模块。

## Validation Evidence

| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| 原失败RED | 原RecoveryTests准确单例 | 1错误，KeyError id，未改旧fixture | red-original.json / red-original.log |
| 新mixed RED | 新公开mixed测试，旧产品树 | 缺id分支准确KeyError，空id分支原本可读 | red-mixed.json / red-mixed.log |
| 最终受影响GREEN | unittest -v test_recovery test_handoff_revalidation test_feedback_history | 24/24，35.247秒；外部调用37.531秒 | green-affected.json / green-affected.log |
| 镜像/语法/差异及旧记录 | 同字节、AST、git diff --check与git blob核对 | 最终结果见static.json | static.json |
| 结构/记录/敏感扫描 | create-skill --require-change-records | 继承负例独列，最终结果见检查记录 | create-skill.json / static.json |

全部外部证据位于 本地验收证据。产品测试完成后只补本记录，不再追加产品条件；随后一次commit冻结。未重跑338无关整套，Root负责最终整仓及独立审核。

## Safety And Privacy

仅独立worktree与明确模拟材料；既有Python311 -X utf8 -B，不安装。PowerShell状态变更经controlled runner，调用1800秒/测试子进程1200秒上限。无全局Skill、Root计划、原P0、旧trial、真实新稿QA/candidate、远端、UI或模型操作。RED预期失败由runner自动保留事件，不将其当作PowerShell语法问题。

## Risks And Follow-up

状态保持applied candidate；create-skill继承三条模拟凭据负例不在本次写集。独立Root审查、全套检查与真实具体稿验收分开。CR日期沿本轮预分配CR-20261117-119，实际检查跨到2026-11-18本地时间，原证据时间不改。

Refs: REQ-006/016/017；AC-007/019/020/021/034；references/feedback-contract.md；references/qa-record-contract.md。
