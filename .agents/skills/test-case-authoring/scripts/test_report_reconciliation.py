"""Synthetic public report intake regression, never business execution."""
import json  # Serialize supplied synthetic reports.
import tempfile  # Isolate evidence files.
import unittest  # Exercise the public adapter.
from pathlib import Path  # Local authorized inputs.
from test_p0_evidence import fixture  # Existing P0 gate fixtures.
from report_reconciliation import reconcile_reports  # New public intake seam.
from qa_record import start_record, advance_record, read_record, read_notes  # One answer source.


class ReportTests(unittest.TestCase):  # Test outcomes through the public entry.
    def test_nearby_versions_and_conflicting_metadata_never_prove_p0(self):  # Remaining version-conflict acceptance boundary.
        full, baseline, reports, request = fixture()  # Synthetic full approved scope.
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:  # Real isolated source reads.
            root = Path(directory)  # Authorized fixture directory.
            metadata = root / 'version.json'  # Necessary readable attachment.
            metadata.write_text(json.dumps({'tested_version': 'another-version'}), encoding='utf-8')  # Contradicts report version.
            reports[0]['required_attachments'] = ['version.json']  # Explicit necessary evidence.
            paths = []  # Original files retained.
            for index, report in enumerate(reports):  # Every approved P0 remains represented.
                path = root / f'{index}.json'  # Source identity.
                path.write_text(json.dumps(report), encoding='utf-8')  # Actual synthetic report bytes.
                paths.append(str(path))  # Exact authorization.
            result = reconcile_reports(full, baseline, paths, request, authorized_paths=paths + [str(metadata)], mode='simulation')  # Existing target cannot conceal conflict.
            self.assertFalse(result['check']['can_extend'])  # Conflict remains blocking.
            self.assertEqual(result['check']['cases'][0]['execution_status'], 'pending_check')  # No fabricated pass.
            self.assertIn(str(metadata.resolve()), [row['path'] for row in result['read_sources']])  # Actually read metadata before decision.
            denied = reconcile_reports(full, baseline, paths, request, authorized_paths=[], mode='simulation')  # Authorization is not inferred from supplied paths.
            self.assertEqual(denied['read_sources'], [])  # No unauthorized file read claim.
            self.assertEqual(len(denied['gaps']), 2)  # Each unavailable report remains visible.

    def test_report_question_and_selection_share_existing_task_record(self):  # No fake business-field updates.
        full, _, _, _ = fixture()  # Existing catalog can seed a report-only stage.
        full['questions'] = []  # No manufactured rule doubts.
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:  # Isolated journal.
            path = Path(directory) / 'qa.md'  # Sole source across stages.
            start_record(path, 'simulated-task', full, [])  # Existing public start boundary.
            question = {'display': 'QREPORT1：模拟报告版本选择，A为V1，B为V2，也可另答；推荐核实目标；理由：不同边界；代价：缺证据等待；假设例子：50或100字。', 'basis': ['synthetic://report']}  # Full Chinese question.
            advance_record(path, 'record_context', question)  # Save before asking, without inventing a reply.
            advance_record(path, 'record_note', {'actual_reply': '[模拟]选V2', 'source_ref': '模拟对话第2轮', 'question_id': 'QREPORT1', 'tested_version': 'V2'})  # Save actual selection.
            self.assertEqual(read_notes(path)[-1]['payload']['tested_version'], 'V2')  # Resume from the same MD.
            self.assertEqual(read_record(path)['batch'], full)  # Report selection is not a rule update.
            self.assertIn(question['display'], path.read_text(encoding='utf-8'))  # Saved question is readable.

    def test_selected_report_with_missing_attachment_stays_pending(self):  # Selection cannot open P0 gate.
        full, baseline, reports, request = fixture()  # Explicit simulated target and manual start.
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:  # Authorized isolated fixtures.
            root = Path(directory)  # File root.
            reports[0]['evidence'][0]['path'] = 'missing.txt'  # Cached inline content must not hide absence.
            paths = []  # Original report files.
            for index, report in enumerate(reports):  # Full P0 report scope.
                path = root / f'{index}.json'  # Stable local evidence path.
                path.write_text(json.dumps(report), encoding='utf-8')  # Actual data supplied.
                paths.append(str(path))  # Authorized exact paths.
            result = reconcile_reports(full, baseline, paths, request, authorized_paths=paths, selected_paths=paths, mode='simulation')  # User choice retains proof requirements.
            self.assertFalse(result['check']['can_extend'])  # Missing necessary attachment blocks.
            self.assertEqual(result['check']['cases'][0]['execution_status'], 'pending_check')  # Never false pass.
            self.assertEqual(result['gaps'][0]['case_id'], 'EDIT')  # Concrete affected scope.
            self.assertEqual(result['check']['cases'][1]['execution_status'], 'passed')  # Independent evidence preserved.
            self.assertFalse(result['needs_selection'])  # A missing attachment is a fact gap, not a version question.

    def test_missing_report_is_a_fact_gap_not_a_new_target_question(self):  # Preserve valid target decisions.
        full, baseline, _, request = fixture()  # Explicit unchanged target.
        result = reconcile_reports(full, baseline, [], request, authorized_paths=[], mode='simulation')  # Nothing accessible.
        self.assertFalse(result['needs_selection'])  # Ask for missing evidence, not already known version.
        self.assertFalse(result['check']['can_extend'])  # All approved cases remain in scope.
        self.assertIn('待核对', result['chat'])  # Human-readable result.

    def test_known_target_reads_all_reports_and_reuses_matching_version(self):  # Dates never select the target.
        full, baseline, reports, request = fixture()  # Simulated complete P0.
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:  # Keep files inside workspace.
            root = Path(directory)  # Authorized fixture location.
            paths = []  # Explicit file allowlist.
            for index, report in enumerate(reports + [dict(reports[0], tested_version='old-version')]):  # Nearby dates, different versions.
                path = root / f'report-{index}.json'  # Distinct original reports.
                path.write_text(json.dumps(report), encoding='utf-8')  # Actual report bytes.
                paths.append(str(path))  # Read every supplied report before selecting.
            result = reconcile_reports(full, baseline, paths, request, authorized_paths=paths, mode='simulation')  # Public call.
            self.assertTrue(result['check']['can_extend'])  # Existing full P0 checker still decides.
            self.assertEqual(len(result['read_sources']), 3)  # Read old report too, do not ask first.
            self.assertFalse(result['needs_selection'])  # Known valid target is reused.
            self.assertIn('old-version', result['chat'])  # Explain excluded version in readable summary.


if __name__ == '__main__':  # Standard test entry.
    unittest.main()  # Run isolated regressions.
