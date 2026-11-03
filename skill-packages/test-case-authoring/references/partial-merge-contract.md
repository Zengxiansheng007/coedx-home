# Isolated partial merge

This branch applies approved P1/P2 business deltas to a synthetic or authorized
isolated `authoring_full_catalog` v1. It does not adapt formal ui-test assets.
Use complete catalog records and the original `initial_copy_baseline` from scoped
review; the latest candidate may include accepted feedback. Keep input files
unchanged and write a NEW output directory.

Public Python entry:

```python
merge_reviewed(catalog, batch, instruction, target_kind='isolated')
```

CLI (paths refer to authorized isolated files):

```text
python -B scripts/partial_merge.py --catalog full.json --batch reviewed.json --instruction merge.json --target-kind isolated --output-dir new-merge-result
```

`instruction` contains `kind: merge_instruction`, the user's `actual_reply`,
`content_version` of the latest reviewed batch, `baseline_version` of the original
catalog and explicit unique `case_ids`. Each applied case needs current-version
final approval from the common clarification/feedback workflow, formal or
explicitly provisional rules, complete business content and complete dependencies.
Use candidate APIs for changes; changing content directly while retaining an old
version or final approval violates this contract. Simulated replies stay labelled.

Actions come from the scoped selection. Accepted feedback can promote a reused
or related existing record to a modification; unrelated display grants no change
permission. Changes require the user's merge scope and current final approval.
P0 always remains pending for ui-test. Deferred, excluded, missing, cyclic,
unapproved or deactivated prerequisites block their dependents. Complete
preparation references and data policies are rechecked with the dependency
contract, including exclusive/expiry decisions. Preparation reuse never claims
functional execution or reduces the independently approved P0 validation scope.
These checks cover every necessary owner/edge in the dependency closure, using
the actual target plus only the approved deltas that remain eligible to apply.
The same delta projection supplies dependency checks and the returned full
catalog: candidate data outside those writes cannot satisfy a prerequisite.
When a delta becomes pending, its content and data are removed from the effective
target and affected dependents are checked again. A final approval on a
root case cannot fill missing descendant decisions. Existing prerequisites are
read and checked without expanding merge scope or rewriting their records.

Only authorized deltas are applied to the complete target. Changed shared data
is blocked if it would alter any unapproved, pending or retained original case;
use a separately reviewed data identity or explicitly review all affected owners.
Target case/data drift stops affected writes. Unrelated drift is retained; unknown
data baseline after drift stops affected writes for reconciliation. This is not
automatic concurrency recovery. Deactivation retains the complete original and
user reason in `deactivation_history`; no record is deleted.

The pure return and `merge-result.json` expose the new `catalog`, per-case
`applied` or `pending` and reason, target `content_version`, original approved
validation scope, `formal_sync: pending_joint_validation`,
`execution: not_started`, and `evidence_kind: isolated_authoring_result`.
`catalog.json` is the same full isolated result. A successful CLI can contain
pending cases: inspect each row. Only applied P1/P2 changes justify recommending
user-started ui-test. Formal source/data synchronization, automated readiness and
execution remain separate downstream work. No execution handoff list is created.
