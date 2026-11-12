# Same-version chat delivery

Apply this contract to initial P0 authoring, batch clarification, scoped review,
feedback, dependency and product-rule regeneration, and P1/P2 expansion.

1. Self-check source semantics, identity, preparation and data rules before delivery.
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
