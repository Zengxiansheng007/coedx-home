import unittest

from run_evidence import check_received_field


class ReceivedFieldTest(unittest.TestCase):
    def check(self, record, collection="headers"):
        return check_received_field("CASE-7", "run-A", record, collection, "Trace", "v")

    def test_header_name_ignores_case_but_value_is_exact(self):
        record = {"correlation": "CASE-7-run-A", "source_ref": "receiver#31",
                  "headers": {"trace": "v"}, "form": {"Trace": "v"}}
        self.assertEqual(self.check(record)["status"], "通过")
        for observed in [None, "V", ""]:
            with self.subTest(observed=observed):
                record["headers"] = {"Trace": observed}
                self.assertEqual(self.check(record)["status"], "失败")
        record["headers"] = {}
        self.assertEqual(self.check(record)["status"], "失败")

    def test_unavailable_record_collection_or_run_keeps_specific_gap(self):
        for record in [None, {"correlation": "CASE-7-run-B", "source_ref": "receiver#old",
                              "headers": {"trace": "v"}},
                       {"correlation": "CASE-7-run-A", "source_ref": "receiver#31"},
                       {"correlation": "CASE-7-run-A", "headers": {"trace": "v"}}]:
            with self.subTest(record=record):
                result = self.check(record)
                self.assertEqual(result["status"], "待取证")
                self.assertTrue(result["gap"])

    def test_form_names_are_literal_and_headers_do_not_replace_form(self):
        record = {"correlation": "CASE-7-run-A", "source_ref": "receiver#31",
                  "form": {"trace": "v"}, "headers": {"Trace": "v"}}
        self.assertEqual(self.check(record, "form")["status"], "失败")
        record["form"] = {"Trace": "v"}
        self.assertEqual(self.check(record, "form")["status"], "通过")

    def test_whole_case_requires_all_current_checks_and_keeps_gaps_on_failure(self):
        from run_evidence import summarize_case
        case = {"id": "CASE-7", "steps": [{"id": "s1", "expected": [{"text": "ok"}],
                                          "verification": [{"text": "matched file"}]}]}
        observed = {"s1": {"ok": {"status": "通过", "correlation": "CASE-7-run-A",
                                  "source_ref": "page#1", "observed": "ok"}}}
        pending = summarize_case(case, "run-A", observed)
        self.assertEqual(pending["status"], "待取证")
        self.assertEqual(pending["assertions"][0]["source_ref"], "page#1")
        observed["s1"]["matched file"] = {**observed["s1"]["ok"], "source_ref": "receipt#2"}
        self.assertEqual(summarize_case(case, "run-A", observed)["status"], "通过")
        observed["s1"]["matched file"]["correlation"] = "CASE-7-run-B"
        observed["s1"]["ok"]["status"] = "失败"
        failed = summarize_case(case, "run-A", observed)
        self.assertEqual(failed["status"], "失败")
        self.assertEqual(failed["assertions"][1]["status"], "待取证")

    def test_judgment_requires_a_location_and_a_recorded_observation(self):
        from run_evidence import summarize_case
        case = {"id": "C", "steps": [{"id": "s", "expected": [{"text": "field"}]}]}
        for status in ("通过", "失败"):
            for extra, expected in [({}, "待取证"), ({"observed": None}, status),
                                    ({"observed": False}, status), ({"observed_values": []}, status),
                                    ({"observed": 42, "source_ref": " "}, "待取证")]:
                with self.subTest(status=status, extra=extra):
                    row = dict({"status": status, "correlation": "C-R", "source_ref": "receipt"}, **extra)
                    self.assertEqual(summarize_case(case, "R", {"s": {"field": row}})["status"], expected)

    def test_each_dependency_call_needs_its_own_precondition_and_endpoint(self):
        from run_evidence import summarize_case
        child = {"id": "dependency", "common_preconditions": [{"id": "ready", "operation": "open"}],
                 "steps": [{"id": "end", "expected": [{"text": "saved"}]}]}
        case = {"id": "C", "steps": [{"id": key, "operation": "call", "resolved_case": child}
                                     for key in ("first", "second")]}
        row = {"status": "通过", "source_ref": "page", "correlation": "C-R", "observed": True}
        root = {key: {"call": row} for key in ("first", "second")}
        self.assertEqual(summarize_case(case, "R", root)["status"], "待取证")
        nested = {"/steps/first/common_preconditions/ready": {"open": row},
                  "/steps/first/steps/end": {"saved": row},
                  "/steps/second/common_preconditions/ready": {"open": row}}
        def report():
            return summarize_case(case, "R", root, scoped_observations=nested)
        gaps = [item["step_path"] for item in report()["assertions"] if item["status"] == "待取证"]
        self.assertEqual(gaps, ["/steps/second/steps/end"])
        nested[gaps[0]] = {"saved": dict(row, observed=False, status="失败")}
        self.assertEqual(report()["status"], "失败")
        nested[gaps[0]] = {"saved": row}
        self.assertEqual(report()["status"], "通过")
