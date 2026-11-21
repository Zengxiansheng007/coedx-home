# CR-20261119-002 - Default to Codex and retain explicit Claude retrieval

| Field | Value |
|---|---|
| Status | validated |
| Target Skill | research-guided |
| Scope | Workspace candidate |

## Summary

Default to Codex and retain explicit Claude retrieval.

## Context And Problem

Direct guided entry previously selected Claude by default. The user confirmed that guided research should default to Codex and Claude should require explicit selection. Generic research keeps its AnySearch default.

## Sections Changed

Skill description and workflow, UI metadata, entry and quality references, validator expectations, and a Claude-specific reference containing the original adapter gates.

## Decision And Alternatives

Keep one shared research workflow and select an executor by entry and actual user instruction. Preserve the strong gate, the user-confirmed light exception and the existing AnySearch fallback rules.

## Impact Analysis

Codex uses current host search and page-reading with existing source and claim review. The selected executor can perform one targeted reinforcement round. Claude retains its existing adapter, preflight, schema and failure behavior after an explicit choice.

## Validation Evidence

The workspace baseline at `<workspace>/research-guided-codex-default-20261119/baseline-sha256.tsv` records the SHA-256 of each file before changes. Readback matched that baseline for the installed files.

Package validation reported zero P0/P1/P2 findings and the Skill validator suite passed. The Claude repair and adapter suites passed 26 and 32 checks respectively. Registry drift and sensitive scans reported zero findings. The sibling router's 42 offline tests passed.

Live search, adapter canaries and installation were outside this offline validation.

## Safety And Privacy

This candidate uses the existing public-source and restricted-data boundaries. Validation uses offline fixtures and mocks.

## Risks And Follow-up

Live provider availability and global installation require independent evidence. The authoritative installation status comes from its release receipt.
