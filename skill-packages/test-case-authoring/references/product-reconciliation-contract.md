# Product final confirmation and historical results

Read this when product confirms or changes a previously provisional rule. Inspect
the actual product message, the provisional decision, complete cases, manual-check
coverage, report contents and necessary evidence before interpreting the relation.
The agent determines whether the business meaning is consistent or changed; a
helper's accepted JSON cannot establish that interpretation.

Use stable `rule_refs: [rule_id]` on cases, coverage rows or individual manual
checks. Coverage rows retain the existing `links: [{case_id, aspects}]` contract;
legacy companion rows may use `case_ids`. Follow all links and inspect their
completeness. Missing or ambiguous mappings stay pending source inspection.
Do not invent a mapping from a similar title. Keep unrelated cases unchanged.

Public Python boundary (no filesystem, execution or formal asset writes):

```python
from p0_evidence import approve_result_scope
from product_reconciliation import reconcile_product, decide_reuse, prepare_product_change
baseline = approve_result_scope(catalog, round_id, case_ids, actual_scope_reply)
result = reconcile_product(catalog, baseline, reports, conclusion, mode='simulation')
```

The baseline freezes the supplied catalog cases and business data for subsequent
applicability checks. Prefer the original historical baseline. A new baseline
requires inspecting the historical case/data records, not reconstructing them
from today's assumptions. Existing P0 validation baselines remain supported.
`approve_result_scope` accepts P0/P1/P2; it grants no testing or P1/P2 entry.

`conclusion` contains `rule_id`, `relation` (`consistent` or `changed`),
`actual_reply`, `source_ref`, and the intended `tested_version`. Preserve actual
wording and provenance. Reports follow the P0 evidence contract's identity,
round, module, semantic/data version, tested version, functional purpose,
result, evidence content/digest and source fields. Generic P0/P1/P2 reports use
`kind: case_execution_report`; original P0 reports retain their existing kind.
Use `simulation` only for explicitly labeled samples. Production rejects sample
provenance. Unknown real report formats require mapping and source inspection;
formal ui-test adapter and real joint acceptance remain a later PR dependency.

For **consistent** meaning, show each affected case's content/data versions,
tested version, report/evidence references, retained provisional conditions and
either a reuse suggestion or the specific missing applicability proof. A matched
pass suggests reuse; absent, failed, unexecuted, stale, ambiguous or incomplete
evidence remains `pending_check`. Present the choice to reuse or decline with a
recommendation and reason. Record only explicit answers using `decide_reuse` with
`reconciliation_id`, selected `case_ids`, boolean `reuse`, and `actual_reply`.
Unanswered cases stay awaiting the user. A reuse decision is separately retained;
it does not create a new execution pass or change the old rule status.

For **changed** meaning, show affected case IDs/module paths and coverage links,
actual before/after fields and suggested changes. `pending_retest` names the
downstream scope immediately; it is not an execution request. Use
`prepare_product_change(catalog, result, changes)` then the existing feedback
contract's `respond`, `summarize`, `apply_feedback`, and `review_feedback` gates.
Ask all eligible independent questions in chat, preserve partial/unanswered
records, obtain exact-summary agreement, update the common version once, regenerate
both review views, and submit complete changed cases for exact-version final
review. Regenerate the existing extension design coverage from the revised common
content with `render_extension` when extension design is present; coverage design
and historical execution results remain distinct. Keep unresolved affected cases
pending. Shared data changes are allowed only when every consumer belongs to the
identified affected scope; inspect additional consumers before expanding scope.

The resulting candidate retains a `product_reconciliation` reference and
`downstream_retest_pending_not_executed` marker. Present the retained retest scope
after review and recommend separately user-started ui-test. This skill neither
retests nor clears that marker based on a content review.

Done means the formal product conclusion, applicability check and actual reuse
decisions or changed-content review and pending retest scope are traceable.
`historical_results` preserves the supplied reports and frozen baseline with the
original provisional conditions. Keep this reconciliation alongside the originals;
never backdate a historical result into formal confirmation. No result here means
formal source synchronization, merge or execution has occurred.
