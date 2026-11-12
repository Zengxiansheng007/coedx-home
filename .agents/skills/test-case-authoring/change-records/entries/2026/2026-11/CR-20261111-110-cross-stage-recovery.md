# CR-20261111-110 - Cross-stage recovery from the sole task Markdown

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | changed |
| Scope | core-skill-md / references-and-assets / scripts-and-validation |
| Source | Issue 110; questioning REQ-006/007, AC-010/011/012 |
| Baseline | fe5f1727f166fd8252c751f871780e281ff9582d |
| Author | Codex |
| Related Records | CR-20261111-105, CR-20261111-108, CR-20261111-109 |

## Summary

Reuse the existing Markdown event adapter to retain prior stages, checkpoint actual candidate/source identities and resume from disk. Preserve existing clarification, coverage, feedback and full P0 extension gates.

## Context And Problem

The existing adapter replayed a single candidate and feedback but could not append an extension candidate or compare the actual current candidate/source files on a fresh-context recovery. Version labels alone cannot identify conflicting technical content.

## Sections Changed

SKILL.md recovery pointer; references/qa-record-contract.md concrete stage and source checks; scripts/qa_record.py checkpoint_record/resume_record and start_extension; scripts/test_recovery.py public regressions. Same-file events remain the only answer source.

## Decision And Alternatives

Reuse record_context for metadata and existing build_extension for the stage transition. Store no parallel recovery ledger. Retain old event bytes/answers and derived prior_stages, reserve old question anchors, and require the Agent to interpret actual source differences and dependent scope. Do not copy foreign requirements/module approval gates.

## Detailed Change

Checkpoints read real source files and the candidate, requiring complete equality with the existing MD projection. Resume reads these files again and reports source/candidate gaps without overwriting either input. Extension transition rechecks the existing P0 gate and preserves old questions; feedback retains that history. Write failures propagate with attempted payload/action/path for honest unsaved-content reporting.

## Impact Analysis

Existing records replay without migration. Existing pure APIs and approval boundaries stay intact. Recovery diagnostics do not grant execution, merge, publication or real business acceptance; source-change semantics and independent scope remain Agent responsibilities.

## Validation Evidence

Two red/green slices: missing recovery API; unsupported start_extension. Five new public regressions passed, then 135 full standard-library tests passed (30.627 seconds). Evidence in private qa110 task folder. Six-entry actual conversation, fresh-context recovery and independent review are pending and must be reported separately; test fixtures are simulated, not dialogue transcripts.

## Safety And Privacy

No external calls, dependency install, global writes or business execution. Existing credential guard checks event payloads. Private requirements/transcripts stay outside package. Structure scanner results are reported separately, including inherited findings.

## Risks And Follow-up

Candidate only. A byte difference identifies a review need, not its business meaning. Legacy records require actual source/candidate inspection before their first checkpoint. Source/MD conflicts are not silently repaired. The workflow is not an OS enforcement boundary. Root owns real six-entry and fresh-context validation.

Refs: https://github.com/Zengxiansheng007/coedx-home/issues/110

Pre-review cross-stage check: a later checkpoint must allow source bindings to an earlier stage's permanent Q ID. Added a failing public-stage checkpoint assertion, then extended lookup to retained prior stages. The five targeted recovery tests pass after this one-line correction. No independent review or behavior acceptance had started; earlier 135-test full result and failures remain historical. Actual QA108/109 records replay unchanged with exact candidate equality; 73 mirrored files match. Structure validation retains the same seven inherited findings (3 P0 negative credential fixtures, 3 P1, 1 P2), not a clean pass.
