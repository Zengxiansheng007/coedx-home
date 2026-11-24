# Dependency and data-condition authoring

Use this branch when a current case creates, consumes or changes an object used
by another module. Read the supplied human points and complete independent cases;
trace the object lifecycle and likely producers/consumers. Propose each impact
with source locations and explain inclusion/exclusion consequences. Ask the user
to choose scope through the existing batch clarification workflow. A dependency
display never grants execution or change approval to its target.

Read whole independent cases and select a suitable business endpoint. If none fits, write the complete needed operations inline; unknown endpoints return to clarification. Never slice arbitrary ranges or silently skip trailing actions.

## Public batch entry

`dependencies.review_dependencies(catalog, batch_id, current_case_ids, proposals,
approved_validation_scope=None)` is pure and uses the scoped-review full-catalog
contract. The full input remains unchanged. It returns complete selected cases,
same-version `human_view` and `xmind_markdown`, `findings`, `blockers` and
`ready_for_final_review`. This last value means conditions are filled; final
review remains a separate user action. Data creation, validity checking,
persisting/replacing actual identifiers, scheduling and execution are downstream.

Each proposal contains:

- `id`, `current_case_id`, target `case_id` and full `module_path`, `direction`
  (`operation`, `pre` or `post`), and `basis` with exact source references for the impact.
- `purpose`, `required_state`, `inputs`, `outputs`, `object_binding` mapping
  business object names to existing `data_refs`. Bind a postcondition to the
  exact object produced by this run, with its recipient/role references as needed.
- `complete_case: true`, `final_state_matches: true`, `applicability_basis`
  documenting actual inspection; these are agent conclusions, not proof supplied
  by the helper. Step subsets are rejected.
- `decision: {include: true|false, actual_reply: ...}` containing the user's real
  words. Missing decisions stay pending. Optional `script_asset` requires
  `managed_by: ui-test`, `applicable: true`, `ref`, and `basis`.

The included current case contains the reference and all necessary conditions,
at its requested operation position or explicit pre/post group. The complete target stays
independent with its original module path. A special post group appears only
when required, with the same one-data-node and sibling-expectation structure as
special preconditions. Shared data remains authoritative in `data`.

## Data decisions in each referenced data record

Retain value/condition or credential reference, provenance, accurate
`identity_ref`, `object_ref`, `validity`, `validity_check`, `reuse_policy`,
`invalidation_action`, and `policy_decision.actual_reply`. Propose based on the
business lifecycle, ask missing decisions together with independent scope
questions, and preserve the reply through summary and final review.

- `long_term`: reuse after checking the saved exact identifier and associations
  remain valid. No automatic re-preparation.
- `time_limited`: supply `valid_until`, `downstream_window`, and an evidenced
  `covers_downstream_window: true`. A window not covering downstream execution
  remains unresolved rather than being treated as reusable.
- `exclusive`: bind `exclusive_case_id` to the consuming case; other cases need
  separate data. Ask the user about subsequent runs of this same case:
  `subsequent_use: {choice: reuse_if_valid|new_each_run, actual_reply: ...}`.
  Neither option is the default.

`invalidation_action` is `ask_user` unless reviewed complete re-preparation was
explicitly allowed (`rebuild_complete_precondition` with
`rebuild_decision.actual_reply`). Downstream must use the full referenced
preparation case, save the new exact object association after success, and then
continue. Apply this rule only to pre-execution invalidity; a business failure
during testing remains a failure. Data reuse never implies browser-session reuse.

When reference or data conditions are blocked, resolve the named findings using
batch clarification, update the source candidate/data through its approved
summary, and regenerate the dependency review before final review. Do not submit
a blocked copy for final review or merge.

## Report reconciliation and file entry

Keep functional scope separate from related-case display. If the upstream case
is itself in the approved functional scope, it still needs a full matching P0
functional report. Use `p0_evidence.approve_p0_scope` and `check_extension` from
the P0 evidence contract. `purpose: preparation_reuse` cannot satisfy a
functional result; missing or mismatched evidence remains pending. For a pure
preparation dependency, express reused data satisfying conditions without
claiming functional execution or shrinking an already approved P0 scope.

```text
python -B scripts/dependencies.py --catalog full-catalog.json --request dependency-request.json --output-dir new-dependency-review
```

The request has the public function arguments except `catalog`. The new output
contains `candidate.json`, `dependency-review.json`, `xmind.md`
and companion review notes. P0 is presented as the four-column business view and
same-version XMind Markdown. Expansion uses the existing scoped-copy default.
Render again via `authoring.render_batch`; clarification preserves these groups.
No extra execution handoff checklist is generated. XMind desktop import and
formal ui-test consumption still need their separate verification.

## Ordered whole-case references and recovery

Use direction: operation and zero-based position to place a whole reference within the actual step order. Pre/post groups are only used when explicitly requested. Read the current full source case, including trailing actions, and its explicit endpoint. Any priority may be independently complete; this does not waive the full P0 qualification for a new P1/P2 extension.

required_state must match the source endpoint. Unknown endpoints return to clarification. For incompatible endpoints (such as payment after creating an unpaid order), select alternative_case_id from the current catalog or author all needed inline_operations with unique IDs, complete operation/data/expected/verification, inline_endpoint and inline_basis. Preserve purpose, necessary conditions and same-object input/output bindings. Never extract arbitrary ranges or silently skip trailing actions.

Every new reference binds source_digest to actual complete source content and referenced data. cross_module_references.resolve_case_reference(catalog, edge) rereads supplied content and rejects missing or changed sources even when version labels are unchanged. Reload actual sources before generation, changes and recovery; a cached catalog is not evidence of currentness. Legacy unbound references require reassessment. TAS-11 composes nested preparation/P0 dependencies and cycle checks before review. Only affected references require reassessment; no persistent expanded copy is produced.

Updating the same proposal ID replaces its reference without duplicating operations or changing the independent target. A shared target change is separately reviewed.
