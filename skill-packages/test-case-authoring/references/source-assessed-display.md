# Source-assessed display partition

Before first generation, revising an existing draft, feedback, recovery or shared-definition updates, assess each statement by its actual role against the current source. Use `scripts/review_projection.py` after constructing the existing candidate; do not rewrite source cases or data to make a shorter display. This optional candidate metadata is neither a new required packet nor business approval.

`assess_review_projection(batch, source_version=batch['content_version'], basis=source_locator_and_reason, assessments=[...])` returns a copy. Each assessment supplies `collection` (`cases`, `data` or `selection`), `id`, a `path` of known dictionary keys and nonnegative integer list indexes to one scalar leaf, `rationale`, and `disposition`. For example, `['steps', 0, 'expected', 0, 'text']` locates the first expected claim; bool, negative, missing and out-of-range indexes are rejected. Optional `source_catalog` is checked against the exact complete parent:

- `technical`: general governance or technical locating information; keep the original in the candidate and place it in the existing module Agent explanation with owner/field applicability.
- `duplicate`: source review established the same meaning already in an explicitly retained `equivalent_to` path in that owner. Assess all object, role, condition, trigger, timing and result distinctions before choosing it. A graded visible title based on the original priority can support omitting a repeated priority leaf; the visible graded case title still comes from the original priority.
- `readable`: use explicit `text` to express a known status or value in readable language. For example, rule `formal` means the rule is confirmed, never that a pending draft passed review. Preserve the distinction in the wording.

Do not classify by field name or a phrase blacklist. A `validity` object can contain both a general instruction to recheck source and a real deadline: assess only the former leaf, keeping the latter in the case. Every-case isolation, required role, initial state, actual expiry, invalidation outcomes, conditions, independent results and unknown values remain visible. Do not collapse complete dictionaries or arrays, or move a necessary operation into technical notes. Unknown equivalence stays uncompressed and returns to clarification when material.

评估绑定原始来源版本、实际业务 owner 和可识别的使用来源注册。用例的已知评审控制字段（review_status、final_review、review_history、merge_status、execution_status）单独保存，不使业务未变的显示评估失效；语义/数据版本、真实条件、步骤、数据引用及规则决定仍参与 owner 绑定。真实 owner 或使用来源漂移后恢复原文并重新评估。无关且未使用的来源注册不重开当前明确评估；每个 typed 来源都独立匹配；明确的 ref/path 片段定位（如材料#章节）绑定其注册材料，不能因另一个 kind 已匹配而漏掉它。结构体或其他未分辨引用保守绑定全部注册；明确未使用的注册仍不使局部评估失效。实际 value/input/inputs/output/outputs 中的同名 source_ref 不成为框架来源。永久问答及原始 case/data 保留，显示评估不授予业务确认、执行或合并。

实际任务用 [唯一 QA 公开入口](qa-record-contract.md) 的同名动作保存并回放评估；只调用纯函数后写 candidate，尚不能通过 checkpoint。不要放松候选与 QA 回放的完整相等核验。必要的 selection 动作/理由可按真实来源逐叶评估；真实业务字段（如 user_rule）未知时仍保留，不能按名称当作审计回执删除。

After rendering, inspect actual business prose and Agent notes, including titles, data constraints, preparation, all operations and independent results. Merely retaining JSON fields or reducing topic count is not compression acceptance. Save a new candidate/version and verify readback; do not overwrite historical review or native-client failure baselines. Test source-drift fallback and feedback on a retained visible leaf. Actual client and business acceptance remain separate.

Duplicate retention is checked against the complete proposed assessment set through both actual business renderings. The equivalent target must be a scalar leaf with a visible expression after projection (including generated graded titles and explicit readable wording). A source-only field, technical-note-only target, disappearing self-reference or cycle is insufficient. Invisible duplicate chains are conservatively rejected even when a later endpoint survives: point each duplicate directly at that visible endpoint. This checks expression retention, not natural-language equivalence; the author still reviews semantic sameness against the current source. Unchanged original owner/source bindings continue to govern drift fallback.

For TAS-12 assessment, identify the exact same-owner retained path in each duplicate decision, then inspect its visible title/body expression in both exported views. If only a technical note or JSON value remains, retain the original business leaf or revise the assessment. Record real source-based rationale; synthetic test rationales are not real approval, and pending draft identity remains pending.

## Technical-note grouping

Within each case, group technical leaves only when the complete key path and original scalar text match (ignore leading/trailing whitespace only). Compare before rendering; keep interior whitespace, conditions, exceptions and differing paths distinct. Generated notes escape backslash, newline, carriage return and tab reversibly; spaces remain unchanged. Paths use JSON Pointer escaping for slash and tilde. The original candidate remains authoritative.

Display data owners by their object_ref name with collection-scoped identity; unnamed objects remain explicitly unnamed rather than borrowing the case title. Label validity as 有效性, reuse_policy as 复用条件, and invalidation_action as 失效后的处理, and label priority_basis as 优先级依据, maintenance_action as 维护动作, action as 变更动作, and reason as 变更原因, retaining the full original path beside the label; unknown field names remain visible. Keep object order stable. A known object occurs once per matching rule; distinct IDs remain distinguishable even with identical names. Missing or duplicate owner identity retains each occurrence with 身份歧义 and a stable position for review. Never merge across cases or change source/version/review bindings. Later scoped delivery updates the existing case section and preserves unselected sections.

## 有效规则解释的同源投影

规则解释、已答子项、暂定预期、产品核对和范围差异沿同一逐叶评估进入正文。
显式 technical/duplicate 的有效解释只从当前投影省略，不能再用原 actual_reply 回退，
也不生成“规则内容待核对”占位；真正缺失或未知解释继续待核，未评估业务规则完整保留。
历史决定按原身份选择有效项，解释用其对应投影；技术叶在现有模块说明按原路径定位，
原始整轮答复继续引用同一 QA，不为修复复制到 Agent 说明。
