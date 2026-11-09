# CR-20261109-001 - Business Before Planning

| Field | Value |
| --- | --- |
| Status | validated |
| Target Skill | test-point-discovery |
| Change Type | fixed |
| Scope | core-skill-md / references-and-assets / scripts-and-validation |
| Source | issue89, confirmed S5/R22 |
| Baseline | cdc663bd112680a2abfba6e0fb4501092d57f025 |
| Author | Codex |
| Related Records | CR-20261109-006 |

## Summary

先分别理解保存、取消、提交审核等操作与业务衔接，实际处理影响划分的问题，再提出模块表图并等待确认。

## Context And Problem

原入口先给候选安排再整理关联，流程参考另要求整体阶段独立出流程测试点，与 issue89 确认的顺序相反。原始基线演员首轮正确提问，没有观察到该轮行为失败。其第二轮实际规划却把 F01 跨模块流程单列为首项，并要求先具体流程评审再进入 M01/M02，这与当前模块承接流程检查的顺序冲突。原始两轮均保留，第二轮提供有限的行为RED，不把首轮成功改写为失败。

## Sections Changed

| File | Section | Change Summary |
| --- | --- | --- |
| SKILL.md | 步骤3/4/6及完成判定 | 整体问答先行，独立初始入口验证 |
| references/planning-confirmation.md | 规划前业务理解 | 划分完成条件与操作示例 |
| references/workflow-lifecycle.md | 流程分析、范围 | 整体分析承接约定模块，移除独立提前出稿 |
| references/dashboard-intake.md, information-maintenance.md, async-exchange.md, roles-entitlements.md, rule-calculation.md | 新规划入口 | 到达划分条件再应用分支参考 |
| references/module-clarification.md, writing-review.md | 阶段适用 | 整体阶段仅整理依据 |
| tests/test-point-discovery | requests/rubric、flow89虚构夹具 | 初始入口与逐轮实际回复 |

## Decision And Alternatives

复用现有自然语言入口、问答和 archify 契约，增加规划前语义完成条件。无需新状态机或额外依赖。仅追加原则会保留相反路径，因此替换原冲突顺序。当前模块集中生成细节由后续工单处理，本票限定整体阶段。

## Detailed Change

资料已明确的规则直接保留依据。影响划分的未知关系先问并等待实际答复，用户明确延期等处置保留未知影响，方向未知留双方注记。主要操作分别分析，实际职责与对象决定模块，保留全部七类、实际 archify 表图、规划确认和模块深入。

## Impact Analysis

入口、规划、跨模块流程、七类入口及编写旁路同步核对。其余方法/反馈/交接/读取器无规划前路径变化，无需改下游。历史实际问答、失败、图形和冻结runtime清单保留。格式与脚本字节未改，旧客户端与读取器验证按此边界复用。

## Validation Evidence

| Check | Command or Method | Result | Evidence |
| --- | --- | --- | --- |
| Pre-edit plan | 固定基线、写集、AC、复用 | recorded | TASK/evidence/89/plan.md |
| RED | 文档契约及实际基线第二轮 | 首轮正确问答，第二轮独立流程先评审路径与新顺序冲突 | TASK/evidence/89/red-document-contract.json, TASK/evidence/actor-baseline/QA-baseline-001.md, QA-baseline-002.md |
| Static | create-skill --require-change-records | P0=0/P1=0/P2=2，validated-candidate | TASK/evidence/89/validation/create-skill-green.json |
| Reader regression | unittest discover test_xmind_reader.py | 3/3 pass，源码/测试与基线字节相同 | TASK/evidence/89/reader-tests.txt |
| Repository regression | tools/checks.py --output-dir TASK/evidence/89/repository-checks | pass，运行原有仓库必跑检查 | TASK/evidence/89/repository-checks-output.txt |
| Sensitive scan and references | 候选26文件扫描与包内引用检查 | 0 static errors，常见凭据模式未命中 | TASK/evidence/89/candidate-static.json |
| Behavioral current supplement | 新演员初始入口、主持另发答复、实际表图及规划确认 | issue89 四AC在已检查的有限虚构模拟范围成立 | TASK/evidence/candidate-actor/QA.md turns1–3, TASK/evidence/89/independent-review.md Actual green checkpoint supplement |
| Graph corroboration | 实际finalize回执及1440浅色视口读图 | validate/deliver/check/browser-check均pass，模块/顺序/同ID标题正文边及三块说明可见 | TASK/evidence/candidate-actor/planning-v1/plan.finalize-summary.json, visual-check/plan.visual-check.1440x900.light.png |
| Current reconciliation | 最终评审发现后的状态、引用与范围复核 | 本地validated-candidate，静态及回归证据见CR006 | TASK/evidence/final-fix/validation/candidate-static.json, CR-20261109-006 |

TASK指本轮工作目录 work/test-point-discovery-flow-20261109，所有证据位于克隆外。包内语义规则和本地验证均为候选证据，实际人工决定不由关键词或脚本替代。

## Safety And Privacy

仅虚构资料，未读取真实PRD，未改全局或下游，无远程写入。现有隐私和授权边界适用。本轮未请求宿主提升或安装，工作流确认属于人工语义条件，无OS级强制门声明。

## Risks And Follow-up

历史提交cd9dbd048c63c16212bc66245ee40cd6cda794a0交付时，独立候选模拟与审查尚待调度，故原冻结记录为applied，Behavioral为pending，原预定路径TASK/evidence/actor-green89。该检查点保留在原提交中。实际随后完成的有限模拟及独立审查记录于上述真实路径，本次CR006将当前记录与索引、分类账同步为validated，仅表示本地候选证据完成。

实际QA turns1–3从未规划虚构资料开始，先Q001–Q003，再另收主持答复，实际表图/Q004展示后另收规划确认，并按主持要求暂停模块深入。图候选SHA256为3247a04bf8ac5caa9001856712cb6323d0b66bcedd2fed48aa5f3869902049e6，HTML为fe330b1ffd3d8359948a2aff019e08e02922adf38d4fbf8077dfa3f225bb8325。1440浅色视口已独立读图，较大深色视口底部截断仍保留。实际原始QA、回执、失败与独立评审均保持原字节。

初次静态检查因既有中文章节不匹配验证器英文标题而失败，保留原输出，现有标题补充英文后通过。P2两项为中文触发词未匹配英文启发式，以及读取器经XMind参考间接链接，均保留并记录语义适用理由。后续issue90—93运行时存在明确切换，增量链不能充当最终单一冻结运行时复演，最终六项观察须在修复复审后另行运行。真实客户端未重跑，格式未改。真实PRD用户确认、业务系统正确性及宿主接受仍未验证。

Refs 为本次 inputs/issue-89.md、原访谈 Q016/Q017/S5/R22、核心 v0.8 REQ-002/024、细节 v0.2 §0/V13、测试入口提案及逐票计划。实际成文历史待审标签保留，以已确认S5和发布工单为当前依据。
