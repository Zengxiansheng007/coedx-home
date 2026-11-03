# P0 evidence and extension entry v1

Read this before responding to a request to enter P1/P2, or when new P0 reports
or suspected missing core cases arrive. This is read-only authoring work. It
neither executes tests nor merges P0. Formal ui-test report mapping and the
cross-skill production chain remain pending joint validation.

## Bind the whole approved round

Use the same `authoring_full_catalog` v1 as
[scoped review](scoped-review-contract.md). Read the user's actual functional
validation approval and identify every approved P0, including other modules
that are functional targets. Preparation-only references do not become targets;
existing data does not remove an approved functional target. Display selection
and partial merge selection cannot replace this whole-round scope.

```python
from p0_evidence import approve_p0_scope, check_extension
baseline = approve_p0_scope(catalog, round_id, case_ids, actual_reply)
result = check_extension(catalog, baseline, reports, request)  # production default
```

`approve_p0_scope` freezes the source reference, catalog version/digest, explicit
approval text, complete scoped case records, referenced data and required checks.
Keep this `p0_validation_baseline` unchanged. Its `id` binds the approval. Required
checks are each supplied verification claim under every public/special pre/post
and feature operation, keyed as `steps/0/verification/0`, for example. These keys
are local evidence identities, not executable assertions. Every operation must
already have expected results and verification. The baseline is a snapshot, not
a second maintained formal source. Changes to P0 require the P0 clarification,
review and downstream validation/merge path plus a new explicit scope baseline.

## Read reports and necessary evidence

Read the actual supplied reports and the contents of every necessary attachment.
Inspect whether each attachment supports its stated check, object and tested
version. Reject a filename, same title, screenshot existence, oral pass summary
or old data as sufficient proof. If no formal adapter exists, normalize the
read contents into this envelope while retaining original report references;
state unsupported formats or missing mappings rather than fabricating success.
The helper checks identity/version/digest and completeness. It cannot authenticate
the producer or judge whether arbitrary prose proves a business check; that
semantic judgment belongs to the agent reading the original evidence.

Each item in the `reports` list has:

- `kind: p0_execution_report`, `synthetic: false` for actual evidence;
- `report_ref`, `round_id`, stable `case_id` and full `module_path`;
- `semantic_version`, `data_version`, and actual `tested_version`;
- `purpose: functional_validation` and `result: passed | failed | not_run`;
- `evidence`: objects with `check_id`, original `ref`, read UTF-8 `content`
  (sanitized attachment text/observations), and its UTF-8 `sha256`.

Keep original raw material outside the public repository. Reference credentials
only. For binary evidence, the agent must inspect the original and provide a
source-traced description in `content`; a hash alone proves no business result.
Missing or multiple ambiguous reports, wrong round/module/version, changed
business content/data, preparation reuse, absent check contents and digest
mismatch produce `pending_check`. Matching failures and explicit not-run results
remain `failed` and `not_run`; complete matching evidence produces `passed`.
No input case's stored execution state is rewritten.

## Independent user decisions and gap review

`request.tested_version` names the version whose reports were requested.
`manual_start` contains `baseline_id` and the user's actual request in
`actual_reply`. Passing reports alone never starts extension.
If any case is provisional, also require `provisional_continue` with
`baseline_id`, `continue: true` and the actual reply. Ask specifically about
continuing under the listed product-verification conditions. Manual start,
provisional continuation and pass evidence are distinct facts. Reuse a clear
message that explicitly supplies both actions; silence supplies neither.

After the whole P0 passes, actively compare its business coverage against the
mandatory human test points and available PRD, UI and supplementary materials.
Propose suspected missing P0 paths yourself, citing concrete source positions
and the current coverage gap. Do not ask the user to discover the missing cases.
Use the [batch clarification workflow](clarification-contract.md): present all
independent questions together with options, recommendation, reasons, example
and affected scope; dependent questions wait for their premises. Keep actual
answers, histories and provisional conditions. Rule decisions do not replace
complete final review.

Record `gap_review` with `completed: true`, nonempty source `basis` references
and a concrete `summary`, even when no suspected gaps are found. Each `gaps`
item has unique `id`, `proposal`, source `basis`, and optional `decision` with
actual user reply and `route`:

- `supplement_p0`: return to clarify, complete review, user-started ui-test
  formal script validation and user-started downstream merge. Block extension
  until the updated whole scope is verified; this helper performs none of it.
- `extension`: carry the suggestion into P1/P2 authoring and priority review.
- `exclude`: retain the user's exclusion and its basis; do not silently delete it.

Undecided suggestions block extension. Produce a compact per-case table with
identity/path, priority, rules, review, merge, execution, version and report basis.
Preserve provisional conditions; partial merge may change merge metadata but
cannot shrink this table. `can_extend` means only that the authoring entry
conditions are met. It grants no execution, merge or production integration.

## Public file entry and isolated tests

```text
python -B scripts/p0_evidence.py --catalog full.json --request approval.json --output-dir new-baseline
python -B scripts/p0_evidence.py --catalog full.json --baseline baseline.json --reports reports.json --request extension.json --output-dir new-check
```

The first request uses `round_id`, `case_ids`, `actual_reply`. The second uses
the request above. Each writes a new directory only, containing respectively
`p0-validation-baseline.json` or `extension-check.json`. Sources are unchanged.
Use `--mode simulation` only for explicitly isolated synthetic development
fixtures. Mark synthetic reports `synthetic: true`, inputs and natural-language
replies as simulated, and output as `evidence_nature: simulated`. Production
refuses synthetic/unspecified report nature and synthetic provenance even when
relabelled. Simulation never opens a real P0 entry gate or counts toward actual
execution or joint acceptance.
