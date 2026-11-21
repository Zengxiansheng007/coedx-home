# CR-20261119-001 - Use Codex for the guided entry default

| Field | Value |
|---|---|
| Status | validated |
| Target Skill | research |
| Scope | Workspace candidate |

## Summary

Use Codex for the guided entry default.

## Context And Problem

Direct guided entry previously selected Claude by default. The user confirmed that guided research should default to Codex and Claude should require explicit selection. Generic research keeps its AnySearch default.

## Sections Changed

Router instructions, handoff and runtime contracts, CLI state persistence, route selection and offline regression tests.

## Decision And Alternatives

Keep one shared research workflow and select an executor by entry and actual user instruction. Preserve the strong gate, the user-confirmed light exception and the existing AnySearch fallback rules.

## Impact Analysis

Generic requests retain AnySearch. Direct guided entry uses Codex. Legacy tasks that got Claude implicitly adopt Codex at the next handoff or provider-unspecified resume, advance generation and retain source provenance. Completed research and explicit Claude choices retain their recorded executor.

## Validation Evidence

The workspace baseline at `<workspace>/research-guided-codex-default-20261119/baseline-sha256.tsv` records the SHA-256 of each file before changes. Readback matched that baseline for the installed files.

The offline router suite passed all 42 tests. It covered the public CLI entries, legacy route persistence, receipt generation checks, AnySearch fallback, explicit provider selection and existing permission/no-fallback boundaries. Package validation reported zero P0/P1/P2 findings. The sensitive scan reported zero findings.

Live search, adapter canaries and installation were outside this offline validation.

## Safety And Privacy

This candidate uses the existing public-source and restricted-data boundaries. Validation uses offline fixtures and mocks.

## Risks And Follow-up

Live provider availability and global installation require independent evidence. The authoritative installation status comes from its release receipt.
