# CR-20261118-001 - 原审批证明与明确范围收尾

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | core-skill-md / references-and-assets / scripts-and-validation / safety-and-governance |
| Source | 当前唯一 QA 的独立范围收尾审计及已确认 REQ-020 阻断 |
| Baseline | 3b05ada918b4f7d51a2f0b3393e0d87c3f0aca05；tree 49f6cfb42af1418f735e9ce6d02e75c61e33679f |
| Author | Codex |
| Related Records | CR-20261116-004, CR-20261117-113, CR-20261117-119 |

## Summary

局部反馈保留未变用例的原 final_review，而关闭入口只接受全批当前版本，导致合法保留审批无法收尾。仅修改现有 close_record_scope：从同一 QA 真实评审事件还原原快照，证明完整用例及实际依赖、来源、适用和显示含义均未变后复用；原审批不重签、不改版本。旧覆盖观察缺 case_ids 时，可在原关闭入口提供有据 scope_bindings，随原永久收尾事件保存，不清空汇总。

## Context And Problem

本轮读取 CONTEXT.md、plan.source_requirements 三份实际需求/规格、req-ac-matrix.json、scope-closure-audit.md/json，以及当前 QA、反馈、范围、还原与显示契约和实现。REQ-020/AC-026—028 引用 stage-delivery 文档，避免与 presentation 同编号主题混用。审计确认当前14临时行无 case_ids；默认拒绝正确，需要准确补归属，而不是按 resolved/topic 自动猜。十例有效原审批保留与全批版本门冲突属于独立产品缺陷。当前真实新稿、旧 trial、全局技能、Root 计划与报告只读；本实现只以隔离通用模拟材料重现及验证。

## Sections Changed

| File | Section | Change Summary |
|---|---|---|
| scripts/qa_record.py | close_record_scope 及其私有证明辅助 | 同 QA 原审批快照、完整依赖/显示/范围比较；显式有据绑定；保留默认拒绝与原子保存/回读 |
| scripts/test_scope_closure_reuse.py | 公开实际文件回归 | 两例局部反馈、无关/相关数据、整例/P0来源、显示/频次变化、缺 scope、负向绑定、中断/幂等 |
| references/scope-closure.md | 原审批复用与补绑定 | 准确参数、现场摘要示例、来源边界、原有证据与汇总保护 |
| references/coverage-review.md / SKILL.md | 首次覆盖与旧任务收尾 | 已有具体用例时明确 case_ids；无具体稿的规划分支继续保留 |
| change-records | 索引、四类台账及本记录 | 本次根因、范围及验证追踪 |

## Decision And Alternatives

复用现有唯一 QA、restoration.preflight、scope_context、operation_scopes/active_scopes、typed source_binding 与活动显示投影。原评审快照只取同一 QA 真实 review/review_feedback 的回放结果；种子中的 approved、自报 unchanged、外部摘要均不构成原审批证明。缓存只活在本次调用内。current source_catalog 仍经过既有准确父源/当前 P0 门，历史来源只取当时事件。外部 technical_handoff.source_ref 须有历史 sha256 且实际回读匹配；未知或未绑定外部来源保守拒绝。

不选择重新批准所有未变用例、改 final_review 版本、重放已答/汇总/反馈、手改 MD、放宽未归属分支，或另设答案/审批权威。显式 scope_bindings 绑定永久 branch 原值计算摘要、精确 case_ids 与来源依据，随已有 scope_closure 保存，原 coverage 行保持。已有及永久补绑定的归属不能覆盖，失败不先写收尾依据。

## Detailed Change

候选仍须与唯一 QA 回放完整相等且实际保存。每个待关闭用例必须同版具体通过，或其完整用例与本 QA 原评审快照完全相同并且完整还原、实际引用数据/整例、来源注册、公共适用/例外/频次及活动可见表达均相同。缺依赖、来源漂移、显示含义变化及无法证明均阻断。原 case/data、content_version、final_review 和实际原话保持不变。

默认无 case_ids 仍拒绝。scope_bindings 必须提供准确 branch_id、branch_digest、case_ids、provenance；只绑定本次选择的已处置分支，归属完全在具体批准范围内。未完成/其他范围、未知/待产品影响、永久问答、原编号及 highwater 保留。先永久保存再原子清理临时区；中断按准确相同参数重试，既有 prepared 证据复用，不重复审批。新变化使用新 B/Q 并引用旧决定。

