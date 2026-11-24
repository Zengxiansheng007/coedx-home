# Current-source restoration before review and handoff

Use the existing candidate as the only maintained business authority. The public render, review, artifact writer and checkpoint/resume interfaces perform transient reconstruction; never save the expanded result as another case catalog or per-case ledger.

- Existing drafts use build_scoped_review and render_review_batch; they do not require fabricated P0 execution qualification.
- render_review_batch(batch, source_catalog=current_catalog) accepts a caller-read source catalog. A pure render is planned; fixed definitions alone cannot establish current P0 validity at approval or delivery.
- review(session, decision, source_catalog=current_catalog) and review_feedback accept current source evidence. Without a current source, active fixed P0 references block selected approval. The caller must identify the source and reading basis in the existing task record; a generic new JSON state pack is not required.
- write_artifacts(result, output, source_catalog=current_catalog) reads existing technical documents relative to output, checks nonempty content, anchors and declared version/object/applicability/endpoint or SHA256, writes module notes, and reads them back. It preserves blocked originals in result.batch and writes only ready business scope. A planned link is not materialized proof.
- checkpoint_record accepts optional source_catalog_path; resume re-reads that source and the actual candidate. Source descriptors may carry explicit case_ids for selective drift blocking; sources without a known scope remain stage-wide conflicts. Technical document links are checked relative to the candidate directory. The sole task Markdown retains recovery metadata; no independent answer authority is added.

Whole-case operation references restore all four groups recursively, data, assertions and endpoint via resolve_case_reference. Cycles, stale sources, missing targets, object associations and inapplicable endpoints generate concrete blockers and clarification requests. Unrelated known cases continue. Top-level legacy dependency descriptions remain readable metadata; executable references belong on complete step.dependency objects.

Preparation remains lossless in candidate.common_preconditions. preparation_scope is a reviewed display extraction, with membership/exception/source/version/frequency bindings; invalid scopes stay inline rather than inheriting silently. Restoration reads those original operations and their data. No preparation action is executed.

P1/P2 generation and recovery retain the whole-round P0 prerequisite check. A failed required P0 cannot be removed from that scope to qualify extensions. Existing-draft review does not manufacture that qualification. Source approval, rendering, materialization, actual dialogue, XMind client operation and business execution remain separate evidence.

Valid P0 whole-step references inside a whole-case dependency are recursively restored before operation/assertion completeness is checked. Necessary source definitions and candidate definitions are merged by source case/group/step/version; conflicting business definitions block only their dependents. Presentation-only title changes do not replace step meaning. Current source steps/data and the P0 qualification boundary remain mandatory.

Restore common_postconditions through the same source step resolver and preparation_scopes v2 directional binding. Keep common pre, special pre, steps, special post, common post order and source endpoints. Absence in historical candidates must not change reuse signatures or invent obligations.
