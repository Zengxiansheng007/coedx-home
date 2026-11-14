# P0 whole-step reference contract

At P1/P2 authoring, first write the complete target sequence from supplied source
materials. Independently compare each proposed P0 step for operation, fixed-data
business conditions, expected results and verification. Explain applicability to
the current role/state and identify the target's final assertion. A matching
string or an `equal=true` flag is not a semantic judgment.

Pass those judgments in each candidate's `reuse_assessments`: `group`, `step_id`,
`p0_case_id`, `p0_step_id`, `applicability`, `endpoint`, `source_basis`, and a
`comparison` object with concrete explanations for `operation`, `data`,
`expected`, `verification`. `build_extension` still accepts complete target
steps and still enforces the P0 entry gate. No assessment means independent
complete authoring. Any detected business difference keeps the entire step
inline; partial inheritance and reference-plus-overrides are rejected.

The fixed-data implementation conservatively requires identical data bindings
and all business conditions. Different identifiers remain independent even if
their values happen to match. Dynamic generation and value rebinding are outside
this static contract. Source addresses and assertion IDs alone do not establish
business equivalence. The deterministic comparison is a consistency check of
the agent's source-based decision, not natural-language semantic reasoning.

The candidate stores `id + step_reference` exclusively. The reference binds P0
identity, group, step identity, semantic version, definition digest, data and
context. Batch `step_definitions` contains version-pinned technical dependencies,
including fixed data and the original Chinese title/step number. These are
immutable recovery snapshots, not independently editable business definitions.
The initial display baseline binds the same dependencies. Scope copies and
isolated catalog merges retain the required dependency closure.

Review displays the operation and `P0 中文名，步骤 N`. The internal `expanded`
projection reconstructs the declared target sequence only. Its business digest
must match the complete authored target, including order and final assertion.
Rendering, coverage, clarification, final review and isolated merge recheck the
same definitions. A missing, changed, inapplicable or overridden reference raises
a path-specific error; return to existing clarification/source correction.
Never guess missing content or call that candidate review-ready or handoff-ready.

Returned unchanged Markdown uses the same baseline. Reference labels and
definition identities are derived fields, not editable scalar bindings. An edit
to inherited content enters the existing clarification and summary gate. Chat
may address resolved business leaves; Markdown/native returns may edit the
displayed action. After agreement the changed step becomes complete local
content, using current-case data bindings. Other steps, P0 snapshots and other
cases remain unchanged. Outer action whitespace is formatting only and keeps
the reference. Other ambiguous equivalence claims require clarification.
Explicit requests to change P0 require shared-impact review; do not reinterpret
them as permission to alter a dependency snapshot. Shared updates are separate.

Do not append P0's remaining success path to a negative scenario. Definition
reuse neither executes P0 nor carries its historic pass result. Existing complete
independent upstream/downstream case requirements remain unchanged. No extra
human-maintained expanded draft or human-view file is created; actual downstream
and XMind-client support still requires separate qualification.
