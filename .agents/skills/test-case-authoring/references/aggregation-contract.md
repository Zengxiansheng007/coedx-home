# Aggregated review hierarchy

Read before generating a multi-case batch or scoped XMind review. Both public rendering entries share the same projection.

Directory identity is its complete semantic path and position. Preserve team, product, system, every module and function even when adjacent names match. Scope selection remains authoritative: unshown cases are not deleted.

Compare complete ordered preparation, role and initial context, dependencies, referenced data and business extensions. Provenance and generated local step identities do not change meaning. Only extract after source assessment and actual review establish that the vast majority of an existing business group require the preparation with very few exceptions (fall back to the original function only when no reasonable business group exists). Never invent a ratio or regroup cases to create reuse. Matching text alone is insufficient. Keep differences separate; preserve special preconditions, postconditions and all case actions/data/expectations. Public common definitions always belong directly to the module; the assessed business group appears in the definition. Cases show actual special operations only, with no common heading or repeated reference list. Unreviewed common actions remain explicitly pending and inspectable; they cannot become special actions merely to shorten the tree. Presentation reuse never permits skipping execution preparation.

Markdown and supported native XMind scalar feedback expand through the generated baseline's source bindings. A shared edit proposes changes for every applicable owner and enters the existing clarification/review flow. Structural or ambiguous changes require explicit interpretation; no candidate is silently modified. Generated applicability and paths are structural, not editable business scalars.

Before delivery check selected cases against source, semantic levels, preparation owners and special groups. Test the actual Markdown in the agreed XMind client and record version and visible hierarchy separately from static checks. Without that client evidence report import unverified. This does not execute business cases.

Retain answered question history without pending labels while answers remain valid; display unanswered and stale questions as pending. An empty list with an explicit no-preparation note is known absence; retain its conditions without an empty operation heading. An empty list without a note remains unknown. Empty special-operation nodes are omitted entirely.

## Source-assessed business groups

Before rendering, read the source and propose a business hierarchy for concrete review.
For announcements, put system announcement and home popup announcement in parallel,
with fields/rules/operations below each type only where cases exist. Put type switching
in a separate parallel group; retain each direction and independent scenario.
For orders, approvals or another business, use its actual permissions, states,
operations and domain relationships, not an announcement directory template.

The existing candidate may carry `business_group: {"path": ["采购订单", "权限"], "source": "source section or original Q&A decision locator"}` on each case.
This is assessed presentation metadata, not a separate grouping file, business
approval, or a new state machine. The source locator must identify actual inspected
evidence; a nonempty string check does not prove semantic correctness or user review.
Group labels are Chinese business names. Missing metadata preserves legacy layout;
empty or unsourced groups are rejected. No title classifier or automatic category
guessing runs. The renderer creates only groups owning selected cases.

Keep `module_path`, IDs, source traces, coverage, actions, data, order, expectations,
independent checks and endpoints unchanged. Group-only movement retains existing
semantic/data versions; rebuild the candidate via the existing scoped entry to bind
a new content/display version and baseline, then review the actual regenerated
hierarchy. Keep the full catalog and original source untouched. Scope omission
does not delete cases and never creates a module daily-view artifact.

Technical grouping evidence stays internal. Public titles remain `P0 中文名称`,
`P1 中文名称` or `P2 中文名称`. Existing digest-and-reply identity bindings support
case-title edits under grouped Markdown/native returns. Directory rename/move is
structural feedback: clarify the intended grouping against source and regenerate
a source-assessed candidate; do not infer identity from title/order or silently
apply the returned directory as a scalar edit. Real client import/edit/return and
the user's group review remain separate from parser tests.

## Reviewed preparation scope

Before generation, modification, restored work, or a shared definition change, reread
the full existing group and its source assessment. Present the proposed applicable
set, exceptions, conditions and real required frequency, then record the actual
review in the sole task Q&A. Never manufacture an approval from equal operations.

