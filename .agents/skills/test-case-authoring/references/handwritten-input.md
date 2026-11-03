# Complete handwritten P0 adapter

Read the supplied case as a complete business scenario: identity, module path,
role, initial state, preparation, ordered operations, data, expected results and
observable checks. Extract existing details before asking anything. This is an
agent interpretation step, not automatic parsing of arbitrary documents. If the
input contains several scenarios, identify and split complete cases explicitly;
convert each independently before collecting them in the shared review batch.

Use the [batch contract](batch-contract.md) with these input substitutions only:

- Source claims use `source: handwritten` and exact 1-based `lines`.
- `handwritten_coverage` accounts for every nonblank line with a reason.
- Supplied expectations remain material statements, not observations, user rule
  decisions or final approval. Optional PRD uses `source: prd`. Preserve conflicts
  side by side. Missing information remains missing; mark AI proposals as inference.
- Business values belong in `data`; retain object association, validity, reuse
  and invalidation conditions when supplied. Use credential references only.
- If the input explicitly states that no extra preparation is needed, preserve
  it in `common_preconditions_note` as a source claim. An empty preparation list
  alone means no preparation was provided, not an explicit business decision.

Run the same converter, selecting the handwritten input:

```text
python -B scripts/authoring.py --handwritten sanitized-p0.md --interpretation interpretation.json --output-dir new-candidate-output
```

Add `--prd requirements.md` only when supplied. In-process callers use
`build_handwritten_batch(handwritten, interpretation, prd=None)`. Results have
the same batch, data, questions, statuses and dual-view contract as `build_batch`;
source identity/digests, provenance and coverage remain specific to the input.
Versions can therefore differ even for equivalent business content.

Compare both views against all supplied steps and conditions. Show the inspection
result first, allowing optional additions before clarification. A complete input
does not need repeated role/state/data questions. Missing or conflicting fields
enter the existing [batch clarification](clarification-contract.md), including
summary agreement and separate final review. Complete inputs with no questions
still need explicit current-content summary agreement before final review.
There is no handwritten-only approval, merge path or separately maintained body.

Use clearly labeled synthetic sources/replies for self-tests. Keep source text,
interpretation, generated views, question/answer history and limitations available
for review. Self-tests do not prove real UI execution, XMind client acceptance or
formal integration; they do not require an additional user joint-acceptance chain.
