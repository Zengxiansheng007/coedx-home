# Public recording batch contract v1

`scripts/authoring.py` is a deterministic converter, not a JavaScript parser or
business analyst. The skill reads the source and supplies its interpretation.
The converter validates source ranges, line coverage and data references;
semantic correctness of the translation requires the skill's final comparison.
No dependency other than Python 3.10+ is needed.

The input object contains:

| Field | Meaning |
| --- | --- |
| `batch_id`, `case_id`, `title` | Nonempty stable identities and business title |
| `module_path` | Five strings: project group, product, system, module, function |
| `context` | `role` and `initial_state`, each an array of claims; empty means missing |
| `data` | Records with unique `id`, `value` or `credential_ref`, and provenance |
| `steps` | Nonempty ordered complete business steps |
| `common_preconditions` | Ordered preparation steps; empty only when none is supplied |
| `recording_coverage` | Ranges and business/technical accounting reasons for every nonblank line |

A claim is `{"text":"business statement","source":"recording","lines":[2,3]}`.
Sources are `recording`, `prd` (only when supplied), or `inference` (no source
range required). A step has `operation`, `data_refs`, `source`, `lines`,
`expected` (claims), and `verification` (claims). Multiple conflicting values
for one field remain alongside each other and trigger an unresolved question.
Equivalent differently worded statements may conservatively need clarification.
Coverage entries have `lines` and `reason`; line coverage verifies accounting,
not whether the agent interpreted the lines correctly.

Example (synthetic):

```json
{
  "batch_id": "demo", "case_id": "DEMO-P0-001", "title": "Save draft",
  "module_path": ["Example", "Workspace", "Web", "Notes", "Save"],
  "context": {"role": [], "initial_state": []},
  "data": [{"id":"title","value":"Example title","source":"recording","lines":[1,1]}],
  "common_preconditions": [],
  "steps": [{
    "operation":"Enter the title", "data_refs":["title"],
    "source":"recording", "lines":[1,1],
    "expected":[], "verification":[]
  }],
  "recording_coverage":[{"lines":[1,1],"reason":"title entry"}]
}
```

Data records may retain `object_ref`, `validity`, `reuse_policy`,
`invalidation_action` and their evidence as additional candidate fields. Absence
is unresolved, not a default business policy. Never put credentials in `value`,
operations, titles, PRD or notes. Use `credential_ref` exclusively for references.
The credential guard rejects recognizable literals; it does not certify all
text as safe. Error messages deliberately omit source text and values.

The result contains one versioned batch with source SHA256 references, coverage,
cases, separate authoritative data, questions and independent rule/review/merge/
execution states. `content_version` hashes the content and `data_version` hashes
the data; both views share the content version. No current final approval or
execution evidence is synthesized. The initial copy baseline is null and the
approved validation scope is empty.

Each case also carries a semantic version and a link to the data version. Steps
receive internal identities on initial conversion; callers can retain supplied
step IDs during later updates. These identities stay out of business columns.
Missing data association, validity, reuse or invalidation conditions produce
locatable questions; they are not filled with implicit execution policies.

Human-view uses four columns; hierarchy uses project/product/system/module/
function, public preparation and case steps. Each step has exactly one
`参数/数据` child and a sibling `预期`, including its observable verification
point. Missing expectations render as `待澄清`. Source records retain basis
(`recording_observation`, `material_statement`, `ai_inference`) and positions.
Technical hashes and internal assertion syntax stay outside business columns.
Special pre/postconditions and cross-module references are reserved for later
extensions, rather than silently synthesized here.

For multi-case clarification, versioned rule decisions, confirmed updates and
independent final review, continue with [the clarification contract](clarification-contract.md).
The recording converter's single-scenario boundary does not restrict the batch
clarification API to one case. Candidate cases keep stable identities and data
references when collected into a review batch.

Run synthetic behavioral checks:

```text
python -B -m unittest discover -s scripts -p test_authoring.py -v
```