The public adapter in scripts/preparation_scope.py is
review_preparation_scope(batch, *, applicable_case_ids, exception_case_ids,
coverage, basis, actual_reply, version, frequency). It returns a copy with
preparation_scopes; coverage is vast_majority_few_exceptions only after qualitative
source assessment. The adapter checks complete group enumeration and equivalent
preparation semantics; it cannot establish truth of the supplied assessment or reply.
No percentage threshold is implemented. Scopes live in the existing candidate,
not a parallel registry or user-maintained file. Then use the existing scoped or
batch renderer and save its actual same-version output.

The rendered group names its scope version, business path, applicable cases,
exceptions and execution frequency. Bindings include preparation, context,
dependencies and referenced data, including long_term, time_limited and exclusive
conditions, validity and invalidation actions. Shared wording never means one-time
execution: preserve actual required checks, expiry renewal and independent data per
case. Authoring only records these obligations and does not prepare business data.

A new, moved, deleted or changed case, changed exception, or changed preparation
data invalidates old extraction. A partial selected group requires reliable full-scope context;
omission is not deletion and does not authorize a new applicability set. Restore
from candidate JSON and re-render to recheck bindings. To remove preparation or
change shared obligations, first show dependent cases and impact through existing
feedback proposals, clarify and review before applying. Shared scalar feedback
proposes all existing owners; structural removal must be interpreted in chat. After
accepted changes, reassess the complete applicability set and review the new scope.
Keep old evidence; do not edit stored bindings to pretend that old approval covers
the change. Unknown preparation remains pending; explicit no-preparation stays known.

The scope adapter also accepts optional `business_group_path`, an existing ancestor prefix. Enumerate every descendant member and exception while retaining each case's full child hierarchy. Ancestor membership and each full path are rebound on every render; newly added or moved descendants invalidate the old extraction. Default business assessment does not collapse existing groups. For a genuinely reviewed complete module authoring scope, pass scope_kind="module" with an empty business_group_path (or omit the path). Enumerate that complete source module, keep genuine child groups, and record the actual scope reply. A newly bounded authoring scope is not approval for an older full catalog or a concrete generated draft.

## Per-item common operations (contract version 2)

Supply `operation_id`, `step_ids_by_case` (applicable case ID to ordered source step IDs), and `direction="pre"` to `review_preparation_scope`. The existing `preparation_scopes` collection carries version 2 definitions; no registry or second business authority is introduced. Both direction="pre" and direction="post" use this same contract. Post definitions locate common_postconditions; pre definitions locate common_preconditions. Direction separates overlapping local step identities and binds its own notes. The original candidate steps remain the ordered definition source, including provenance, conditions, data references, expectations, assertions and endpoints. Stable source locators bind each definition to these complete steps.

Review applicability and exceptions separately for each operation. An exception to one item remains eligible for another; keep exception IDs only in the definition, never in each case. Source step order and distinct identities are required. Overlapping definitions for the same source step are rejected. Scope version, actual reply, source basis and frequency remain required, and equivalence still includes context and lifecycle semantics. Caller-supplied review text is evidence to check against the sole Q&A, not independent approval.

`operation_scopes(batch)` resolves current per-item memberships and local pending reasons. Stale or conflicting version 2 bindings block affected restoration; unrelated cases remain available. Unassigned preparation remains visible for clarification. Shared edits retain the original case/group/index mappings and propose changes only for applicable owners. Save and restore through the existing candidate and artifact writer; definition reuse does not change long-term validity, expiry renewal or per-case acquisition.

Historical whole-list scope records and exported layouts remain readable against their original baseline. New deliveries use module-direct definitions. Preserve old files; the legacy feedback interpretation is not a migration or permission to overwrite newer decisions.

## Common postconditions

Supply common_postconditions only for actual sourced follow-up obligations; absent legacy fields remain absent. The source sequence is common pre, special pre, business steps, special post, common post. Retain each original group order, condition, data reference, assertion and endpoint. If the source needs another interleaving, clarify before grouping it; a shared definition does not authorize execution. Empty special post groups are omitted. A missing post group produces neither cleanup nor a pending cleanup placeholder.

