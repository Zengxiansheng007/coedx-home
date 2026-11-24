# 同一任务的问答记录

## 跨阶段保存与新上下文恢复

恢复先实际读取本 MD、当前候选和必要来源，再继续未决工作。使用
`resume_record(qa_path)` 获得回放状态及实际文件差异；它是只读核对，
不自动处理业务冲突，也不批准候选。旧记录没有 checkpoint 时返回
`needs_checkpoint=True`，保留其有效历史；先定位并读取当前候选和来源，
不要因旧记录缺少新元数据重新询问已确认决定。

暂停或阶段切换时先保存实际候选 JSON，然后调用
`checkpoint_record(qa_path, stage, candidate_path, sources, next_step)`。
stage 为 `p0/report/p1-p2/review`；sources 是实际文件路径及其影响问题的
`question_ids` 列表，例如 `[{"path": "source.md", "question_ids": ["Q1"]}]`。
阶段级事实允许空列表，不能把空列表解释为无影响。脚本实际读取文件并
保存来源摘要、候选定位及下一步到同一 MD；候选必须与当前回放完整一致。
来源身份摘要不是业务结论，仍需读取原文核对具体含义、版本和适用范围。

P1/P2 候选还必须传 `extension_evidence=实际证据JSON路径`。该文件沿用
既有 `check_extension` 输入：`catalog`、`baseline`、`reports`、`request`，
合成材料显式指定 `mode: simulation`。它是必要技术来源，不是新审批或
人工展开稿。checkpoint 和 resume 都重新还原完整动作、当前数据、预期、
断言及声明终点，重新核对当前完整 P0 资格及活动引用的源版本、步骤和数据。
历史未再引用的定义继续留存，不作为活动依赖阻塞。没有当前证据的历史
P1/P2 checkpoint 仍可恢复问答，但不能宣称交接核对通过。

接收方读取同一问答 MD、候选 JSON、来源文件及上述证据文件，核对
`conflicts` 为空后使用瞬时 `complete_batch`；不落盘人工维护展开版。
证据变动、缺失或还原失败时 `complete_batch` 为空，返回具体冲突。
该结果保留原审批状态，不授予合并或执行权限，也不证明下游 UI-Test
已支持当前契约或业务测试通过。未知规则继续原澄清，默认反馈仅影响当前用例。

报告核对继续使用 record_context/record_note，不新建批次问答。实际进入
P1/P2时用 `advance_record(qa_path, 'start_extension', payload)`，payload 包含
既有 build_extension 的 `envelope`（catalog、baseline、reports、entry_request、
design）、完整新问题 `questions` 和实际 `source_ref`；仅合成验收显式传
`mode: simulation`，真实任务沿用默认 production。它重新调用既有完整P0
门和候选编写入口，不靠阶段名称、用户选报告或已保存 checkpoint 放行。
已保存的报告选择、范围/排除与规则决定从同一 MD 读取并在设计中引用，
不得要求用户重复未变答案。旧阶段状态保留在 `prior_stages` 投影及原事件，
旧未决与暂定条件保留其影响，不自动判为解决。新阶段新问题使用未用过的
Q编号；相关旧决定发生变化时保留原Q及答复来源，在新问题说明改变与依赖。
后续评审继续 start_feedback/apply_feedback/review_feedback 的既有路径。

恢复时逐项核对技术投影的决定来源、实际候选内容及其版本。候选不同或
来源变化只定位冲突，不覆盖任一输入。回到实际Q/答复/源条目，核对对象、
条件和受影响依赖；无关明确部分继续整理，相关候选更新等待澄清。不能因
一个来源变化将所有决定重新问一遍。MD正文与事件本身不一致时保留原文件，
明确无法安全追加的原因与待保存内容，先核实真实原话；不新建第二份答案。

保存抛出异常时如实展示待保存的问题/原话、动作和同一MD恢复路径。
advance_record 的写入 OSError 带 `pending_payload/pending_action/record_path`；
未返回成功不表示动作已保存。回读实际文件确认最后成功事件后再恢复，
只重试真实未落盘动作，避免回读失败后重复已写入答复。初次保存或其他读取
失败也依照实际磁盘状态报告，不能声称已完成。用户无需维护技术字段。

