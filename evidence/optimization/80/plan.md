# #80 implementation plan

SIMULATION development only. Baseline `475b924a753a27437ea22664126b8a00edfe9543`, branch `codex/tpd-opt-80`. Product source is `skills/test-point-discovery`, isolated from global and downstream copies.

## Sources and applicability

Read optimization inputs issue-79 and issue-80, confirmed 优化开发规格-v0.1 and 优化细节设计-v0.1 sections 1–2, repository README and docs/development/verification.md. Reuse the established real Skill natural-language entry and turn-by-turn simulated replies. TDD, writing-for-agents and create-agent-skill apply independently of develop-system.

## Baseline issue and write set

Entry step 6 requires clarification before step 8 writing. There is no explicit path for an unambiguous PRD to produce candidates without re-asking every known rule. module-clarification distinguishes sources and preserves exclusions, but automatically labels unknown expectations product questions after scope inclusion. information-maintenance says to retain page conflicts as product questions instead of requiring an actual question. dashboard-intake template categorizes business unknowns as product questions. xmind-feedback covers feedback authority but lacks explicit historical organization-only reference treatment.

Expected writes are the entry, directly affected source/clarification/maintenance/writing/XMind references, active request/rubric guidance and a concise worked reference example if needed. Audit all seven organization references for this ticket's contradictions. Other ticket behavior, historical result files, scripts and parser are preserved.

## Acceptance and verification

Issue #80 AC1–6 cover direct known-rule candidates, questions on conflict/staleness/unknown result, historical XMind as expression-only, derived checks versus optional risks, scope versus expected result, project-scoped exclusion, and concentrated source/decision provenance.

Before product edits Root runs `tests/test-point-discovery/optimization-80-request.md` against this baseline. Actor receives only ordinary request and fixture, with no rubric or plan. Save every actual reply and follow-up with SIMULATION identity. RED is an observed semantic failure, distinct from static contradictory-rule evidence. Then minimally change the affected instructions, rerun the same entry on the updated source with an independent actor, inspect candidates and follow-up handling against each AC, and obtain independent semantic review. If an AC has no behavior observation report unverified.

Use existing Python at C:/DevelopTool/Python311/python.exe and existing PyYAML, no installation. Mandatory final `python -X utf8 -B tools/checks.py` verifies repository checks only. Run the existing native reader unit tests if the untouched parser's compatibility is implicated. Git diff checking and semantic source audit support consistency, not behavior. No real XMind client or business execution is claimed.

## Reuse and accounting

Reuse existing fixtures/request patterns, source mapping in the same MD, and independent review. No new validator/framework or helper. One ticket cycle starts here, with RED pending. Project numerical development caps are cancelled under existing authority, no model/business/global/remote writes authorized. Actual validations and final evidence will be recorded beside this plan.
