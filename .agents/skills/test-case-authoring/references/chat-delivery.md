# Same-version chat delivery

Apply this contract to initial P0 authoring, batch clarification, scoped review,
feedback, dependency and product-rule regeneration, and P1/P2 expansion.

1. 先完成[专业生成核对](professional-generation.md)的源材料解释和内部完整还原；
   对照实际文件的业务路径、逐例目标、准备/步骤归属、独立结果、数据及范围例外。
   Self-check source semantics, identity, preparation and data rules before delivery.
   Persist candidate JSON, the XMind scope copy, necessary coverage/review notes and
   the task's existing Q&A MD. Never write human-view Markdown or a human-view total
   table. Existing historical files remain unchanged.
2. Deliver the XMind scope link and a concise status/pending summary by default,
   including for P0. Review scope contains only new and related cases; an unshown
   case still exists in the complete source. Display scope never determines test
   scope, deletion, approval or merge scope.
3. When the user needs 1–9 cases expanded, resolve their business descriptions
   against the current source through the presentation identity contract. Ask about
   ambiguous same-name cases rather than guessing. Internally call
   `presentation.render_chat(batch, case_ids=[...])`. The returned `human_view`
   is the complete four-column text to place directly in this conversation;
   `content_version` and `case_ids` bind it to the candidate. Never save this text
   as a companion MD or substitute a hand-authored summary for complete cases.
4. No selection means no human table. Empty, unknown, duplicate and over-nine
   selections are rejected. For a larger request, supply the XMind copy and ask
   which 1–9 need discussion. Do not automatically continue with the next chunk,
   repeatedly select nine, or dump a large batch through pure rendering APIs.
5. After a confirmed change is applied once through the existing review workflow,
   regenerate XMind from that new version and re-project only the requested cases.
   Preserve complete preparation, special pre/postconditions, action/data/result
   correspondence, dynamic business data rules and linked case names. Projection
   never changes source identity, data, versions, or approval records.
6. Render preparation notes as prose before their table and separate every group
   and pending-question section with blank lines. Project current effective rule
   meanings once: retain per-question interpretation, accumulated answered parts,
   provisional expected behavior and product checks, and deferred scope/reason.
   A separate deferred branch remains unknown and excluded, without blocking an
   otherwise resolved current case. Keep machine update paths, Q&A references,
   original whole-round replies and superseded rule history in internal records.
   Legacy decisions without interpretation retain their original answer; do not
   infer or rewrite missing business meaning. Ordinary business extension fields
   named updates/path are not rule audit structures and must remain visible.

`render_chat` is a pure public API and performs no writes. The older full pure
rendering APIs remain available for internal semantic comparison; their returned
`human_view` is not an instruction to display or persist a full batch. CLI authoring,
scope and dependency entries emit no human-view file. `render_extension` accepts
legacy `case_id` or keyword `case_ids`, never both, using this same 1–9 contract.
Final review still assesses the complete changed scope and exact version using
the XMind copy; chat expansion is optional and does not bypass review.
# Scope provenance for common operations

`render_chat(batch, case_ids, source_catalog=...)` assesses the complete current
candidate and renders the requested 1–9 cases together. Public extension delivery
accepts the same optional exact original catalog. A chat selection is only a
display selection: it neither rewrites `initial_copy_baseline` nor creates a new
scope review. Module common definitions appear once; other case bodies and
questions are not included. Existing applicable and excluded membership remains
authoritative, including per-item postconditions and current data bindings.

Supply `source_catalog` for a genuine partial source copy; its digest and version
must match the existing baseline. Never pass the current candidate as its own
original catalog. A complete bounded candidate created against an empty catalog
can assess its complete current membership locally. Missing or stale required
parents remain pending. Rendering preserves the candidate version and source
records and cannot stand in for fresh generation or user review.

模块展示顺序固定为：公共前置定义、原业务分组及具体用例、公共后置定义。各区内保留原有顺序；没有公共后置时不创建空项。聊天与 Markdown 共用该顺序；旧稿回传保留原来源映射，排序变化不作为业务修改。

## Independent case handoff

An independent executor reads `content_version` and `case_ids` from the delivered
`agent.json`. Select one listed case and pass that exact version:

```shell
python scripts/single_case.py --agent path/to/agent.json --version <content_version> --case <case_id> --output case.json
```

Keep the index with its candidate and any indexed parent catalog. The command checks
the selected case, its step and data identities, and the versioned sources, then writes
to a new output path. A scope or source mismatch requires the matching delivery.
For the existing direct candidate workflow, use `--candidate candidate.json` in place
of `--agent` and add `--source-catalog <exact-parent.json>` for a partial copy.
For chat, call `presentation.render_chat(batch, [case_id], source_catalog=parent_if_scoped)`.
Read the current case's context, ordered preparation and steps, and any postconditions.
Each step's `data_refs` names records in the attachment's `data` object. Use their actual values,
preserving omitted keys, empty strings and objects. Replace only existing placeholders with
this environment's values; preserve the remaining path, query and per-run identity.
Each method specifies its timing and original step, context or data slots in `applies_at`.
An explicitly pending applicability keeps its original case condition. The last business
step and its checks are identified by `endpoint`. Preserve the current case's review and
execution status. If retrieval reports a missing parent, data, step, or assertion, supply
the exact missing source and retry. Execution records each assertion against this run.

A single named case expands legacy whole-step references with their original P0 title and step
number, current input, operation, expected outcome and independent checks. Each executable
expected or verification item needs nonblank business text. Use the case, group, step and
claim field from a retrieval error to correct the candidate at its source.

## Paired reader delivery

Use the normal writer for both files. A new full authoring run uses `authoring.py`;
for an assessed complete candidate use `source_preparation.py --candidate ... --output-dir ...`.
While drafting, pass repeated `--case` to the latter entry for the actual ordered review list.
For a premerge scope use `scoped_review.py --catalog ... --request ... --output-dir ...`
with the selected cases in the request. The full, draft, and premerge deliveries retain their
separate authorization and review boundaries.

Read the version and selected IDs from the Markdown and the adjacent `agent.json`.
The index points to the authoritative `candidate.json` and, for a partial catalog, the exact
`source-catalog.json`. Its `cases` maps each selected identity to its step and data references.
Keep these files together when moving a delivery. Regenerate the pair after confirmation of
a source change. A copy of the full parent provides reference context, including hidden P0
inputs, while the index lists only the current review selection.

Use data-record root fields `validity`, `generation_rule`, `reuse_policy`, and
`invalidation_action` for execution instructions. Put a business input or acceptance
condition under its bound step. An actual property with one of these names inside a JSON
input retains its meaning. For a source preparation's data or evidence definition,
`review_condition` can name the observable business condition at its applicable step.
Use an explicit empty string when there is no such condition. Older evidence methods retain
their timing at each bound step. Their detailed collection instructions stay in the Agent source.