各入口沿用正常中文完整提问；恢复本身不是额外业务审批。实际问答与候选
供新上下文读取，聊天记忆、评分标准与预写成功答复不能充当交接材料。

开始业务规则提问前，读取本任务已有问答 MD、当前候选和相关源文件。
首次任务固定一个获授权的问答路径。报告选择、规则、评审回问及后续阶段
继续使用它；阶段变化追加章节，不能另起一份答案。此处提供规则入口的
最小记录契约，报告核对与覆盖的业务判断仍遵从各自契约。

## 对话与实际决定

共同提问、部分答复追问、汇总交付和继续意图按宿主同名加载的
**test-grill-me** 执行；TCA 的阶段与公开入口映射见[阶段适配](stage-adapter.md)。
下面只规定本任务持久化和专业决定的含义，不另维护一套共同对话流程。

- formal：实际明确确认的规则，记录确认者来源，不冒充产品确认。
- provisional：明确授权的 authorized_expectation 和待产品核对的
  product_check；单独“先继续”不能补出预期和条件。
- deferred：实际明确搁置，记录影响，不写候选更新。
- partial/unknown：仍未决，不是自动搁置或产品待确认；原话先
  record_note 保存回读，然后 respond 记录真实已答部分。

## 持久化公开入口

### 显示评估与公共/特殊归属

实际生成、反馈和恢复均通过同一 `advance_record` 保存两种现有纯评估的同名动作：

```python
state = advance_record(qa_path, 'assess_review_projection', {
    'source_version': state['batch']['content_version'],
    'basis': actual_source_locator_and_reason,
    'assessments': actual_leaf_assessments,
    # 有父源的范围副本传准确完整 source_catalog，不能传展示子集。
    'source_catalog': source_catalog,
})
state = advance_record(qa_path, 'review_preparation_scope', actual_scope_review)
```

显示参数见 [逐叶评估](source-assessed-display.md)，公共与本例特殊参数见
[适用归属](aggregation-contract.md)。这些事件只改变原 batch 的显示元数据、
来源绑定及当前视图；问题、真实答复历史、未决和业务确认保持，不记录执行请求。
未完成的反馈先走原反馈确认流程，不用元数据动作绕过它。

推荐顺序：原来源与真实答复核对 → 正常汇总应用 → 实际显示/适用归属评估保存 →
具体稿评审 → write_artifacts → 实际 MD 回传 → 原反馈汇总/应用 → 受影响部分复评 →
write_artifacts → checkpoint/resume。真实业务或来源变化后按当前 owner 重新评估
失效部分，不能沿用旧绑定。新 review/review_feedback 事件给原话生成同 QA 精确锚点；
Agent 说明引用该 qa_ref，历史事件和确认文字保持原样。

普通 review 也可在 payload 提供准确完整 `source_catalog`；事件回放和评审渲染
使用同一源。含父源的候选交付继续把该材料传给 render_review_batch、write_artifacts，
checkpoint 使用实际 `source_catalog_path`。P1/P2 的当前 P0 证据仍必须通过既有
`extension_evidence` 路径核验；评估事件不替代该门。不要新建可独立修改的答案 JSON，
也不要改 candidate 去迎合 checkpoint。

`scripts/qa_record.py` 是对现有 clarification 纯 API 的薄适配。
MD 内事件保存实际来源，技术状态按事件回放；不要另存可独立编辑的
答案 JSON。返回候选里的 qa_ref 指向同一 MD 的 Q/答复版本。

```python
from qa_record import start_record, read_record, advance_record
session = start_record(qa_path, task_id, batch, questions)
# 只有保存并回读成功，才全文发送 session['chat']，然后等待实际回复。
session = advance_record(qa_path, 'respond', actual_replies)
# 实际回读原始来源、答复历史和直接依赖，发现新问题先 append_questions 并等待实际答复。
session = advance_record(qa_path, 'record_coverage', actual_source_review)
session = advance_record(qa_path, 'summarize')
# 按 test-grill-me 展示汇总；仅确认时先 record_note 保存版本/范围并等待。
# 只有确认且明确继续（或已有有效继续授权）才调用下一行；不可仅为保存确认而应用。
session = advance_record(qa_path, 'apply_summary', actual_confirmation)
# 展示更新后的完整用例，单独等待本版本完整评审。
session = advance_record(qa_path, 'review', actual_review)
```

