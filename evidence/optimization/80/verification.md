# #80 implementation verification

SIMULATION development evidence. This is the implementer's per-AC assessment, pending Root's independent whole-ticket semantic review. Product byte identities for the GREEN execution are frozen in `source-manifest.json`, based on `475b924a753a27437ea22664126b8a00edfe9543` plus this ticket's patch.

## Changed behavior and consistency

The existing Skill entry now routes scoped clear rules directly to reviewable candidates, checks accessible facts, and actually asks about conflict, stale evidence and unknown expectations. The module clarification reference owns detailed input decisions. Optional risks require concrete value, cost and user choice. Scope and expected result remain separate, exclusions retain project applicability, and historical XMind contributes expression only.

Thirteen product documents were updated, including the entry, affected organization references, input/writing templates, planning annotations, XMind guidance, feedback and error-guessing/decision-table examples. The active clarification rubric was updated together with the dedicated natural-language request, fixture and independent rubric. Seven organization schemes were audited, with workflow/lifecycle already delegating clarification to the shared reference. Unchanged shared-rule duplication and full-branch reprint rules remain assigned to later optimization tickets. The two-heading structure remains for #81, while this ticket removes its automatic unknown-to-product classification behavior.

No parser, engineering Skill, global copy, downstream Skill or historical output was changed. No new framework, dependency or semantic validator was added.

## Actual entry execution

Root ran isolated actors with ordinary request and input only. Actor records list actual reads and confirm the plan, issue, diff, rubric and other actors' outputs were excluded. RED and GREEN used the same initial fixture/request and the same second-turn business answer. GREEN then received an actual third-turn answer to the remaining questions. Each reply retains SIMULATION identity, version and pending state.

RED is in `actor-output/red/turn-01.md` and `turn-02.md`, assessed in `red.md`. GREEN is in `actor-output/green/turn-01.md` through `turn-03.md`, with the actual candidate versions `draft-01.md` through `draft-03.md`. Rules were not prefilled as a whole passing session.

| Ticket acceptance | Implementer assessment | Actual semantic evidence |
| --- | --- | --- |
| AC1 clear candidates plus conflict/staleness/unknown questions | Pass for the simulated fixture | GREEN turn-01 asks Q1 name40 versus observed20, Q2 overlength and Q3 stale retention. draft-01 directly writes P1/P2 candidates without querying every known rule. turn-02 adopts only actual name/retention answers, leaving overlength unanswered. |
| AC2 historical XMind expression only | Pass for supplied historical excerpts | GREEN draft-01 and draft-03 explanation maps H1/H2 to organization-only reference, excludes historical15, blur truncation and typo rules, and confines readability to format. No real parser or client operation is claimed. |
| AC3 derived checks versus optional risk choices | Pass for the simulated fixture | GREEN draft-01 directly derives required/format/unique checks from P1/P2. turn-01 Q4/Q5 give concrete duplicate-record/content-exposure risks, value, extra preparation/clarification cost and user choices. Neither S1 nor S2 is a draft-01 body check before adoption. draft-02/03 exclude rejected permissions. |
| AC4 risk adoption distinct from correct outcome | Pass for the actual second/third turns | GREEN turn-02 records Q4 as scope adoption, creates Q6 and asks both requests' feedback and final record expectations. draft-02 holds only an unknown marker. Only after turn-03's actual answer does draft-03 express one success, duplicate refusal and the single successful draft/name. |
| AC5 exclusions remain project-scoped | Pass for the simulated fixture | GREEN turn-01 and draft-01 preserve existing upload exclusion without reopening it. turn-02 and draft-03 preserve permissions rejection and upload exclusion, explicitly retain project applicability and ask neither excluded capability's details. |
| AC6 reviewable candidates and concentrated source/decision identity | Pass for the simulated fixture | Every GREEN draft has concentrated P1–P4/O1/H1–H2/S1–S2 mappings and actual simulated answer provenance. Known rules form candidates in draft-01, remaining rules form draft-03 after actual answers with no new questionnaire. turn-03 stops pending concrete review and creates no accurate baseline. |

## Executed checks

- `git diff --check` passed after the source edits.
- Existing `tools/verification/skill_format.py skills/test-point-discovery` passed with exit0. The aggregate repository entry does not include this separate Skill, so this check was run explicitly.
- Mandatory `tools/checks.py --output-dir evidence/optimization/80/checks` initially failed in the sandbox. Existing workflow tests encountered44 errors and verification tests4 errors, each at temporary-file `os.replace` with WinError5. Dependencies, authoring, format, registry and copies passed. Full records remain unchanged under `checks/`.
- The same aggregate entry was rerun outside the sandbox with an independent output path `checks-unsandboxed/`. Exit0, all seven stages passed. Actual suites ran67 workflow tests,8 verification tests and94 authoring tests. Full records and hashes are in `checks-unsandboxed/summary.json`.
- No product/test workaround was made for sandbox permissions. The controlled runner automatically recorded the initial failure. A separate redacted incident records read-only diagnostic path/timing mistakes and their corrected reads.

## Limits and next step

The semantic results are a simulated maintenance-module sample, including clear parts of a mixed PRD and the fully answered final candidate. An entirely clear PRD as a separate first-turn sample was not independently run. Historical XMind was provided as text excerpts. Native parser behavior, real XMind client import/edit/return and real business acceptance are outside this run. Prior parser code is unchanged.

Parent-spec behaviors owned by #81–#88 are not declared complete. Root's independent semantic review and local merger remain the next steps. Temporary `.codex/powershell-failures` diagnostics remain untracked by Root instruction and will be archived outside the repository before cleanup. Product, requests and ticket evidence are committed together.
