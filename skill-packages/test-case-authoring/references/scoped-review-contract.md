# Full-catalog selection and initial review baseline v1

Read this contract when selecting existing cases for a review batch. This is a
read-only authoring boundary, shared by later feedback and isolated merge work;
it does not create a second maintained business source.

## Supported input

`scripts/scoped_review.py` accepts UTF-8 JSON `authoring_full_catalog` v1:

```json
{
  "schema_version": 1,
  "kind": "authoring_full_catalog",
  "content_version": "synthetic-full-v1",
  "source_ref": "synthetic://example/full-catalog",
  "cases": [],
  "data": []
}
```

The empty arrays above only describe the envelope. A real input contains the
entire catalog, including unrelated cases, and uses the candidate case/data
records described in [the batch contract](batch-contract.md). Each existing
case has a unique stable `id` and complete `module_path` (at least the five
project/product/system/module/function levels). Keep original extra fields,
ordered steps, public and special preparation, special postconditions and
dependency records. `data_refs` resolve against the catalog data collection.
Unknown metadata and step extensions are retained, not discarded.
Both review views derive labelled business conditions from the same projection:
role/state, dependency purpose and required state, data values, business object,
validity, reuse and invalidation policy. Step extensions (including object
bindings) appear in the parameter/data area of both views, across all preparation,
feature and postcondition groups. Nested extensions become labelled leaves;
opaque JSON is not reviewer prose. Source ranges, provenance, internal IDs,
assertion operators and build hashes remain in candidate/baseline records.

Missing business fields become locatable `questions` with `待核对`; the source
record and its baseline remain unchanged. Absent role, initial state, expected
result or verification is not inferred. Missing identity/path or unresolved
data references prevent a meaningful copy and are rejected. Privacy review
and reference-only credentials remain mandatory.

This PR supports the explicit local JSON catalog boundary only. Native ui-test
Source Case/Test Data, Resolved IR/product-outline and arbitrary existing
Markdown are **not** automatically imported. Their formal reader and mapping
are pending the next PR. If the supplied full document has another format,
report the unsupported format and missing mapping rather than pretending a
single candidate file is a full catalog. A caller may supply a locally checked
snapshot in this contract, retaining its source reference/version; it is an
input snapshot, not authority to overwrite or maintain a parallel formal source.

## Request and public entry

```text
python -B scripts/scoped_review.py --catalog full.json --request scope.json --output-dir new-review-directory
```

`scope.json` uses these public `build_scoped_review` arguments:

```json
{
  "batch_id": "synthetic-review-1",
  "selection": [
    {"case_id":"EXAMPLE-1", "action":"reuse", "reason":"Required preparation"},
    {"case_id":"EXAMPLE-2", "action":"related", "reason":"Review downstream impact"}
  ],
  "approved_validation_scope": []
}
```

Select only `add`, `modify`, `reuse`, `deactivate` (suggestion) and `related`.
Each needs an explicit reason. `add` requires a new complete record in
`candidates`; `modify` requires a complete revised record in `candidates` plus
`basis` and `coverage_impact` on its selection. Other actions retain the full
original unchanged; supplying replacements for them is rejected. `candidate_data`
may provide new/revised authoritative data records by ID. Shared data changes
affect every selected consumer: an unchanged/reused/related consumer cannot be
silently modified. Identify and review that impact before regenerating.

`approved_validation_scope` contains only case IDs explicitly approved for
functional verification, independently of selection reasons. The default is
empty, including for new or modified cases. A related case may be in this list
only when separately approved; display alone never expands it. This entry
does not execute that scope or mark results passed.

## Output and handoff to feedback/merge work

The CLI writes a **new** directory with `candidate.json`, `xmind.md`,
`review-notes.md`, `changes.json` and
`initial-copy-baseline.json`. The Python API returns `batch`, `human_view`,
`xmind_markdown`, `review_notes`, `changes` without writes.

- `batch.kind=scoped_review_copy` and the Markdown heading identify a partial
  review copy. Both views use the same `content_version` and retain complete
  selected cases, paths and public preparation; special pre/post groups have
  the same step structure and appear only when supplied.
- `initial_copy_baseline.cases` and `.data` capture exactly the initial displayed
  candidates, including new and revised content. Later returned-file feedback
  compares against these fields, not the full catalog or a later regenerated
  projection. `.selection` retains initial reasons.
- `.catalog_cases` and `.catalog_data` hold the original selected existing records
  for old/new comparison; `.catalog_version`, `.catalog_digest`, `.source_ref`
  bind the read baseline. `.not_displayed_case_ids` identifies unrelated full
  catalog records whose absence is never a deletion.
- `changes` lists only actual differences, with JSON Pointer field paths,
  before/after presence and values, stable case/module identity, reason, basis
  and coverage impact. Ordered lists use numeric JSON Pointer segments.
  Data changes are associated with affected selected cases. New records and
  deactivation suggestions are selection actions, not fabricated field diffs.
- The full catalog is never changed. No returned-file edit, deactivation,
  final review, execution or merge is applied by this entry. Later feedback
  and merge implementations must reuse these baseline/identity fields and
  preserve unselected content. Formal synchronization remains pending.

Markdown structure verification does not prove XMind client import or return
compatibility. P1/P2 default presentation is the scoped Markdown and companion
notes; show a particular case's human-view when discussion requires it.
