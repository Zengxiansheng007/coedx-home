---
name: research-guided
description: Run evidence-guided research when invoked directly, when the research router hands off, or when the user explicitly selects Codex or Claude retrieval. Use Codex by default and Claude only when the user explicitly selects it. Route generic research through research.
---

# Research Guided

## Operating Rules

- Use Codex for retrieval by default. Select Claude only from an explicit user instruction to use Claude for retrieval. Treat product names in the research topic as search terms.
- Read [entry compatibility](references/router-entry-compatibility.md) before retrieval. Use [the Claude profile](references/claude-profile.md) for the explicit Claude branch, including its preflight, approval, schema and fallback rules.
- Codex owns the research outline, evidence review, reinforcement decision and final decision for both executors.
- Start with the [strong gate](references/strong-gate-and-light-path.md). For an objectively simple task, use the light path only after the user confirms the downgrade. Record the decision and results.
- Use the task's authorized data sources and tools. Preserve private, internal, login-gated and restricted-source boundaries.
- When maintaining this skill, follow [change-record traceability](references/change-record-traceability.md). Candidate validation and global installation require separate evidence and authorization.

## Workflow

1. **Select the executor and depth.** Use the actual user choice or router handoff and record the selection. For standard or deep research use the full workflow, with deeper coverage for deep research.
2. **Plan.** Define scope, objectives, priorities, exclusions and expected source types. Record the outline and evidence targets in the research packet.
3. **Retrieve.** On the default Codex path, use current host search and page-reading tools. Inspect existing sources first and retrieve missing or insufficient evidence. Record actual queries, tool evidence, URLs, read depth and relevant findings. On the explicit Claude path, apply the adapter gates before the first retrieval round and preserve structured output.
4. **Review.** Inspect sources, map claims to evidence and compare coverage against the outline and applicable requirements, design and tests. Apply [severity rules](references/severity-and-fallback-rules.md). A structurally invalid packet fails validation. Resolve P1 decisions with the user as specified there and log any P2 format repairs.
5. **Reinforce once if needed.** Use the selected executor for at most one targeted content round to address P0/P1 coverage gaps. Record the gap list, queries and closure. Keep format repairs separate from content retrieval. If the tool fails, follow the entry profile's pause or authorized recovery rules.
6. **Decide and report.** Apply [the decision gate](references/decision-gate-rules.md). Record the outline, executor, first-round evidence, gaps, any reinforcement and the final decision with an evidence index. Return partial, blocked or rerun when the remaining evidence requires it. For router tasks, use the guided handoff contract linked from the entry reference. Complete only after coverage review.

## Scholar Compatibility Bridge

Use the optional bridge under `scripts/compatibility/` and
`fixtures/compatibility/` only with an accepted Research result, an actual
frozen ledger and a lineage-bound pipeline plan. The fixed
`scholar-deep-research` baseline retains `research_state.py`, Phase 0..7, G1..G7,
ranking, triage, citation-chase, report and export contracts.
Fixture runs report `test-completed`. Product completion requires a
`live-scholarly` plan with real scholarly evidence identified by DOI,
OpenAlex, arXiv or PMID. Ordinary pages remain evidence-only.

## Validation

For changes to this package run:

```text
python scripts/validate_research_skill.py <skill-folder> --require-change-records
python scripts/test_research_skill.py
python scripts/scan_sensitive.py <skill-folder>
```

For routing changes also run the sibling router's offline runtime suite. For
Claude profile checks follow its [validation commands](references/claude-profile.md#validation).
Forward-test with an ordinary guided request, a topic that mentions Claude
and a request that explicitly selects Claude retrieval.

## Escalation

Obtain authorization before global installation, dependency installation,
publishing, destructive changes or access beyond the task's data and tool
scope. For Claude-specific escalation, use the Claude profile.
