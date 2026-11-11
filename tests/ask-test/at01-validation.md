# AT-01 validation record

Baseline: 1200dbbcdbc94458c411b7aa7b702fe2a703fb41; issue100; spec v0.1.
Before implementation: request, independent rubric and fictional materials authored first. Baseline has no `.agents/skills/ask-test/SKILL.md`; entry load is impossible (structural RED, not a behavioral failure run). Actual actor RED/GREEN, supplemental dialogue, read-only action observation and host trigger behavior remain pending Root execution. No fabricated results.

Allowed write set: new `.agents/skills/ask-test/` and `tests/ask-test/`. Existing skills, business materials, global install, external models and remote writes excluded. Candidate only; instructions and metadata are not host enforcement.

Root subsequently ran a fresh RED actor against the actual missing entry and reported that the actor stopped rather than substituting another Skill; Root owns the actual transcript. Implementation started only after that notification.

Implementation sources read: current installed test-point-discovery SKILL.md (PRD required, existing planning/clarification reusable, specific review separate); repository test-case-authoring SKILL.md (complete handwritten/recorded P0, review/merge/execution independent); repository ask-matt invocation policy. These are evidence for implementation, not evidence of downstream execution.

Local checks: create-skill validator returned exit 0, P0=0/P1=0/P2=1 (generic trigger wording warning: intentionally explicit manual invocation rather than autonomous trigger phrasing). Repository skill_format.py initially failed under default GBK decoding; rerunning with Python `-X utf8 -B` passed. No validator/source workaround was applied. This validates structure, references and the validator's secret patterns, not behavior or host enforcement. Actual multi-turn GREEN and independent review remain pending Root orchestration.
