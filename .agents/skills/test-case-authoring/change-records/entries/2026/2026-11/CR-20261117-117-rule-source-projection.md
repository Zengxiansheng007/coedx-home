# CR-20261117-117 - 有效规则解释的来源投影

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | scripts-and-validation / references-and-assets |
| Source | 实际重新生成具体稿拒收后，独立公开 API 实证 |
| Baseline | ea8300d39d97af469ba546d0e166bc82c502fae1；tree ba0ffc74a09222ac9b7d7b7aa53559fe9bf2e96f |
| Author | Codex |
| Related Records | CR-20261117-113, CR-20261117-115, CR-20261117-116 |

## Summary

scoped_review 的元数据和步骤使用逐叶投影，规则解释却读取原 case，导致明确 technical 的治理过程仍以已确认规则出现在正文，同时在 Agent 说明出现。本轮只贯通同一来源投影，保留原规则身份、状态和真实缺失判断。

## Context And Problem

修复前核对 CONTEXT、plan、req-ac-matrix、源 REQ-008/014/016/017、AC-009/017/019/020/021/034，以及 source-assessed-display、review-expression、唯一 QA、公开反馈和恢复契约。独立 prepared/build_extension 合成来源经 assess_review_projection 后，render_review_batch/render_extension（准确 parent）的对话和 MD 四处仍显示治理解释；模块说明同时已有精确源路径。真实 candidate/QA 只读，未修改。

## Sections Changed

| File | Section | Change Summary |
|---|---|---|
| scripts/scoped_review.py | _render/_rule_lines | 解释及条件读逐叶投影，原记录选择有效身份/真实状态/缺失；省略不触发长答复回退或未知占位 |
| scripts/test_rule_projection.py | 公开评估到两种渲染 | technical/readable/duplicate、旧决定、独立条件、真实未知和来源漂移 |
| scripts/test_projection_full_lifecycle.py | 同一 QA 实际文件链 | 生成评估、具体稿评审、反馈复评、checkpoint、新进程恢复保持规则投影 |
| references/source-assessed-display.md | 规则解释投影 | 明确省略与真实未知、来源和长答复归属 |
| references/professional-generation.md | 规则解释与实际来源 | 决定含义和复用过程分工；动作/数据/具名结果各自核依据 |
| references/qa-record-contract.md | 解释及过程持久化 | 同一 QA note/qa_ref 复用，直接指向生成契约 |
| change-records 与 .agents 镜像 | 本次写集 | 同字节镜像及记录 |

## Decision And Alternatives

复用现有 project_record、逐叶角色和 owner/source 绑定。原始来源与决定完整保留，只显示投影变化；不引入 schema、答案台账、关键词黑名单或语义分类器。旧候选无评估按原有效规则显示，显式空 active 集合不复活历史。真正缺失或未知保持待核。状态及延期影响仍读原控制语义，不能因显示评估改变业务资格。

## Detailed Change

按原规则身份选择对应投影记录；interpretation 与旧 actual_reply 的选择基于原始是否存在有效解释，正文值取当前投影。显式省略的有效叶不再回退到整轮原话。answered_parts、暂定预期、产品核对、有效性、适用条件、范围差异及延期影响继续按实际用途保留。历史文本只由真实来源逐叶处置，不能因自由业务字段名删除规则。

## Impact Analysis

首次生成、范围副本、扩展、反馈及恢复共享 _render，无需新增入口或改变唯一 QA 事件。duplicate 保留门仍使用实际最终业务投影；精确 parent 样本可通过，未发现需要改动其父源 seam 的实证，因此不扩大写集。直接生成契约同步防止作者将复用/提问过程当成产品规则，源 claim 则分别核动作/具体数据/具名结果依据。

## Validation Evidence

| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| 独立公开实证 | prepared → assess → review/extension | 四处 body 泄漏；说明已有源路径；原 batch 未改 | run/evidence/rta07-rule-projection/red-public-probe-final.json |
| RED | 新公开规则测试，原源码 | 三种有效决定来源均失败 | red-test-baseline.log |
| GREEN | 受影响十模块 unittest | 43/43，44.540秒 | green-targeted-final.log |
| 同 QA 全链 | 真实合成文件反馈与新进程恢复 | 同 QA 实际文件与新进程恢复通过 | green-targeted-final.log |
| 结构/记录/敏感扫描 | create-skill --require-change-records | 与继承三负例比较；不改扫描器 | create-skill.json |
| 镜像/语法/差异 | 同字节/AST/git diff --check | 178文件同字节、88个Python AST通过 | static.json |

## Safety And Privacy

仅合成公开入口验证，无真实 UI、网络、模型、依赖安装、全局改动或业务写入；原 P0、旧 trial、实际新稿 candidate/QA 和 Root plan 不改。原始长答复仍留同 QA，技术说明仅引用精确源叶，不复制整轮答案。

## Risks And Follow-up

本地检查只证明契约实现，不代表真实具体稿业务通过或原生 XMind 验收。真实新稿应用评估和重新语义审查由原授权作者/独立评审执行。本轮复用此前未受影响 404 全仓结果，不重跑整仓；新增改变由定向公开接口、结构、记录、镜像和语法验证覆盖。

Refs: REQ-008/014/016/017；AC-009/017/019/020/021/034；本轮 CONTEXT/plan/req-ac-matrix。

## 最终定向结果与限制

最终受影响十模块 43/43 通过（44.540 秒），基线 RED 保留：同一公开测试的三种规则来源均失败。
新逐叶规则四项用例覆盖技术/可读/重复和不可见目标拒绝；同一 QA 串联保留真实文件反馈与新进程恢复。
此前一次 42 项测试有 41 通过，CLI 原子重命名在沙箱默认临时目录 WinError5；独立直接公开写入口实证后，
只将测试进程 TEMP/TMP 指向本轮授权 evidence/tmp，最终 43 项均通过，产品文件和全局环境未因此更改。
原始公开 probe 两次接口假设错误及换行匹配导致的中间源码错误均保留外部日志和自动事件，不算产品缺陷或通过证据。
create-skill --require-change-records 返回 1，仅既有 test_authoring/test_clarification/test_handwritten 的三条凭据负例；
P1/P2 为 0，无新扫描发现，不修改负例或扫描器。178 镜像同字节、88 Python AST、git diff --check 通过。
审查 `_rule_lines` 消费者仅共享 _render；生成、反馈、QA回放和恢复均复用它，无额外产品调用旁路。
准确 parent 的 duplicate 公开样本及不可见目标反例均通过，无证据支持扩大到 review_projection 参数改造，保留其原门。
提交前当前集成 tip 与本票 parent 同为 ea8300d39d97af469ba546d0e166bc82c502fae1，同树已核，无需合并新变更。
状态保持 applied candidate，独立代码审查、真实新稿评审和客户端验收分别由 Root 接续。
