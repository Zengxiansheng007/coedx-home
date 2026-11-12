# Frozen synthetic feedback artifact

`legacy-review-294a12a.json` contains the exact candidate and Markdown returned by
public `build_scoped_review` at commit 294a12a69b72cc42af68255a64caafb75a0bfa98.
The independent old checkout emitted it once from the synthetic catalog fixture
with two cases sharing data and formal rule/audit/history collections. It is a
regression input for `scripts/test_legacy_feedback.py`; never regenerate it with
the current renderer. It contains no private requirement or real business input.

The old artifact is intentionally audit-heavy. New rendering is tested separately
for clean effective rules, while old returns retain exact scalar binding and
reject changed audits, topology, identities, versions and inconsistent data.
