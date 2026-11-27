# CR-20261127-071 · Selected suite routing

| Field | Value |
|---|---|
| Status | applied |
| Baseline | 4be027b |
| Target Skill | ask-test |
| Source | UI-TEST #71, parent #57 |

## Summary

Read the selected suite catalog for explicit navigation advice while preserving authoring routes.

## Context And Problem

New capabilities must be discoverable by both consumers with one catalog entry.

## Sections Changed

core-skill-md, downstream-and-handoff.

## Decision And Alternatives

Keep the execution policy in the main workflow and the explicit consultation policy in the advisor. Reuse the selected installation's JSON catalog.

## Detailed Change

Read the selected suite catalog for explicit navigation advice while preserving authoring routes. The workflow entry participates in consultation only. The existing authoring map remains available when a UI suite is missing.

## Impact Analysis

Old Packet callers retain compatible child names. Public navigation selects the canonical Skill. Additional capability entries require no consumer dispatch change.

## Validation Evidence

Ticket evidence under p57-evidence/71 includes CLI success and refusal receipts, historical routing tests and the isolated revision-stamp delivery.

## Safety And Privacy

Only controlled offline inputs are used. The consultation reads the catalog as data.

## Risks And Follow-up

Integrated catalog completeness and host-level discovery are checked under #74.
