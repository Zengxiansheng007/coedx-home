# Runtime contract

The router uses Python 3.11+ standard library only. Its sibling official anysearch payload is pinned by upstream-manifest.json. It reuses the official capability/HTTP contract while owning the guard; it never imports upstream code that auto-loads .env, and never modifies the upstream payload.

## Inputs

Objectives is a non-empty JSON array of unique strings. Task ID is a restricted alphanumeric identifier. The host maps an actual explicit instruction to requestedProvider; the query text is not parsed for provider keywords.

For `--provider auto`, `--entry research` opens an AnySearch task and `--entry research-guided` opens a Codex task. An explicit Claude route requires the user's instruction to select Claude retrieval.

Requests is an array of one to five objects. Each has objective and operation (search, get_sub_domains or extract). Search uses query, optional tag/params/max_results/zone/language. Domain discovery uses domain. Extract uses a public URL. All required parameters discovered for a domain tag must appear, including empty strings when appropriate.

For example, a public documentation query can use:
```json
[{"objective":"documented behavior","operation":"search","query":"Agent Skills specification","max_results":3}]
```

## State

State records schemaVersion, taskId, generation, requestedProvider, actual executor, branch, phase, objectives, sources, calls, capabilities, progress and events. Stored state is enveloped with a SHA-256 content digest and atomically replaced. SHA-256 detects accidental corruption, not malicious changes by a user with equal filesystem rights.

An exclusive per-task CLI lock prevents concurrent writers. A leftover lock after process termination requires operator inspection; it is not automatically broken. A persisted started call is recovered as interrupted-request pause, never silently retried.

Phases: anysearch-ready → guided-pending with Codex (default AnySearch service failure); active → paused (fault); paused → original active phase (real user resume); retrieved evidence → review; valid reviewed coverage → complete. Pending guided handoffs are not executed or completed by the state machine.

A task saved under the old implicit Claude default adopts Codex at its next guided handoff or when the user resumes without picking a provider. This advances generation and preserves existing sources. Explicit Claude selections and completed records retain their executor.

## Faults

Only HTTP 402 plus an authenticated call and a JSON envelope with integer code -1 and exact supported message quota_exhausted or user_daily_quota_exhausted is currently recognized as quota. This narrow mapping labels the fault; unrecognized quota shapes still follow the service-failure route to Codex. The generic HTTP status alone never establishes quota.

Default AnySearch service failures (unknown provider errors, HTTP 401, HTTP 429, quota exhaustion, malformed responses, transport errors and missing credentials) immediately hand off to Codex without retrying AnySearch. HTTP 403, redirects, boundary/integrity denials, non-public source URLs and invalid request inputs pause/deny without fallback. Explicit provider choice and no-fallback take precedence. The entire request batch is validated before checking credentials or issuing calls. Responses and exception text are not logged raw. Credential-like fields and the actual request key are removed before evidence persistence. API base overrides and redirects are denied.

No-fallback overrides automatic switching. A guided Claude failure can move to Codex only if the host recorded a real applicable prior Codex authorization; otherwise pause and ask the user. User-selected Codex starts directly.

## Quality

A review JSON includes taskId, generation, reviewedBy=Codex, actualEvidenceReviewed=true, gaps=[], and claims. Each claim has text, objective, and non-empty sourceIds resolving to stored source content for that objective. Every objective must be covered. The host must inspect facts; structural acceptance is not proof that claims follow semantically.

Sources keep original URL, retrievedAt, readDepth, objective, actual executor and a content-based source ID. Search content remains search-result even if the provider labels it content; only extract/host-attested full reading is body depth.

A reinforcement command allows one additional content round. It cannot run while paused and cannot be used as error retry. Explicit human resume is the only recovery trigger. Existing guided internal format-repair rules are preserved separately.

## Recovery probe

Resume records recoveryPending. Completion and reinforcement remain denied until a real successful provider operation or matching validated guided receipt clears it. Existing evidence is preserved but cannot bypass this recovery check. Task-state directories inside the installed sibling Skill container are rejected.

## Evidence continuity on fallback

Fallback increments generation, selects Codex and preserves sources with their original executor, depth, URL and IDs. Recovery remains pending until a matching validated actual Codex retrieval receipt arrives. The handoff carries evidencePolicy=reuse-verified-and-fill-gaps and requiresEvidenceReview=true. Objectives are not covered merely because results exist: the host inspects existing evidence and retrieves only missing or insufficient parts. Final review covers every original objective across both providers. Codex failure pauses without automatic retry, bounce or background resume.
