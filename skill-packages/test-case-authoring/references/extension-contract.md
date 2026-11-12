# P1/P2 design batch and coverage v1

Read this when P0 entry permits extension. Business analysis belongs to the
skill reading actual sources; the helper checks deterministic completeness,
identity, versions and gates. Structured sample input alone does not evaluate
the skill's interpretation of natural language.

## Public batch entry

```python
from extension import build_extension, render_extension
result = build_extension(catalog, baseline, reports, entry_request, design)
```

The first four arguments are the unchanged full catalog and
[P0 evidence contract](p0-evidence-contract.md) inputs. The helper calls
`check_extension` again; a copied `can_extend: true` receipt is insufficient.
Use `mode='simulation'` only for labelled synthetic development samples.
The resulting evidence remains simulated and cannot open a real business gate.

`design` contains:

- `batch_id`, `candidates` (complete P1/P2 records), `candidate_data` (new or
  revised data), and optional `selection` using the
  [scoped review contract](scoped-review-contract.md). Selection may include
  complete related existing cases; display does not approve execution.
- `manual_points`: each has unique `id`, source `basis`, and nonempty `checks`.
  A check has unique `id`, `description`, and required `aspects` (e.g. save,
  recipient visibility). Each separate boundary check also has `boundary_group`
  and its actual `input`. A boundary links one case; different inputs in the
  same group use different case IDs. Compare data/operation semantics against
  the input yourself; the helper cannot understand arbitrary prose limits.
- `coverage`: exactly one record per required check, with `check_id` and
  `links`, each containing `case_id` and covered `aspects`. Missing aspects
  require a concrete `pending` explanation. A deliberate disposition instead
  uses no links and `decision` with `route: deferred | excluded`, source `basis`
  and `actual_reply`. Split mixed covered/disposed aspects into distinct checks.
- `ai_suggestions`: independent extra combinations, each with `id`, `proposal`,
  `basis`, `risk`, `uncovered_scope`, and user `decision` with
  `route: include | defer | exclude` plus `actual_reply`. Include supplies
  `case_ids` for complete independent cases; other routes supply no cases.
  `uncovered_combinations` lists the remaining range even when no extras chosen.
- `ui_gaps`: concrete `description`, source `basis`, `recommendation`, affected
  `case_ids`, and `decision` with `route: write_first | explore_first` plus actual
  words. Undecided/explore-first blocks generation of this batch; after supplied
  exploration, re-evaluate evidence. Independent work can use a separate batch.
  Write-first preserves the gap and user authorization, not invented UI facts.

Each candidate has `priority: P1 | P2`, `priority_basis`, `priority_factors`
with `importance`, `risk`, `frequency`, complete `context.role/initial_state`,
and `data_preparation`. Each operation has expected and observable verification
claims. Data references resolve to single-source data records with object,
validity, reuse and invalidation conditions. The agent proposes these conditions
from sources and brings doubts into grill. Data is never actually prepared here.

The helper resets new/revised candidates to unconfirmed, pending review,
not merged and not run. Each priority proposal creates a required batch doubt.
Enrich these and any other rule doubts with the
[shared clarification API](clarification-contract.md). A reply can change
`cases/<index>/priority` and its basis using the declared target paths.
Priority confirmation is not final review. Reuse existing explicit decisions
when unchanged; never manufacture replies from silence.

## Same-version review

`build_extension` returns `batch`, `xmind_markdown`, `review_notes`, `changes`,
`coverage` and `coverage_notes`. Coverage derives complete/partial/gap from
covered versus required aspects; deferred/excluded retain actual user evidence.
Whole-point status is complete only if all checks are complete. Expected and
verification summaries come from current linked cases, not a second edited text.
The batch retains original manual input, coverage mappings, decisions and P0
entry basis in `extension_design` and `extension_entry`.

After `apply_summary`, call `render_extension(session['batch'])` for the scoped
Markdown and coverage notes at the updated content version. Use
`render_extension(batch, case_id='...')` for a requested single case, or keyword
`case_ids=[...]` for 1–9 requested cases; follow [chat delivery](chat-delivery.md).
The returned four-column text stays in chat. Regeneration preserves the original scope baseline;
it does not apply returned-file feedback or merge. Read complete cases and all
coverage decisions during final review, including missing/deferred scope.

```text
python -B scripts/extension.py --input envelope.json --output-dir new-review
```

The JSON envelope contains the five named API arguments. CLI creates a new
directory only: `candidate.json`, `coverage.json`, `changes.json`, `xmind.md`,
`review-notes.md`. The baseline is embedded in `candidate.json`; full inputs are
unchanged. Full-batch human-view is omitted by default. No execution, merge,
exploration, XMind client acceptance or formal ui-test integration is implied.
