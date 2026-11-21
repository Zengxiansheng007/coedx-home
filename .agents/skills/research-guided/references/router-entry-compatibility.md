# Entry compatibility

Both executors use the strong gate, the approved light exception, at most one content reinforcement round and final Codex review.

## Executor selection

The sibling `research` Skill handles generic requests and defaults to AnySearch. Use Codex when invoked directly, when the user explicitly selects Codex, or when the router hands off a qualifying AnySearch service failure. Use Claude only when the user's instruction clearly selects it for retrieval.

For direct entry through the router CLI, use `create --entry research-guided` with the normal task and objective arguments. The default provider resolves to Codex. An explicit Claude selection uses `--provider claude --user-choice <actual-user-instruction>`. A user-authorized change on resume uses the actual user message and selected provider.

## Preserved profiles

Codex uses current host retrieval tools. Record observed search and page-reading evidence and validate it against the objectives. Router handoff tasks use the existing host receipt. Claude uses the [explicit Claude profile](claude-profile.md) and its preflight, registry, schema and adapter checks. Existing Claude packets retain their original validators.

When a user-selected Claude run fails, apply the explicit profile's pause and authorized fallback rules. If Codex retrieval fails, pause for user-directed recovery. Keep permission/security restrictions and no-fallback constraints in effect.

For router tasks, follow the [guided handoff contract](../../research/references/guided-handoff.md) when returning evidence. Record the actual executor, tool runs and outcome.

For a qualifying AnySearch fallback, use the router's existing authorization. Inspect and reuse verified sources and retrieve missing or insufficient evidence.
