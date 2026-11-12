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

## 2026-11-12 F-110-01 repair follow-up

Repair baseline: 46a2a2b6bf35155429eaeb9b92a985b94be76176, isolated codex/tca-qa110-repair. The earlier candidate and review evidence remain frozen. Independent review demonstrated that start_feedback could introduce a new question using a prior stage ID, producing a second permanent Q1-A1 anchor. Existing append_questions and start_extension correctly rejected that collision.

The existing qa_record admission check now covers explicit start_feedback questions as well as append_questions. Only new feedback IDs are checked against retained stages; current-stage questions continue through the existing history-preserving feedback adapter. Omitted questions still retain the current graph. No new recovery system, replay rewriting, external effects or stage approval is introduced. The existing qa-record-contract already requires unique new-stage IDs and remains applicable without changing instructions.

Public persistence regression first failed with ValueError not raised, then passed after the admission correction. Seven recovery checks pass, including all three admission paths, byte-identical MD after rejection, valid new IDs, current-question reopening, A1/A2/A3 history and fresh replay. The full 137-test suite passes (27.929 seconds). A separate follow-up test initially used a P0 fixture without the required scoped feedback baseline; its failure is retained, and the fixture was corrected to use the existing public scoped input without changing production logic.

Actual historical QA108 and QA109 MD records replay to their original candidates and retain their byte hashes; all 73 source/mirror files match. create-skill --require-change-records remains rejected with the same seven inherited findings (3 P0 negative credential fixtures, 3 P1 structure/resource findings, 1 P2 description); no new finding and no clean scanner claim. New code and test changes contain only simulated data. Private repair-red, repair-green-initial, repair-green, repair-green-final, repair-full, repair-validator and repair-compatibility evidence stays outside the package.

Status remains applied/review-required. Independent repair review, latest PRE04 composition and actual six-entry/fresh-context/fault dialogue remain Root-owned pending work; these regression fixtures are not actual conversation acceptance. Existing invalid historical records are preserved for review, not automatically rewritten or migrated.

Pre-review cross-stage check: a later checkpoint must allow source bindings to an earlier stage's permanent Q ID. Added a failing public-stage checkpoint assertion, then extended lookup to retained prior stages. The five targeted recovery tests pass after this one-line correction. No independent review or behavior acceptance had started; earlier 135-test full result and failures remain historical. Actual QA108/109 records replay unchanged with exact candidate equality; 73 mirrored files match. Structure validation retains the same seven inherited findings (3 P0 negative credential fixtures, 3 P1, 1 P2), not a clean pass.


## Local integration independent repair evidence - 2026-11-12

Frozen source bbea7c9351c85a3057cba4de0568411c090ac5bf passed independent
F-110-01 re-review. append_questions, explicit start_feedback and start_extension
reject prior-stage IDs without MD mutation; fresh IDs succeed. Existing current
questions retain A1/A2/A3 and unique anchors; omitted feedback questions and disk
replay remain valid. Original P0 Q1-A1 is unique and prior history unchanged.
Evidence: external review-qa110.md and qa110/re-review-fixed/run3/result.json.
Earlier probe failures and collision evidence remain unchanged.

Only the repair is accepted. Whole-ticket behavior remains pending: latest
PRE04 composition, six-entry interaction, fresh-context stage continuation,
actual save failure and source inconsistency must be observed by Root on the
combined candidate. Public regression or this merge does not establish those
acceptance results. No global install, business execution or publication.


## Actual combined behavior and final verification - 2026-11-12

Root released this metadata registration after the independent final Spec review
closed all 10 agreed issue-110 simulation ACs with zero new Spec findings.
The reviewed product is 6d6c88e49e194967b87a7d11020db313c70bf7c8; its comment-only
delta from c3eeef7135460d89b7d118e87ec3251e4f9f9625 has verified AST/token
equivalence and independent STD-01 closure, with zero remaining new Standards
findings. This entry explicitly supersedes earlier whole-ticket behavior/review
pending statements for the observed synthetic scope. All original records stay.

Three actual actors covered P0, report reconciliation, P1/P2 and review. Two
fresh-context resumptions used the same Q&A and actual candidate/source files.
Six decision entries were exercised, including partial/unknown follow-up,
provisional conditions, omitted coverage, scope/priority, feedback and recovery.
The host sent replies only after actual questions or complete candidate display;
summary confirmation and exact-version final review remained separate.

The first save-lock injection was ineffective and is retained as such. The
second caused a real local WinError5 during record_note; Q&A bytes stayed
unchanged and the actor stopped before review or downstream artifacts. After
the owned handle was released, disk reread preceded one missing note/review/
checkpoint; no repeated P0 summary application occurred. Later same-version
candidate tampering and a changed source were both detected. Recovery preserved
the originals and unrelated decisions, clarified only the affected priority and
existing unanswered state question, then applied one confirmed feedback round
and one separately approved final review.

Independent public read_record/resume_record exited successfully: 58 events,
15 unique answer anchors, entire final candidate equal to Q&A replay, Q&A bytes
unchanged by inspection, final conflicts empty and checkpoint present. Exact
version 3fec851c420c882f88d46bca7d3e77e15c31d62c76484cd623f19ae05cc0a591 has
two approved/not_run/not_merged cases. The original full P0 scope remains one
case; extension approval does not replace that baseline. No human-view file was
created. Earlier unapproved stage wording, failed injection and conflict files
remain available rather than rewritten as successes.

Remaining sample limits: provisional option/default conditions still require
product confirmation; a navigation path is unknown under explicit write-first
authorization; exclusions and downstream deferral remain in coverage. This is
not execution readiness, a new XMind client import, real business evidence,
formal synchronization, global installation or external publication.

Reuse completed seven-stage repository checks: dependencies, workflow (67),
verification (8), authoring (146), format, registry and copies; 221 tests total.
The metadata-only registration does not rerun them. Existing protection evidence
reports 55 protected files unchanged, and 79 source/package pairs agree. Normal
create-skill scanning remains rejected with seven inherited findings; the extra
host-gate scan remains rejected with eight including the missing promotion gate.
Neither scanner result is relabelled passed. CR status stays applied, not host
accepted, and no additional installation or promotion authority is inferred.

External evidence locations, relative to the local task root outside this repo:
- evidence/qa110/fresh-context-host-observations.md
- evidence/qa110/save-lock-r1-host.json and save-lock-r2-host.json
- test-output/qa110-dialogue/actual-trajectory.md and actor-b-observations.md
- test-output/qa110-dialogue/resume-c-actual-trajectory-and-evidence.json
- evidence/qa110/final-review/acceptance.md and final-inspection.json
- evidence/final-spec.md, final-standards.md and final-checks-and-protection.md

Only generic synthetic results and external references are registered here;
the original Q&A, source materials, reports and private inputs are not packaged.
