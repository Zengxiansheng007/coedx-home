# 同一任务的问答记录

开始业务规则提问前，读取本任务已有问答 MD、当前候选和相关源文件。
首次任务固定一个获授权的问答路径。报告选择、规则、评审回问及后续阶段
继续使用它；阶段变化追加章节，不能另起一份答案。此处提供规则入口的
最小记录契约，报告核对与覆盖的业务判断仍遵从各自契约。

## 对话与实际决定

完整问题必须包含稳定编号、适用用例/字段/检查、证据定位、中文选项、
允许自定义答复、推荐、当前理由、主要代价/边界和具体例子。用正常中文
正文全文展示，不能只发路径或问题卡。真实来源与假设分开标识；无证据
时说明缺口，不能给未知规则填推荐答案。保留原问题编号和证据。

收到真实答复后逐项核对对象、行为和条件，再记录原话、对话来源与归纳。
“不知道”不等于搁置或暂定，先保留原话并继续问处置；未取得明确决定前
先用 record_note 保存并回读原话，再调用 respond 记录 partial 或 unknown；
两者都保持问题未决，返回完整追问必须在正常对话实际发送并等待答复。
不得改写既有事件块。仅记录未知而没有实际追问不算完成。

- formal：实际明确确认的规则，记录确认者来源，不冒充产品确认。
- provisional：明确授权的暂定预期 authorized_expectation，以及待产品
  核对的 product_check；只有“先继续”而无预期和条件时继续澄清。
- deferred：实际明确搁置，记录影响范围，不写候选更新。

## 持久化公开入口

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
# 以中文展示 summary 中实际决定、拟更新、暂定条件及阻塞范围，等待汇总确认。
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

规则答复期间候选不变；汇总确认后才集中更新。完整用例评审、合并、
执行继续独立，不新设业务需求文档审批。模拟答复必须显式标注模拟。

复用来源：grill-with-docs 的完整提问及记录顺序、coverage 扩展 1.0.0 的
来源核对义务、test-point-discovery 的中文对话与单一问答记录设计；不引入
grill-system 的单题和独立 JSON 答案运行时。结构回归不能代替实际分轮对话。
