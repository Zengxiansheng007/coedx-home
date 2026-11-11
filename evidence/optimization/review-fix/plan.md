# Final Standards P2 repair plan

Recorded before changing the active request. Scope is the final Standards finding against #79 US-41/42 and AC-012, with #88 cross-material consistency and historical-evidence protection.

## Baseline and cause

- Worker branch is `codex/tpd-opt-review-fix`, HEAD and integration tip are `ba9a7fcaf16ea792275ddb729f956d0d9bc2a651`. The worktree was clean on entry.
- `reviews/final-standards.md` remains the initial independent finding. `reviews/final-spec.md` has no spec findings. Neither report is rewritten.
- `tests/test-point-discovery/writing-request.md` requires a fresh output directory in line 3 but names an existing historical output in line 7 and an ambiguous relative two-chart output in line 9. This leaves two competing completion conditions.
- Original working-copy SHA256 is `75f3cf0e9160a4ec9f9e5ca84aff396dcee53c31b108de69a33ad6d7df1a3cbb` for `writing-demo.md` and `a06d6e5f3a0a3cbb48b82a64480144c9c0a18c2717b6bea758203e150ad85873` for `two-chart-writing-demo.md`.
- The source lookup in the request depends on the original development root. Its actual existing root is `C:/Users/lenovo/Documents/ChatGPT/ui-test/.scratch/tpd-development-20261107`. An isolated worker must receive that source root explicitly.

## Exact write set and reuse

- Product/active change is only `tests/test-point-discovery/writing-request.md`. Use one host-supplied fresh output directory for both named artifacts. Treat the two existing demos and original development evidence as read-only inputs. Make source-root resolution explicit for an isolated checkout.
- New evidence is limited to `evidence/optimization/review-fix/` for this plan, actual actor inputs/replies, readback and hashes, independent-result analysis, static check records and a delta manifest. Root may preserve raw actor evidence outside the worker and it will be copied without changing its content.
- `progress-request.md` reads the historical M1 demo and already restricts writes to `progress-run/`. `xmind-request.md` explicitly keeps D1 as a historical original and requires a new output directory. Neither instructs rewriting these demos, so neither needs a change for this finding.
- Reuse the existing real Skill entry, writing request, fixtures, original per-turn simulated answers and independent writing rubric. Runtime files, helper, examples and historical results remain untouched. No framework, new dependency, global install, downstream invocation, remote mutation or business execution.
- Apply standalone implement-spec, TDD, writing-for-agents/Skill mechanics, create-agent-skill and PowerShell governance. Source standards are README and docs/development/verification.md. The already agreed seam is the natural-language Skill entry. No additional seam approval is needed.

## RED, GREEN and acceptance

1. Before changing source, Root dispatches an isolated actor to read the real entry/request and return a read-only output plan or clarification. It receives an ordinary simulated request, not this plan or expected results. Preserve its actual reply even if it does not reproduce the conflict. No historical file may be overwritten to obtain RED.
2. Repair only the conflicting output instructions and the source-root prerequisite needed to execute that same request in isolation.
3. Root dispatches a new isolated actor using the changed actual request, existing ordinary sources and a distinct fresh output directory under this evidence directory. Observe new M1 and two-chart files and actual readback through the entry. If necessary, the host answers genuine clarification questions in subsequent turns. No prefilled passing transcript or expected artifact is supplied.
4. Read both actual outputs semantically against the original inputs and rubric. Verify their pending-review identities, two independent scopes, explicit source mapping and fresh destinations. Recompute original demo hashes and compare all historical tracked files to baseline. Keywords or file existence alone do not establish behavior.
5. Run required `tools/checks.py` using existing `C:/DevelopTool/Python311/python.exe -X utf8 -B`, with a fresh output directory, plus focused diff/whitespace and runtime identity checks. Keep static results separate from simulated behavior.
6. Preserve the historical 99-file freeze. Add a delta manifest binding the changed request and new evidence with hashes. Commit a clean worker, merge the current integration tip, and report actual commit, evidence, passed/failed/unverified boundaries to Root for independent review and merge.

This repair does not repeat unrelated successful runtime/client/business checks. New XMind client or real business validation is outside this narrow request-routing change.
