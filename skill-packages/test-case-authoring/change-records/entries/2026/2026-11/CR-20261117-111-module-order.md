# CR-20261117-111 - Chat scope provenance

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | references-and-assets / scripts-and-validation / downstream-and-handoff |
| Source | Actual public chat acceptance defect; #134 / #138 / #140 / #141 |
| Baseline | 38f16d27b390c9394d5e420fce4e33a2469a21ab |
| Author | Codex |
| Related Records | CR-20261117-110 |

## Summary

Order each module as common preconditions, existing business groups/cases, then common postconditions.

## Context And Problem

Actual #141 review requested this display order. Projection appended definitions after the first business group; chat prepended all definitions before case prose.

## Sections Changed

Aggregation, scoped human projection, public tests and chat delivery reference; both distributions identical.

## Decision And Alternatives

Stable semantic buckets preserve original order inside each category. Case prose is bound by stable source identity, not parsed titles. Do not patch generated review files.

## Detailed Change

Shared definitions retain source origins and exact generated identity during feedback matching, permitting previous insertion-order exports. No empty post definition is created. Legacy layout paths retain prior placement semantics.

## Impact Analysis

Display only: preserve candidate cases, data, membership, exceptions and approval. Current draft review remains pending.

## Validation Evidence

Public red test reproduced preparation after business group. Targeted 25 tests passed, including post ordering with excluded cases; 8 aggregation tests passed with old-order no-edit and actual shared-edit feedback. Required checks recorded in external task evidence.

## Safety And Privacy

Synthetic tests only. No private source material, global install, remote writes or business execution.

## Risks And Follow-up

Candidate pending independent review and fresh generation; no actual draft approval is inferred.

Refs: #134, #138, #140, #141.
