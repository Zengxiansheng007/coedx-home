import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/".agents/skills/jmeter-tps-writer/scripts"))
from requests_input import parse_requests, BatchError


class Batch(unittest.TestCase):
    def test_ansi_body(self):
        cmd = r"curl http://example.invalid --data-raw $'line1\nline2\tend'"
        self.assertEqual(parse_requests(cmd)[0].body, "line1\nline2\tend")
        with self.assertRaises(BatchError):
            parse_requests(cmd.replace(r"\t", r"\x09"))

    def test_reference_with_credentials(self):
        with self.assertRaises(BatchError):
            parse_requests("curl http://example.invalid -H 'Referer: https://example.invalid/path?ctoken=fictional'")

    def test_identity_and_links(self):
        url = "https://example.invalid/a?x=1"
        lines = ["curl " + url, "curl " + url + " -X DELETE", "curl " + url + " -H 'X-A: 1'",
                 "curl " + url + " -d one", "curl " + url + " -d two", "curl " + url + "2",
                 "[别名](" + url + "2)"]
        targets = parse_requests("\n".join(lines))
        self.assertEqual(len(targets),6)
        self.assertIn("别名",targets[-1].titles)
        with self.assertRaises(BatchError):
            parse_requests("\n".join(lines + ["[不明确]("+url+")"]))

    def test_repeated_header_value_order_is_significant(self):
        one = "curl http://example.invalid -H 'X-Item: one' -H 'X-Item: two'"
        two = one.replace("one","temp").replace("two","one").replace("temp","two")
        self.assertEqual(len(parse_requests(one+"\n"+two)),2)
