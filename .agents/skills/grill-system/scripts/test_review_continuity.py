"""Contract and existing-runtime regression tests; no semantic inference is claimed."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from grill_session_runtime import close_session, create_checkpoint, reconcile_format_only_drift, reopen_question, render_report
from test_grill_phase_contract import configured_ledger, closure
from validate_grill_report import extract_session

ROOT = Path(__file__).resolve().parents[1]

class ReviewContinuityTests(unittest.TestCase):
    def test_contract_and_all_routing_cases_are_present(self):
        text = (ROOT / "references/review-continuity.md").read_text(encoding="utf-8")
        for required in ("substantive-requirement-change", "evidenced-conflict", "new-major-risk", "Whole-review reopening is exceptional", "explicit user agreement", "consumed writeback batch", "does not automate"):
            self.assertIn(required, text)
        fixtures = json.loads((ROOT / "assets/fixtures/review-continuity.json").read_text(encoding="utf-8"))
        self.assertEqual(len(fixtures["cases"]), 12)
        actual = {x["id"]: x["expected"] for x in fixtures["cases"]}
        self.assertEqual(actual["FORMAT-MD-JSON"], "validate-without-reopen")
        self.assertEqual(actual["TECHNICAL-GATE"], "separate-qualification")
        self.assertEqual(actual["WHOLE-REVIEW"], "explicit-user-scope-required")
        self.assertEqual(actual["FORMAT-LABEL-WITH-MEANING-CHANGE"], "targeted-reopen")
        for path in ("SKILL.md", "references/routing-policy.md", "references/grill-session-contract.md", "references/phase-boundary-contract.md", "references/downstream-skill-map.md"):
            self.assertIn("review-continuity.md", (ROOT / path).read_text(encoding="utf-8"))

    def test_format_reconciliation_preserves_every_review_state(self):
        for phase, result in (("review-ended", "ready-for-writeback"), ("writeback-complete", "completed")):
            with self.subTest(phase=phase), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                ledger, target = configured_ledger(root)
                close_session(ledger, closure())
                ledger["phase"], ledger["result"] = phase, result
                create_checkpoint(ledger, root, "CP-BASE")
                keys = ("phase", "result", "questions", "decisions", "effectiveDecisions", "closureEvidence", "writebackReceipts", "writebackPolicy")
                before = {key: copy.deepcopy(ledger[key]) for key in keys}
                target.write_text("before\n", encoding="utf-8")  # Real format-only byte change, not changed requirements.
                reconcile_format_only_drift(ledger, root, "CP-BASE", "CP-FORMAT", "reviewer verified trailing newline only", [])
                self.assertEqual(before, {key: ledger[key] for key in keys})
                report = root / "report.html"
                ledger["processArtifacts"].append({"kind": "report", "path": str(report)})
                render_report(ledger, report)
                projected, _ = extract_session(report)
                self.assertEqual(projected, ledger)

    def test_targeted_reopen_does_not_reset_unrelated_decisions_or_history(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger, _ = configured_ledger(Path(directory))
            unrelated = copy.deepcopy(ledger["questions"][0])  # Separate question histories must not share a mutable list.
            unrelated.update(id="Q-002", severity="P1")
            ledger["questions"].append(unrelated)
            ledger["decisions"] = [
                {"id": "D-001", "sourceQuestion": "Q-001", "status": "effective"},
                {"id": "D-002", "sourceQuestion": "Q-002", "status": "effective"}
            ]
            ledger["effectiveDecisions"] = ["D-001", "D-002"]
            close_session(ledger, closure())
            prior_closure = copy.deepcopy(ledger["closureEvidence"])
            prior_question = copy.deepcopy(unrelated)
            reopen_question(ledger, "Q-001", "evidenced-conflict: approved scope contradicts new source E-002", "E-002")
            self.assertEqual(ledger["questions"][1], prior_question)
            self.assertEqual(ledger["decisions"][1]["status"], "effective")
            self.assertEqual(ledger["effectiveDecisions"], ["D-002"])
            self.assertEqual(ledger["closureEvidence"], prior_closure)
            self.assertEqual(len(ledger["questions"][0]["reopenHistory"]), 1)

if __name__ == "__main__":
    unittest.main(verbosity=2)