## Impact Analysis

只改现有 QA 关闭 seam 与直接说明/回归，canonical 与 .agents 镜像同步。普通同版通过和旧 scope_closure 五项测试原样保留；生成、MD mapper、710探针性能、旧 UI-Test 执行层、真实新稿反馈/恢复、全局安装及发布不在写集。本轮公开模拟验证不等于当前真实14行已清理，更不代表真实用户批准、NativeXMind 或业务执行验收；真实收尾由单写作者在独立审查后实施。

## Validation Evidence

| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| 原缺陷 RED | 实际两例 QA：v1 两例审批→只改/审 LINK v2→关闭两例 | 精确报 Concrete current-version review required | red-reuse.json |
| 第一纵向 GREEN | 新公开复用单例与原 scope_closure 五例 | 6/6 | green-reuse.json |
| 绑定/范围扩展 | 公开新模拟文件与中断恢复 | 8/8 | green-scope-bindings.json |
| 首轮依赖探针 | 完整依赖及来源维护样例 | 5 个测试设置错误，原失败完整保留；未据此改产品门 | dependency-source-probes.json |
| 修正依赖探针 | 补真实完整断言；来源/定义维护使用既有拒绝契约 | 14/14 | corrected-dependency-probes.json |
| 受影响预检查 | 原关闭/QA/feedback/恢复/显示/范围及新回归 | 90项中85通过；5项既有写盘测试系统 sandbox TEMP 原子替换 WinError5，保留原失败 | targeted-final.json |
| 展开owner RED | 有真实整例依赖的未改根例，仅活动显示预期改义 | 原helper错误放行；精确公开断言失败 | red-expanded-display-owner.json |
| 展开owner GREEN | 回原始owner核显示及实际来源；逐依赖核适用/频次 | 15/15 | green-expanded-display-owner.json |
| 最终受影响同树 | 原关闭/QA/feedback/恢复/显示/范围及新回归；仅子进程TEMP/TMP使用本轮授权目录 | 92/92，59.758秒；含16项本轮公开回归，原五项关闭测试未改 | targeted-final-r2.json |
| 镜像/AST/差异/原测试保护 | 全包逐字节、Python AST、Git diff --check、旧测试 blob | 结果由最终 static.json 精确记录 | static.json |
| 结构/记录/敏感扫描 | create-skill --require-change-records | 继承三条合成凭据负例预期保留，无真实新问题；准确结果见文件 | create-skill.json |

证据目录：本地验收证据。PowerShell 状态动作经原 controlled runner，outer1800秒、run_record inner1200秒；原测试及失败记录保持。TEMP修正仅外部本轮检查器的子进程环境，不改测试、产品或全局环境。展开owner问题于预检查退出后独立RED确认：瞬时 resolved_case 改变原owner摘要，故显示必须仍从原始owner定位；根例及每个传递依赖分别核活动显示、实际来源及公共义务，完整展开操作/数据独立比较。最终冻结单次源码提交，Root 负责整套及独立双轴审查。

## Safety And Privacy

只读原来源/实际审计、独立 worktree 和新模拟目录。固定 Python311 -X utf8 -B，无新依赖/环境、模型、网络、UI 或外部发送。没有实际调用主 QA 的 read_record/close_record_scope，也未复制改路径运行它。没有新业务审批、倒改历史、安装、发布或生产写入；所有模拟答复均显式 SIMULATED。

## Risks And Follow-up

状态为 applied candidate；本地三条历史合成扫描负例保留，不能将其称真实凭据或改全局扫描器以制造通过。保守拒绝无法证明的外部引用、范围或显示变化；需要真实来源/受影响评审而非调用者自报未变。原真实批次收尾、完整工程套件、独立规范/规格审查与后续客户端/业务验收分别登记，不用此记录替代。

Refs: stage-delivery REQ-003/006/016/017/020；AC-003/007/019/020/021/026/027/028/034；references/scope-closure.md；references/coverage-review.md；references/restoration.md。
