# CR-20261111-201 - Source semantics before presentation

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | core-skill-md, references-and-assets, scripts-and-validation, safety-and-governance, downstream-and-handoff |
| Source | PRE-01 approved presentation requirements, AC-018 through AC-021 |
| Baseline | 43456ac371ad65972b86219ee7912d6f61e6247b |
| Author | Codex |
| Related Records | none |

## Summary

Author source semantics before projecting views. Retain source-traced technical
handoff constraints without displaying them as business actions or parameters.

## Context And Problem

A read-only trace of the supplied generator showed an entire baseline bound to
type selection and subsequent data chosen by operation text. Renderers faithfully
projected this mismatch. The agent lacked concrete source-review instructions;
the converter also discarded a separately authored technical_handoff field.

## Sections Changed

| File | Section | Change Summary |
|---|---|---|
| SKILL.md | Interpretation entry | Reach source semantics before authoring/review |
| references/source-semantics.md | Workflow | Goal, checkpoint, field ownership, actual questions, self-check |
| references/batch-contract.md | Input table | Retained technical_handoff claims |
| scripts/authoring.py | Case creation | Preserve technical handoff |
| scripts/scoped_review.py | Projection fields | Keep technical handoff outside business views |
| scripts/test_source_semantics.py | Public APIs | Synthetic dual-entry regression |

## Decision And Alternatives

Reuse existing candidate data_refs, claims, clarification and presentation APIs.
No natural-language action classifier or template full-form expansion was added.
Business interpretation belongs to the agent; deterministic tests prove faithful
projection and retention, not automatic semantic correctness.

## Detailed Change

The operational guide requires goal-bounded preparation, explicit ordinary grouped
entry and separately locatable checks, one effective scenario value, preservation
of dynamic rules, and actual questions for unknown trigger/actor behavior.

## Impact Analysis

Both authoring and scoped review retain technical constraints. Existing business
conditions remain visible. No change to aggregation, Q&A persistence, formal
catalog integration, global installation or business execution is included.

## Validation Evidence

| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| Red | unittest test_source_semantics.py | Failed: technical_handoff absent from converted case | Task tool output, pre01 evidence |
| Green | unittest test_source_semantics.py | 1 test passed after retention/projection fix | Task tool output |
| Regression | unittest discover -s scripts -p test_*.py | 97 passed, including 3 source semantics tests | Task tool output, 34.574 s |
| Skill structure/change records | validate_create_skill.py --require-change-records | Full-package findings: existing test secret-pattern matches, missing legacy headings, command-path parsing; new index section findings corrected | Task evidence; not claimed clean |
| Real multi-turn behavior | Independent executor reads updated Skill and synthetic error fixture | Completed with actual host correction and exact-version review | private dialogue-ac-evidence.md and v5-api-reviewed/readback-verification.json |
| Integration regression | unittest discover -s .agents/skills/test-case-authoring/scripts -p test_*.py | 99 passed after integration with issue 105 | private integration-regression.txt |
| Integration validator | validate_create_skill.py --require-change-records | Same 7 inherited findings, no change-record finding; not clean | private integration-skill-validation.json |
| Integration mirror | Per-file SHA-256 source/distribution comparison | zero mismatches | merger verification |

## Safety And Privacy

Public package contains synthetic examples only. Private source paths/materials
remain outside the repository. No credentials, dependency installation, external
model call, real business mutation, publication or global Skill write performed.

## Risks And Follow-up

Actual multi-turn behavior completed after observed questions and host replies.
Initial missed data questions, scope overreach and adapter failures remain historical
evidence; this was not a clean first pass. The corrected original applied session
was re-presented and explicitly reviewed at version
41b0a60ca9db23da67cb1aadb8224ed74e21efaefb87655d90584b3f175005af.
Public review and disk readback confirm all three simulated cases approved,
not_merged and not_run. No prior-version approval or marker rewrite was used.
Independent review found no blocking source defect and Root released exact
candidate 37500aa473dfeacb8f7b6677b9e860cc2086da13 for local integration.
Inherited validator findings keep the record applied, without host acceptance. XMind client validation belongs to the presentation integration work.
This is a review-required candidate; source self-check is an agent instruction,
not an independently enforced semantic gate. CLI human-view writes remain for PRE-04.

Refs: references/source-semantics.md; scripts/test_source_semantics.py.
