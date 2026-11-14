# CR-20261114-001 - Module handoff partition

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | changed |
| Scope | core-skill-md / references-and-assets / scripts-and-validation / downstream-and-handoff |
| Source | #113; REQ-015-016; AC-023-024 |
| Baseline | 3b9cb992db1211e9a5c08f0e40a43ac6cb6cfa7c |

## Summary

Generate one instruction branch per direct-owner semantic module path. Keep explicit technical handoff and process detail separate from business steps; retain business validity and provisional rules. Shared human/tree projection preserves complete candidate inputs. Source labels and numeric lines point to the same-version candidate without exposing raw internal source paths. Opaque legacy technical text remains internal with an explicit read-before-execution obligation.

## Context And Problem

Technical provenance was hidden while process details repeated in business prose.

## Sections Changed

scoped_review.py, aggregation.py, feedback.py, module_handoff.py, public tests, SKILL.md and linked contract.

## Decision And Alternatives

Explicit semantic classification prevents accidentally moving business validity. No heuristic text classifier.

## Impact Analysis

All existing render entry points share the projection; feedback retains historical version bindings.

## Validation Evidence

Public render/feedback TDD first failed with zero instruction branches instead of two, then passed. Initial full regression found generated title collisions and old-layout/status normalization problems; fixed distinct instruction applicability headings, exact historical layout reconstruction and trusted same-version review-status normalization. Chat case-heading count remains unchanged. Recording/handwriting equivalence still compares every business line, excluding the newly intentional source/version instruction differences.

Added synthetic parent/child ownership, complete-path isolation, original candidate retention, markdown unchanged return, ambiguous instruction modification and native unchanged return tests. All 149 tests passed. No true business rules confirmed. Actual XMind client integration is unverified and belongs to RR07. Skill validator initially found record-format omissions, repaired before delivery; inherited seven scanner findings remain (three synthetic credential fixture patterns, description/section heuristics and a command interpreted as a resource path).

## Safety And Privacy

No install, push, global Skill change, real model call, business execution or formal asset change. Existing credential admission remains in effect. Semantic classification relies on explicit Agent-authored technical_handoff; ambiguous legacy fields remain business content pending clarification. Local validation is not acceptance or runtime authority.

## Risks And Follow-up

Independent semantic review and actual XMind client validation remain pending. This ticket does not implement step reuse or title changes.
