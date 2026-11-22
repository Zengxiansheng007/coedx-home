from pathlib import Path
import sys, unittest
from tempfile import TemporaryDirectory
from unittest.mock import patch
from contextlib import redirect_stdout
from io import StringIO
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".agents/skills/jmeter-tps-writer/scripts"))
from requests_input import parse_requests
import writer

class PasteTest(unittest.TestCase):
    def test_formatted_cmd(self):
        fixture = Path(__file__).with_name("formatted-cmd.txt")
        targets = parse_requests(fixture.read_text(encoding="utf8"))
        self.assertEqual(len(targets), 1)
        target = targets[0]
        self.assertEqual(len(target.titles), 2)
        self.assertIn('"siteId":"510000"', target.body)
        self.assertIn("EXAMPLE_ONLY_SESSION_2", target.captured_session)

    def test_numbered_fixture_titles(self):
        fixture = Path(__file__).with_name("formatted-cmd.txt")
        if not fixture.exists():
            self.skipTest("工作区缺少规格附带的本地占位用例")
        target, = parse_requests(fixture.read_text(encoding="utf-8-sig"))
        self.assertEqual(target.titles, ["线上办按主题查询接口", "根据个法获取当前的一件事"])
        target, = parse_requests("12345热线查询\ncurl http://localhost")
        self.assertEqual(target.titles, ["12345热线查询"])

    def test_entire_batch_is_literal_before_any_request(self):
        # cmd removes carets during decoding. No dynamic expression is executed.
        base = "http://127.0.0.1:1/path"
        expression = "$^{unused}"
        commands = [
            base + "?ctoken=" + expression,
            base + ' -H ^"X-Example: ' + expression + '^"',
            base + ' --data-raw ^"' + expression + '^"',
            base + ' -b ^"sid=' + expression + '^"',
        ]
        with TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "input"
            for index, command in enumerate(commands):
                with self.subTest(index=index):
                    source.write_text("curl " + base + "\ncurl.exe " + command, encoding="utf8")
                    args = ["writer", "--requests", str(source), "--out", str(root / str(index))]
                    with (patch.object(sys, "argv", args), patch.object(writer, "generate_raw") as importer,
                          patch.object(writer, "run_round") as run, redirect_stdout(StringIO())):
                        self.assertEqual(writer.main(), 2)
                        importer.assert_not_called()
                        run.assert_not_called()
