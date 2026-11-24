# P0 whole-step reference contract

## Explicit shared-source changes

Use `prepare_feedback(..., shared_change=...)` only for an actual request to change P0.
Supply `explicit_request`, exact `definition_digest`, a complete versioned
`replacement` definition, and `assessments` for each actual referencing case.
Each assessment contains `case_id`, `disposition` (`reference` or `independent`),
and a concrete `reason`. Independent keeps the old complete step; further changes
to that case use normal local feedback. The existing questions, summary agreement,
and complete-case review remain authoritative, with no second approval system.
Any deferred impacted owner retains the entire old shared proposal. Missing or
incompatible identity/data bindings fail with a specific diagnostic and return to
the existing clarification flow. No guessed bindings or partial inheritance.

The new definition is appended after summary agreement, preserving historical
definitions, initial displayed content and feedback evidence. A displayed exact
P0 source is updated in the same operation and retains its previous content.
An absent source is not invented: only its exact frozen definition is maintained.
Presentation-only definition title changes update the projection without adding
business questions or resetting business approval. Actual XMind client behavior
and real downstream execution are outside this helper's evidence.

At P1/P2 authoring, first write the complete target sequence from supplied source
materials. Independently compare each proposed P0 step for operation, data
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

Fixed data requires identical bindings and business conditions. For dynamic data,
put an explicit nonempty `generation_rule` string on each source and current data
object. Keep constraints in that rule or existing business fields. Only `value`
may differ; `object_ref`, validity, target requirements and all other business
conditions must match. Different current data IDs bind each case independently.
Do not embed concrete runtime values in operation/assertion prose: use the current
data object. A changed target (for example exactly 20 characters), object relation,
or validity keeps the entire step inline. Resolve contradictory source/target
requirements through existing clarification before offering a complete design;
duplicate candidate data identities are rejected rather than silently selected.
The program cannot detect contradictions inside arbitrary natural-language rules.
Source addresses and assertion IDs alone do not establish
business equivalence. The deterministic comparison is a consistency check of
the agent's source-based decision, not natural-language semantic reasoning.

The candidate stores `id + step_reference` exclusively. The reference binds P0
identity, group, step identity, semantic version, definition digest, data and
context. `data_binding_digest` freezes the ordered current data objects, and the
whole-target digest preserves their values through reconstruction. Dynamic current
values remain visible in the concise review beside the P0 reference. Batch
`step_definitions` contains version-pinned technical dependencies,
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
Reviewed shared data changes create versioned bindings for P0 and continuing consumers. Independent consumers and historical snapshots retain old data. Unchanged generated slots retain current-case values. Subsequent shared and local feedback use the updated bindings.

Shared source history appends a complete prior source snapshot without recursively copying its history field. Existing history entries remain unchanged and traceable.

## TAS-08 consistency corrections

Comparison excludes trace metadata only at the declared step, data record and assertion record levels. Nested business objects keep all fields, including id, source and basis: different object identities cannot qualify as the same step. Reconstruction uses this same rule; an older saved reference that depended on erased nested identities must return to source assessment, never be silently rebound.

Outer operation whitespace is formatting only in generation, local feedback and explicit shared proposals. Literal data and assertion text are not normalized. Shared data feedback that would change both a displayed P0 and P1/P2 is refused before application: use the explicit shared-change proposal with impact dispositions, or author a separately bound local candidate. P0-only feedback retains its existing behavior.
