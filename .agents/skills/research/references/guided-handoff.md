# Guided handoff

Read the sibling research-guided/SKILL.md and its entry-compatibility reference. Codex is the default for direct guided entry, explicit Codex selection and qualifying automatic AnySearch fallback. Use the Claude preflight and adapter validation when the user explicitly chose Claude.

The router emits kind=research-guided-handoff with taskId, generation, executor, pending objectives and existing sources. The host must actually run the selected guided workflow; the router does not spawn external models itself.

After the host's original workflow validation, accept-guided consumes a receipt with taskId, generation, executor, actualRetrieval=true, hostValidationPassed=true, non-empty toolEvidence and sources. Each source has url, title, content, objective and readDepth. The host is responsible for attaching true tool execution evidence and for retaining the original detailed packet. Do not manufacture hostValidationPassed or provider/MCP fields to pass a check.

The receipt must match current task, generation and executor. A result from before resume or from another provider is rejected. Accepted evidence still requires the router's coverage review; it is not automatically marked complete.

Claude unavailable: record guided-failure; applicable prior Codex authorization allows the selected fallback. Without it, pause. A failed Codex execution pauses without bouncing back to AnySearch. Existing user no-fallback constraints win.

## Automatic AnySearch-to-Codex handoff

When execute-anysearch returns guided-pending with executor Codex, continue immediately using current host public search and page-reading tools. Do not ask for another provider choice or invoke Claude first. Inspect existing sources, preserve verified evidence and provenance, then retrieve missing or insufficient coverage. Pending objectives await final quality acceptance; they do not require repeating valid retrieval. Preserve the outline, coverage, one content reinforcement round and final review. Record actual tool evidence in a matching accept-guided receipt. If Codex retrieval fails, use guided-failure and pause. Explicit backend/no-fallback and permission/security constraints still win.
