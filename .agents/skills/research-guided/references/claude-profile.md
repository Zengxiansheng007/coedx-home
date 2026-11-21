# Explicit Claude Retrieval

Use this profile when the user explicitly chooses Claude retrieval. Codex still
plans the outline, reviews coverage, decides whether to reinforce, and accepts
the final result.

## Workflow

1. Read [the adapter contract](claude-adapter-contract.md). Resolve the adapter, its execution mode and tool registry, then pass preflight before the first round.
2. For standard and deep public research, Codex can approve the Claude call and the registry's four public read-only Exa and Firecrawl tools within the adapter contract. Private repositories, login-gated or paid sources, internal systems, private documents, internal paths, screenshots, business data, credentials, dependency installation, and arbitrary shell/network tools require separate authorization. Treat tools outside the registry as a scope mismatch.
3. Give Claude the outline and registry. Require structured sources, claims, gaps and review evidence. Check the result before using it for coverage review. Preserve raw malformed feedback, repair only the workspace copy, and validate before advancing. A flat or malformed workspace is `repair-needed` until validation passes.
4. For a targeted reinforcement round, use the same executor and approved tools. Get separate authorization for a new restricted source or tool. Apply the same artifact and validation gates.
5. If the adapter is unavailable, record the failure and pause. Use Codex fallback only with applicable recorded user authorization, subject to any no-fallback constraint. Apply [severity and fallback rules](severity-and-fallback-rules.md).

## Live Adapter Requirements

- **Live Claude research must reject permission mode plan** (FR-RR-001). Plan mode cannot execute tools and will stall the research loop. Allowed modes: `default`, `acceptEdits`, `auto`, `dontAsk`.
- **One JSON registry owns the four approved MCP tool names** (FR-RR-002). The registry at `schemas/public-research-tool-registry.json` is the single source of truth. Use `scripts/check_tool_drift.py` to detect drift.
- **Preflight must verify** executable, CLI capability, fresh session, MCP schema visibility, tool count, exact registry match, canary evidence, and zero permission denials before live research (FR-RR-003). Use `scripts/preflight_research.py`.
- **Claude output must be pure UTF-8 JSON** validated by `schemas/research-result.schema.json` (Draft 2020-12) and semantic evidence gates (FR-RR-004). Use `scripts/validate_research_result.py`.
- **Format retries and content reinforcement are separate and bounded** (FR-RR-005). Format repair: max 3 retries without new retrieval. Content reinforcement: max 1 round. Use `scripts/live_mode_guard.py`.
- **Stable failure classes propagate** through research, handoff executor, feedback reviewer, and development-system contracts (FR-RR-006). See `schemas/failure-classification.json`.
- **Two-stage adapter-validated compatibility mode is explicit** (FR-ADP-001). The run records `schemaEnforcementMode` (`provider-native` or `adapter-validated`) and `providerNativeSchema` honestly. Activation cannot occur silently after a provider-native failure; the `adapter-validated` profile is selected only by an explicit profile, never as a silent downgrade.
- **Retrieval and serialization are separate phases with separate tool boundaries** (FR-ADP-002). Retrieval uses only the approved public MCP registry; serialization exposes no retrieval, shell, browser, filesystem-write, or network tools.
- **Retrieval evidence is frozen before serialization** (FR-ADP-003). Queries, tool calls, permission results, sources, content digests, timestamps, session lineage, boundary checks, and the registry hash are persisted into `schemas/research-evidence-ledger.schema.json` and canonical-hashed. See `scripts/serialize_research.py`.
- **Serialization cannot introduce unsupported facts** (FR-ADP-004). Every final source, URL, claim, and claim-source mapping must resolve to the frozen evidence ledger; additions fail validation.
- **Local validation is the acceptance authority** (FR-ADP-005). Draft 2020-12 Schema validation and semantic gates pass before an output can claim complete, in both modes.
- **Format repair is bounded and performs no retrieval** (FR-ADP-006). At most three serialization attempts are recorded; all use the same evidence hash; exhaustion returns `blocked` or `repair-needed`, never `complete`.
- **Provider-native behavior remains available and unchanged** (FR-ADP-007). Native-mode regression tests pass; compatibility mode is selected only by an explicit profile.
- **Failures propagate without false completion** (FR-ADP-008). Tool denial, missing URL, invalid Schema, source drift, new facts, retry exhaustion, timeout, or sensitive output cannot produce `complete`.
- **Real runtime integration is required but separately approved** (FR-ADP-009). A fresh GLM 5.2 session performs a real approved Exa search and produces a final Research packet with zero P0/P1 findings. Do not execute the live canary in a development-only packet.
- **Candidate and global deployment states remain separate** (FR-ADP-010). Global installation requires the exact source hash, backup, atomic replacement, rollback and separate approval.

## Validation

Research repair validation (FR-RR-001 through FR-RR-006):

```powershell
python scripts/test_research_repair.py
python scripts/preflight_research.py --permission-mode default --session-id test --session-started-at 2026-08-25T10:00:00Z --visible-tools mcp__exa__web_search_exa mcp__exa__web_fetch_exa mcp__firecrawl__firecrawl_search mcp__firecrawl__firecrawl_scrape --requested-tools mcp__exa__web_search_exa mcp__exa__web_fetch_exa mcp__firecrawl__firecrawl_search mcp__firecrawl__firecrawl_scrape --canary-json "{\"canaryPassed\":true,\"canaryDetail\":\"ok\"}" --skip-cli
python scripts/live_mode_guard.py --mode live --permission-mode default --requested-tools mcp__exa__web_search_exa mcp__exa__web_fetch_exa mcp__firecrawl__firecrawl_search mcp__firecrawl__firecrawl_scrape
python scripts/check_tool_drift.py
```

Two-stage adapter validation (FR-ADP-001 through FR-ADP-010):

```powershell
python scripts/test_research_adapter.py
python scripts/serialize_research.py --ledger <frozen-ledger.json> --candidate <serialization-candidate.json>
```

The adapter tests cover unit (ledger freezing, canonical hashing, retry counting,
candidate extraction, source/claim mapping), contract (Schema + semantic gates
for both modes), integration (fake retrieval transcript through both stages),
negative (prose-around-json, malformed JSON, missing field, ledger-absent URL
and claim, serialization tool access, permission denial, evidence hash change,
three failed attempts, silent downgrade), regression (provider-native mode),
cross-skill failure-class propagation, and sensitive scans. No live external
call is executed by these tests.