For example, a simulated loan group can share opening the loan page before its test and returning the borrowed item afterward, while the history-only exception inherits neither loan obligation. One case may additionally inspect its individual receipt under special postconditions. Review pre and post separately using operation_id, direction, ordered step_ids_by_case and the same reviewed applicability/exceptions; render both definitions directly under the module. Keep whole-list notes visible as unresolved when their assignment to an individual definition is unknown.

## Local scope lifecycle

Version 2 identity includes the module, actual business path, direction and operation ID. The same operation ID in two existing business groups cannot replace the other group. Re-review preserves an existing matching older identity. New, moved, removed or edited members are checked per member and item; referenced data changes affect only definitions using that data. Contradictory membership or competing source slots withhold those memberships. Unaffected definitions and cases remain visible. Pending source operations are displayed for review, never copied into special operations or declared restored. Restoration reports the case incomplete until its affected obligation is re-reviewed.

A selected copy retains its existing initial_copy_baseline parent source reference, version, digest and omitted IDs. Supply the exact complete source_catalog to render_review_batch, write_artifacts and preflight for a partial copy. Missing or changed parent identity/version keeps its inherited common items pending; unrelated cases continue. No snapshot is a second applicability authority. Start a new selection from the current complete parent after changes, then review only changed memberships; preserve old copies and review evidence. A selected subset cannot author a new parent applicability set. Full selection can recheck its complete current local candidate.

## 完整新作者范围与本例特殊归属

实际任务通过 [同一 QA 事件](qa-record-contract.md) 的 `review_preparation_scope` 动作保存以下参数，
不直接修 candidate 的内部 scope 记录。公共打开和本例准备可分别评估：

```python
# 例：本轮完整新增 12 条作者稿；parent 是准确完整的原 P0 来源。
common_review = dict(
    operation_id='打开空列表', direction='pre', scope_kind='module',
    step_ids_by_case=actual_open_step_ids_by_case,
    applicable_case_ids=all_current_new_case_ids, exception_case_ids=[],
    coverage='vast_majority_few_exceptions', basis=actual_inspected_source,
    actual_reply=actual_review_reply, version=actual_scope_version,
    frequency='每例独立打开并核对空列表', source_catalog=parent,
)
# 单例 seed 等步骤仍保留在原 common_preconditions，明确评估后只改变展示职责。
special_review = dict(
    operation_id='本例准备', direction='pre', scope_kind='case',
    step_ids_by_case={case_id: actual_ordered_seed_step_ids},
    applicable_case_ids=[case_id], exception_case_ids=[], coverage='case_specific',
    basis=actual_case_goal_and_source, actual_reply=actual_attribution_reply,
    version=actual_scope_version, frequency=actual_per_case_frequency,
    source_catalog=parent,
)
```

完整新增作者范围须来自真实 extension 入口，准确父源版本/摘要匹配，当前身份与初始完整新稿身份一致，
selection 全为 add 且不与父源身份重叠，初始 catalog_cases 为空；not_displayed_case_ids 必须恰好
来自同一父源，不能混入未展示的新作者成员。缺少/漂移父源、夹入既有成员或漏新成员仍拒。
scope 的既有记录内保存本轮作者集合与父集合界限；父 P0 只作来源核验，不列为不适用例外，
也不扩大本轮实际功能批准范围。普通 partial 不能借 extension 标记重新审批父范围。

本例归属只接受一个明确 owner、已存在的有序原步骤、真实依据/答复/版本/频次。
direction='post' 使用原 common_postconditions 的相同契约。公共项与特殊项冲突时拒绝；
公共排除不自动生成特殊项。没有评估的剩余步骤/说明继续待核；没有实际后置就不发明清理。
原步骤、下标、来源与数据保持，XMind 和对话均显示同一特殊分支，反馈准确回到原 common 路径。
来源/条件/数据漂移按受影响成员和项失效；无关来源或另一例的有效归属不重开。

来源等价比较按已声明的 claim/step/data 类型区分定位信息与真实业务语义，不能把
data.value 中同名 source_ref 等实际字段当定位删除。步骤原文、生命周期、角色差异、例外及
独立预期仍参与完整比较。执行频次以真实已评审条件为准，定义只显示一次不减少实际准备次数。
