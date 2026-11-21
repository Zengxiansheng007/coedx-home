# Skill Artifact Contract

Use this contract when delivering a skill package or review result.

## Required Package Files

```text
skill-name/
  SKILL.md
  agents/openai.yaml
```

Optional files must be justified:

```text
references/
scripts/
assets/
gate-contract.json
```

`gate-contract.json` is required when the Skill is submitted to a trusted host for promotion, including an explicit `mode: none` claim when no mandatory gates are declared. Read [the mandatory gate contract](mandatory-gate-contract.md) before authoring it. The package is never its own acceptance authority.

## Report Contract

When producing a report, prefer Chinese HTML with embedded JSON:

```html
<script type="application/json" id="skill-evidence">
{
  "skill": "skill-name",
  "status": "validated-candidate",
  "findings": [],
  "validatedCommands": [],
  "openRisks": []
}
</script>
```

## Adoption Status

Agent-generated reports and the local validator may use only candidate states:

- `draft`: files generated but not validated;
- `review-required`: human review needed before use;
- `sandbox-only`: can only be tested in isolation;
- `validated-candidate`: local P0/P1 checks passed, but host enforcement and acceptance remain unverified;
- `rejected`: unsafe or structurally unsuitable;
- `rerun`: structure is invalid or evidence is incomplete.

`accepted` is a host-issued result only. The host must retain its receipt outside Agent-writable package and report paths, bind it to the exact package and verified runtime/effect scope, and control installation. Older `accepted-with-constraints` or `accepted` labels in Agent-authored reports are historical claims, not current authorization.

## Evidence Checklist

- Source requirement or brief path.
- Skill folder path.
- Frontmatter status.
- File inventory.
- Link/resource validation.
- Script test result.
- Secret scan result.
- Forward-test prompt and result.
- Known limitations.
- Gate contract mode and static findings, when host promotion is requested.
- Trusted host receipt reference and verified effect scope, if the host actually issued one; otherwise state that acceptance is pending.
