from pathlib import Path
import subprocess, sys, tempfile, unittest

WRITER = Path(__file__).resolve().parents[2] / ".agents/skills/jmeter-tps-writer/scripts/writer.py"

class Pilot(unittest.TestCase):
    def test_account_file_uses_physical_lines(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)
            (p/"input").write_text("curl http://localhost/a -b sid=first")
            (p/"accounts").write_text("cookie\nsid=first\u2028sid=second", encoding="utf8")
            run = subprocess.run([sys.executable, WRITER, "--requests", p/"input", "--accounts", p/"accounts",
                                  "--out", p/"out", "--jmeter", p/"missing"])
            self.assertEqual(run.returncode, 2)
            self.assertIn("单列 cookie", (p/"out/summary.md").read_text(encoding="utf8"))

    def test_missing_engine_retains_plan(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p/"input").write_text("curl http://localhost/a -H 'Content-Type: application/json' -d '{}'")
            (p/"accounts").write_text("cookie\nsid=test-secret")
            subprocess.run([sys.executable, WRITER, "--requests", p/"input", "--accounts", p/"accounts",
                            "--out", p/"out", "--jmeter", p/"missing"])
            self.assertTrue((p/"out/plan.jmx").exists())
            self.assertIn("未执行", (p/"out/summary.md").read_text(encoding="utf8"))
            self.assertNotIn("test-secret", (p/"out/plan.jmx").read_text(encoding="utf8"))
