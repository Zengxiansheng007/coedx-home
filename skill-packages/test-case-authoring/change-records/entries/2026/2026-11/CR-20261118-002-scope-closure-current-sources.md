# CR-20261118-002 - 复核当前来源与收尾保存边界

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | references-and-assets / scripts-and-validation / safety-and-governance |
| Source | 冻结 CR-20261118-001 的独立规格评审 |
| Baseline | f901ae21364c5600e06932a0bb3b2f9f23e25569 / d6fd16b202fe53b9552325c7010c5b545a1503dd |
| Author | Codex |
| Related Records | CR-20261118-001 |

## Summary

收尾对每个选中用例重新回读当前依赖。同版具体审批仍与其原候选一致性核对，复用旧版评审时继续核对同一问答中的原审批完整含义。问题或候选在保存间隙变化时，保留实际落盘的问答和临时行，重新读取后决定后续操作。

## Context And Problem

REQ-020 / AC-026—028 要求先保存并回读具体评审与处分依据，再清理已收尾范围。前轮独立审计读到实际 QA 的 14 条临时行，后续独立规格探针在模拟 QA 中确认同版审批跳过来源回读。另一个探针在复核后、永久保存前通过公开入口加入待答 Q77，旧实现仍按已失效的覆盖删除 B1。更换实际候选也可能在拒绝清理前留下旧候选的永久依据。复现证据见项目 `run/evidence/review/spec-scope-current-review-drift-result.json` 和 `spec-scope-concurrent-question-result.json`。

## Sections Changed

| File | Section | Change Summary |
|---|---|---|
| scripts/qa_record.py | 同版/旧版评审还原、永久保存与清理 | 用实际稿目录回读当前来源，永久保存和临时清理各自核对绑定内容 |
| scripts/test_scope_closure_current.py | 模拟问答公开关闭入口 | 来源正常、漂移、缺失、无关来源变化，候选变化，问答并发发生在永久留证前和后 |
| references/scope-closure.md | 关闭与中断接续 | 逐例核来源与保存冲突时的一次重读 |
| change-records | 索引、三类台账及本记录 | 保留前轮冻结记录与新轮来源 |

## Decision And Alternatives

复用 `restoration.preflight` 及原保存入口。当前来源只对所选用例的阻断作决定，旧审批另保留严格完整父源和历史比较。用同一次读取的字节解析问答永久和临时区域，原子替换前再比较实际问答及候选。永久写入后发现非本次保存的事件时，保留当时真实已保存的内容与原临时行，结束本次尝试。

## Impact Analysis

正向路径仍包括独立内联同版用例、局部反馈后经证明未变的旧版评审和有效持久化依据的接续。同次关闭期间其他编辑也会中止，重新读取后可通过同一个入口继续。校验复用现有原子替换，检查与替换仍是两个文件系统动作，调用方仍应按原流程保持单写。

## Validation Evidence

| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| RED | Python311 -X utf8 -B -m unittest -v test_scope_closure_current | 6 项，5 个失败实例，两个正向用例通过 | red-current-closure.json |
| GREEN | 同一新公开入口测试 | 6/6 | green-current-closure.json |
| 定向回归 | 关闭、问答、反馈、恢复、还原、关联步骤和公共范围套件 | 以最终同树记录为准 | targeted-final.json |
| 变更记录与静态检查 | create-skill --require-change-records、AST、镜像逐字节、历史记录保护 | 以最终同树记录为准 | static.json / create-skill.json |

检查记录位于项目 `run/evidence/rta11-closure-current-source`。候选冻结后由集成角色独立重跑整套与评审。实际业务 QA 收尾和客户端验收由各自执行证据支持。

## Standards 复核修正

按项目 CONTEXT.md 的中文注释约定，同步修正两份包中本记录对应的源码和回归测试说明。测试模块首行说明同步翻译，原断言、错误消息和数据字面值均保留。等价校验与冻结回执见项目 `run/evidence/rta12-comments/receipt.json`。

## Safety And Privacy

本轮只读需求、既有冻结与审计证据。回归为隔离文件和明确标注的模拟业务。实物 QA、既有审批、先前冻结、全局安装和远程发布均保持原状态。结构校验与敏感扫描包含在本轮静态检查。

## Risks And Follow-up

本地文件一致性检查依赖生产运行的单写约定。完整集成验证、独立评审与本批真实范围收尾尚需各自的证据。继承的三条合成凭据负例继续用于原安全测试。

Refs: REQ-020；AC-026、AC-027、AC-028；references/scope-closure.md。