questions 沿用 clarification 字段，另需 evidence、boundary、example_kind
（hypothetical 或 evidence）。所有提问内容用中文编写。actual_replies
沿用 decision/updates 等字段，另需 source_ref（实际对话或材料定位）、
interpretation（归纳），暂定还需 authorized_expectation。程序添加
answer_version、qa_ref，不能让用户手工维护技术字段。

每轮和汇总前按[来源覆盖流程](coverage-review.md)实际检查原始条目去向，
用 append_questions 追加遗漏题、record_coverage 保存主题和处置；两者同样
写入本 MD 后回读。全部登记题已答完不等于来源覆盖完成。

复合问题增加 answer_parts 字典（稳定子项名→具体问题描述），分别核对对象、
条件、行为；同一维度有多个可独立回答的检查时继续细分。答复的 answered_parts
只填原话明确提供的子项；程序累积已答并返回 remaining_parts，已答项不重问。
partial/unknown 是答复完整性状态，不新增业务授权路径，且不可带候选 updates。
formal/provisional 需全部子项明确；deferred 可明确搁置未知内容，仍不补出规则。
完成回答后的 summary 同时携带累计 answered_parts，历史答复与 qa_ref 保留在同一MD。
若采用暂定路径，应明确写出各剩余子项的暂定预期及产品核对条件。

依赖按具体规则声明，不以同一用例或字段为由关联全部问题。独立题同轮展示；
当前轮未答题保留，依赖等真实前提。改口只重开声明的后代，保留其历史，
重新核对受影响子项；无关明确答复仍有效。不要把候选待汇总状态当成可执行。

每次 advance_record 都先读取同一 MD，调用既有状态转换，原子保存再回读。
报告核对的事实和完整问题用 record_context 保存 display 和 basis，不伪造
actual_reply；实际报告选择用 record_note，read_notes 从同一 MD 回读。
这两类事件不改变候选规则；具体顺序见[报告核对](report-reconciliation.md)。
写失败时明确告知尚未保存的原话和停止位置；不得声称已记录或继续依赖
该记录的汇总和更新。人工编辑导致正文/事件不一致时先核原话，保留冲突，
不任意覆盖。该工具是本地工作流校验，不是宿主强制安全边界。

规则答复期间候选不变；汇总确认加明确继续授权后才集中更新。完整用例评审、合并、
执行继续独立，不新设业务需求文档审批。模拟答复必须显式标注模拟。

共同交互来源与适配版本由 test-grill-me 单处维护；TCA 继续复用以上公开
记录入口，不引入另一个答案运行时。结构回归不能代替实际分轮对话。

## Review repair boundary

Repairs do not rewrite historical event payloads or confirmation hashes. Old tasks without new scope annotations keep their default blocking semantics. If an old disposition was misclassified, preserve the failed task and start an explicitly new synthetic validation task with source scope correctly declared; obtain fresh actual answers and version confirmation. This is a validation restart, not migration of prior approval.

## 本范围收尾

旧任务升级、具体稿保存后收尾、清理中断或局部变更时，执行 [范围收尾](scope-closure.md)。永久事件不删除；临时行只是同文件可丢弃投影。上游问答保留原路径与引用，不把跨Skill资料合并成新总账。

规则答复的 interpretation 表达实际规则/决定含义。复用来源与提问过程使用本 MD 的
既有 note/qa_ref；分级及风险依据按实际用途定位，具体写法与逐项来源核对见
[专业生成](professional-generation.md#规则解释与实际来源)。历史解释若只是过程，
用同 MD 的逐叶评估保存处置，保留原答复与身份，不修改历史事件或创建新答案台账。
