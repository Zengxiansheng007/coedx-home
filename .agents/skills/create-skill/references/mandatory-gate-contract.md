# Mandatory Gate Contract

Use this contract when a generated or updated Skill claims that a condition is mandatory before delivery or a protected action. A `gate-contract.json` is an **untrusted declaration** in the Skill package. Its presence and structural validity are necessary inputs to host review, never proof that an enforcement point exists.

## Responsibility split

| Owner | Responsibility |
|---|---|
| Agent | Draft the Skill and contract; identify protected effects, conditions, candidate checkers, and known alternate paths; repair failed candidates. |
| Local validator | Check package structure, contract shape, required fields, links, and obvious unsafe content; return `validated-candidate` only when P0/P1 findings are absent. |
| Trusted delivery entry | Independently check package bytes, effect inventory, runtime capability, test evidence, approvals, and all reachable paths; alone issue an acceptance receipt and install into a controlled target. |
| Trusted runtime entry | Intercept every protected action, verify its exact current arguments and state, use a deterministic checker or independent human/policy decision, and deny missing, stale, failed, or inconclusive checks. |

Keep the acceptance receipt and protected target outside Agent-writable locations. A report field, exit code, Hook configuration, or receipt copied into the candidate package cannot grant acceptance. If the Agent can reach the same effect through shell, `apply_patch`, MCP, another API, or direct target writes, gate or disable those paths before making a hard-gate claim. Limit the claim to the verified runtime and effect; ordinary Codex sessions and unverified runtimes remain unsupported.

## Candidate contract

Place `gate-contract.json` at the target Skill root for host promotion. The file has this shape:

```json
{
  "schemaVersion": "1.0",
  "targetRuntime": "controlled-codex-host",
  "mode": "required",
  "gates": [
    {
      "id": "G-001",
      "condition": "Only the approved isolated test target may be written",
      "protectedEffect": "write the isolated test file",
      "protectedAction": "write-file",
      "enforcementEntry": "host.writeProtectedFile",
      "decisionAuthority": "program",
      "decisionProvider": "host-file-policy",
      "bindTo": ["action", "arguments", "target", "state"],
      "freshness": "per-action",
      "failureMode": "deny",
      "alternatePaths": [
        {
          "path": "direct-shell-write",
          "disposition": "disabled",
          "verificationRef": "host-negative-test-001"
        }
      ]
    }
  ]
}
```

`mode` is `required` when the Skill claims a mandatory gate; then `gates` must be nonempty. `mode: none` with `gates: []` is an explicit *claim* of no mandatory gates, not proof that no protected effect exists. The delivery host must review that claim independently. A gate's `decisionAuthority` is `program`, `human`, or `policy`; `decisionProvider` identifies the independent checker or reviewer. `bindTo` must include the action, arguments, target, and current state. `freshness` is `per-action`, and `failureMode` is `deny`. List known alternate paths with a `gated` or `disabled` disposition and a verification reference. The host must independently enumerate and test paths; a complete-looking list in this file cannot establish coverage.

## Host acceptance and runtime checks

Before promotion, the host must run the static validator with `--require-gate-contract`, reject P0/P1 findings, compare the exact package hash to the candidate under review, and verify the contract against its own tool and permission inventory. It must test both the authorized action and bypass attempts for each protected effect. A missing host, incomplete coverage, or unavailable checker blocks `accepted`; the Agent may still deliver a draft or review-required candidate.

At runtime, the host checks each protected action immediately before the effect. It binds the decision to the current action, arguments, target, state, and any relevant artifact hash. Changing any bound input requires another decision. A human or policy decision is valid only if the host can verify its issuer, scope, and freshness. If check and effect cannot be coupled safely, the host must stop or use an atomic operation that keeps the checked state valid through execution.

The first acceptance case for this design is one protected file write in an isolated test project. Passing it qualifies only that effect in that controlled Codex host. Publication, production writes, and other effects need separate path inventories and acceptance evidence.
