# Skill Brief Template

Use this template before writing or changing files when the user's request is vague, high-risk, or broad.

## Required Fields

| Field | Question | Completion criterion |
|---|---|---|
| Objective | What repeated task should the skill make more reliable? | One sentence that names the work. |
| Trigger wording | What would users say when they need this skill? | At least 3 realistic trigger phrases or a reason why one phrase is enough. |
| Inputs | What files, links, systems, docs, credentials, or context are needed? | Inputs are named without embedding secrets. |
| Outputs | What should the skill produce or change? | Output format and location are explicit. |
| Success criteria | How can another agent know the skill worked? | Observable validation exists. |
| Safety boundary | What must the skill refuse, avoid, or ask before doing? | High-risk actions are listed. |
| Runtime assumptions | Which tools, APIs, OS, shell, models, or plugins are required? | Unknown dependencies are marked. |
| Protected effects | Which file, network, account, or other side effects require a hard gate? | Name the exact effect and target; do not infer universal coverage. |
| Mandatory conditions | Which conditions must hold before delivery or each protected action? | Separate deterministic checks from independent human/policy decisions. |
| Enforcement owner | Which trusted host entry controls each protected effect and target permission? | Agent-run scripts and reports are candidate evidence only. |
| Alternate paths | Can shell, file tools, MCP, APIs, or credentials reach the same effect? | Enumerate each path for host verification or disable it. |
| Gate evidence | What binds a decision to the current action, arguments, target, state, and package bytes? | Missing, stale, or inconclusive evidence blocks. |

## Classification

Pick the smallest useful type:

- `steps-only`: ordered operational workflow;
- `reference-only`: reusable vocabulary, policy, or rubric;
- `mixed`: workflow plus detailed reference;
- `tool-integration`: wraps APIs, CLIs, MCP, browser, or apps;
- `asset-template`: produces artifacts from bundled templates;
- `router`: points users or agents to other skills;
- `handoff`: preserves cross-session state.

## Resource Decision

- Use `SKILL.md` for core workflow and non-negotiable rules.
- Use `references/` for long examples, schemas, rubrics, and variants.
- Use `scripts/` for deterministic parsing, validation, generation, or repeated command construction.
- Use `assets/` only for files copied or transformed into outputs.
- Do not create resource folders "just in case."
