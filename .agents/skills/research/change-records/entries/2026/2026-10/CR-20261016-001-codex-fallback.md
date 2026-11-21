# CR-20261016-001 - Automatic Codex fallback

| Field | Value |
|---|---|
| Status | validated |
| Target Skill | research |
| Author | Codex |
| Scope | local update |

## Summary

Default AnySearch service failures use Codex with evidence continuity.

## Context And Problem

User confirmed A/A decisions and local implementation on 2026-10-16.

## Sections Changed

research runtime/boundary/tests, entrypoint/metadata/references and necessary guided entry compatibility.

## Decision And Alternatives

Switch once to Codex on service failure. Preserve explicit choices, no-fallback, permission and security boundaries.

## Impact Analysis

Generic automatic routing changes. Explicit Claude/Codex and standalone guided defaults retain their behavior.

## Validation Evidence

Offline injected-transport runtime suite and package validators are recorded in the local deployment receipt. No live provider call.

## Safety And Privacy

No key values, raw exception text or private data added. Backups and baseline hashes precede installation.

## Risks And Follow-up

Host must actually execute Codex search/read tools and inspect evidence. Offline tests cannot establish live service availability.
