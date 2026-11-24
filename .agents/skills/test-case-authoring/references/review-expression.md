# Review expectation expression

Before generation, compare each expected result and verification point against
the source. If they express the same observation, author the same precise wording
while retaining both internal fields and source links. This is an Agent semantic
decision, not a string similarity score. Unknown equivalence stays visible and
returns to existing clarification. Do not invent a new approval workflow.

For example, synthetic “保存成功” and “保存操作成功” may describe the same
observed result after source review; use “保存成功” in both internal claims.
“列表显示本次记录且状态正确” adds a location, object and result: keep it as
an independent verification. Never remove it because saving also succeeded.
Compare object, condition, action, observation timing and result before normalizing
synonyms. Record the source basis in the existing candidate claim or original Q&A;
do not create a second semantic ledger. The renderer compares complete projected
claims, not individual text fragments. Different observation timing, roles, states,
bindings and endpoints remain independent even when their result wording matches.
Internal assertions remain available for handoff. Unknown equivalence stays visible.

A simple record with an explicit object_ref and one scalar value is shown as
“对象名：值” on the parameter/data node. Identity, original machine keys,
data_refs and raw values stay in the candidate unchanged. A value without an
object name keeps its labelled scalar form. Explicit validity, reuse and invalidation
conditions remain separate leaves after the named scalar expression. Other complex
business conditions, generation rules or independent results keep the full labelled structure. Multiple
values, generation rules and meaningful limits keep individually labelled leaves;
conditional branches remain explicit. This is a layout projection, not permission
to delete unfamiliar data fields. Preserve literal values including action-like
words. Operations belong in steps, values and generation rules in data, outcomes
in expectations; verification adds only independent checks.

Apply this same source review before initial generation, feedback changes, recovery
and shared-definition updates. All use the existing public renderer. Markdown and
native feedback preserve hidden assertion identities; changing a visible result
does not silently rewrite its hidden assertion. Clarify that change explicitly.

Synthetic source-reviewed examples (not product decisions):

| Source distinction | Candidate and visible result |
| --- | --- |
| Same notice, same save, same time: “保存成功” / “保存操作成功” | Normalize both claims to “保存成功”; display once; retain both sources |
| Title blur prompt / save prompt | Keep separate operations and each prompt at its own observation time |
| Save prompt / no created notice | Keep both independent results |
| Approver changes the same pending order to approved / approved synonym | Normalize only the evidenced synonym; retain approver, pending state and same-order binding |
| Approval complete / notification delivered, equivalence unknown | Preserve both; ask about the unresolved result without inferring delivery |

Total, scoped and requested chat views use `P0 中文用例名` (likewise P1/P2),
without changing priority or storing the prefix in the business title. Rename
feedback binds the existing stable identity and version, never node order.
Unchanged returns preserve duplicate internal assertions; editing a hidden
assertion requires explicit chat interpretation. Chat remains 1–9 requested cases,
same-version and without a human-view file. Actual client acceptance is separate.

For explicit, version-bound semantic partition of existing metadata and repeated governance, follow [source-assessed display](source-assessed-display.md). Original case/data values remain authoritative; no field-name deletion policy applies.

Synthetic data examples: `object_ref: 入口地址` plus `value: config://portal:8443/path`
displays `入口地址：config://portal:8443/path`. An order record with generation
conditions for approver and pending state retains those separate labelled leaves.
The projection does not merge two data identities or strip unknown fields.

## 实际值与可见空格

首尾有普通空格的字符串用闭合引号保留原始空格并显示中文计数，例如：
`待办文字：“   Todo with spaces   ”（前导空格：3；尾随空格：3）`。
控制字符和反斜线只在此明确表示内可逆转义，普通字符串沿原文显示。
实际值恰好撞完整保留表示时再包一层；显示不会修改 data.value、id 或 data_refs。
回传编辑时计数须与引号内实际空格一致；矛盾或不明确的表示保持拒绝，
旧稿按其原布局读取。不得把引号、计数或可见提示字符写入实际值。

data.value 及实际输入/产出子树使用字面业务语义。其 source、source_ref、id、text、
lines、case_ids、final_review、user_rule 等合法键不解释成来源或用例关系，
也不移到 Agent 审计说明；来源核验只用于已声明的 claim、step、data 根。
凭据保护仍检查全树，字面值角色不提供凭据豁免。
