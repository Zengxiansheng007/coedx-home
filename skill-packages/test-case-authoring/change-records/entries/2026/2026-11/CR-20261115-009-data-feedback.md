# CR-20261115-009: materialize data feedback consumers

- Baseline: 66df0b444fd8a121e42c76803ea3018ebe23cafb.
- Request: #117 independent review semantic-04-05; REQ-021 / AC-030.
- Category: scripts-and-validation. Status: candidate, independent review required.
- Before: agreed data/value edits left frozen reference bindings and failed validation.
- After: resolve affected whole steps before changing current data; refresh their target digests afterward. Explicit shared identities affect their consumers; separate dynamic bindings retain exact case scope.
- Files: scripts/local_step_feedback.py, scripts/feedback.py, scripts/test_local_step_feedback.py.
- Unchanged: frozen definitions, source P0 and historical input snapshots; existing confirmation and review gates.
- Validation: regression reproduced binding-change exception before implementation; 22 targeted tests passed after fix. Added separate dynamic-binding isolation coverage. Final full-suite result reported in external rr05-fix evidence.
- Sensitive data: synthetic fixtures only; no credentials or business execution.
- Limitations: no real client or business acceptance, no installation or publication. Existing validator baseline limitations remain.
