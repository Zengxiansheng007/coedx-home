"""Exercise the installed outline checker through its documented command."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CHECK = (Path(__file__).resolve().parents[2] / "skills/test-point-discovery"
         / "scripts/check_outline.py")


class OutlineGateTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.tree = {"module": "借阅", "branches": [["登记"], ["归还", "柜台"]]}
        self.request = {"task": "演练", "module": "借阅", "outline": self.tree,
                        "scope": self.tree["branches"], "decision": "decision.json"}
        utterance = "按这个大纲写：借阅 → 登记、归还 → 柜台"
        raw = ("用户回复“" + utterance + "”").encode()
        (self.root / "conversation.md").write_bytes(raw)
        self.cite = {"path": "conversation.md", "sha256": hashlib.sha256(raw).hexdigest(),
                     "quote": utterance}
        self.decision = {"task": "演练", "outline": self.tree, "kind": "adopt",
                         "evidence": [{"basis": self.cite, "reply": self.cite}]}

    def check(self):
        for name, obj in [("decision.json", self.decision), ("request.json", self.request)]:
            (self.root / name).write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
        run = subprocess.run([sys.executable, "-X", "utf8", str(CHECK), str(self.root / "request.json")],
                             capture_output=True, encoding="utf-8")
        self.assertIn(run.returncode, [0, 1], run.stderr)
        result = json.loads(run.stdout)
        self.assertEqual(run.returncode == 0, result["status"] == "allow")
        return result

    def test_direct_user_outline_is_adopted_and_bound_to_module_and_scope(self):
        result = self.check()
        self.assertEqual(result["status"], "allow")
        self.assertEqual(result["module"], "借阅")
        self.assertEqual(result["scope"], [["登记"], ["归还", "柜台"]])
        self.assertRegex(result["version"], r"^[a-f0-9]{64}$")


    def test_title_only_names_the_missing_business_branch(self):
        self.tree["branches"] = []
        result = self.check()
        self.assertEqual(result["status"], "block")
        self.assertIn("具体业务分支", result["reason"])

    def test_other_module_record_cannot_release_current_module(self):
        self.request["module"] = "售票"
        self.assertEqual(self.check()["status"], "block")

    def test_outside_scope_cannot_use_an_existing_version(self):
        self.request["scope"] = [["销毁"]]
        self.assertEqual(self.check()["status"], "block")

    def test_current_tree_moved_branch_cannot_use_previous_decision(self):
        self.request["outline"] = {"module": "借阅", "branches": [["登记"], ["柜台", "归还"]]}
        self.request["scope"] = [["登记"]]
        self.assertEqual(self.check()["status"], "block")

    def test_other_task_cannot_reuse_decision(self):
        self.request["task"] = "另一演练"
        self.assertEqual(self.check()["status"], "block")

    def test_unreadable_decision_stops_with_current_module(self):
        self.request["decision"] = "absent.json"
        result = self.check()
        self.assertEqual(result["status"], "block")
        self.assertEqual(result["module"], "借阅")

    def test_decision_needs_retrievable_user_words_and_reviewed_basis(self):
        for evidence in [[], [{"reply": self.cite}], [{"basis": self.cite}],
                         [{"reply": dict(self.cite, quote="不存在的原话"), "basis": self.cite}],
                         [{"reply": self.cite, "basis": dict(self.cite, sha256="f" * 64)}]]:
            with self.subTest(evidence=evidence):
                self.decision["evidence"] = evidence
                self.assertEqual(self.check()["status"], "block")

    def test_assistant_summary_is_not_a_user_reply(self):
        raw = "助手回复“确认”".encode()
        (self.root / "conversation.md").write_bytes(raw)
        self.cite.update(sha256=hashlib.sha256(raw).hexdigest(), quote="确认")
        self.assertEqual(self.check()["status"], "block")

    def test_numbered_user_reply_can_confirm_previously_shown_scope(self):
        raw = "Q3 是否按借阅下的登记和归还（柜台）组织？\n用户回复“1、保留。3、确认”".encode()
        (self.root / "conversation.md").write_bytes(raw)
        cite = dict(self.cite, sha256=hashlib.sha256(raw).hexdigest())
        self.decision.update(kind="confirm", evidence=[{
            "basis": dict(cite, quote="Q3 是否按借阅下的登记和归还（柜台）组织？"),
            "reply": dict(cite, quote="1、保留。3、确认")}])
        self.assertEqual(self.check()["status"], "allow")

    def test_reply_must_follow_the_displayed_outline_in_the_conversation(self):
        shown = "本次借阅大纲：登记；归还下设柜台"
        answer = "确认按这版写"
        display = {"role": "assistant", "content": shown}
        reply = {"role": "user", "content": answer}
        for turns, expected in [([reply, display], "block"), ([display, reply], "allow")]:
            for suffix, pin_lines in [("json", False), ("jsonl", False), ("jsonl", True)]:
                with self.subTest(expected=expected, suffix=suffix, pin_lines=pin_lines):
                    name = "chat." + suffix
                    lines = [json.dumps(t, ensure_ascii=False).encode() for t in turns]
                    raw = (b"\n".join(lines) if suffix == "jsonl" else
                           json.dumps(turns, ensure_ascii=False).encode())
                    (self.root / name).write_bytes(raw)
                    references = {}
                    for key, turn in [("basis", display), ("reply", reply)]:
                        index = turns.index(turn)
                        citation = {"path": name, "quote": turn["content"],
                                    "sha256": hashlib.sha256(lines[index] if pin_lines else raw).hexdigest()}
                        if pin_lines:
                            citation["line"] = index + 1
                        references[key] = citation
                    self.decision.update(kind="confirm", evidence=[references])
                    self.assertEqual(self.check()["status"], expected)

    def test_host_transcript_uses_original_message_role(self):
        for role, expected in [("assistant", "block"), ("user", "allow")]:
            with self.subTest(role=role):
                payload = {"type": "message", "role": role,
                           "content": [{"type": "input_text", "text": "按借阅大纲写：登记、归还（柜台）"}]}
                raw = json.dumps({"type": "response_item", "payload": payload},
                                 ensure_ascii=False).encode()
                (self.root / "chat.jsonl").write_bytes(raw)
                self.cite.update(path="chat.jsonl", sha256=hashlib.sha256(raw).hexdigest(),
                                 quote="按借阅大纲写：登记、归还（柜台）")
                self.assertEqual(self.check()["status"], expected)

    def test_internal_tool_output_is_not_a_displayed_outline(self):
        shown = "借阅：登记、归还（柜台）"
        answer = "确认本次大纲"
        raw = json.dumps([{"role": "tool", "content": shown},
                          {"role": "user", "content": answer}], ensure_ascii=False).encode()
        (self.root / "chat.json").write_bytes(raw)
        cite = {"path": "chat.json", "sha256": hashlib.sha256(raw).hexdigest()}
        self.decision.update(kind="confirm", evidence=[{
            "basis": dict(cite, quote=shown), "reply": dict(cite, quote=answer)}])
        self.assertEqual(self.check()["status"], "block")

    def test_unsupported_decision_cannot_release_outline(self):
        self.decision["kind"] = "example"
        self.assertEqual(self.check()["status"], "block")

    def test_reply_without_the_original_scope_cannot_release_an_arbitrary_tree(self):
        raw = "用户回复“确认”".encode()
        (self.root / "conversation.md").write_bytes(raw)
        self.cite.update(sha256=hashlib.sha256(raw).hexdigest(), quote="确认")
        self.assertEqual(self.check()["status"], "block")

    def test_pinned_transcript_line_survives_later_append(self):
        raw = json.dumps({"role": "user", "content": self.cite["quote"]},
                         ensure_ascii=False).encode()
        (self.root / "chat.jsonl").write_bytes(raw + b"\r\n{}\r\n")
        self.cite.update(path="chat.jsonl", sha256=hashlib.sha256(raw).hexdigest(), line=1)
        self.assertEqual(self.check()["status"], "allow")

    def test_historical_user_attribution_can_cover_a_section(self):
        samples = [("## 第一轮用户回复\n来源：用户在此轮逐项回复。\n3、采用登记和柜台归还",
                    "3、采用登记和柜台归还"),
                   ("## V1 确认\n- 实际回复：“确认 V1”\n- 来源：本对话紧接 V1 的用户回复。",
                    "确认 V1")]
        for section, reply in samples:
            with self.subTest(reply=reply):
                raw = ("借阅：登记与柜台归还\n" + section).encode()
                (self.root / "conversation.md").write_bytes(raw)
                cite = dict(self.cite, sha256=hashlib.sha256(raw).hexdigest())
                self.decision.update(kind="confirm", evidence=[{
                    "basis": dict(cite, quote="借阅：登记与柜台归还"),
                    "reply": dict(cite, quote=reply)}])
                self.assertEqual(self.check()["status"], "allow")

    def test_resume_uses_original_multiline_qa_after_later_rounds_are_appended(self):
        basis = "借阅大纲包括登记和柜台归还"
        reply = "按展示的大纲继续"
        section = ("## V1 的用户回复\r\n- 来源：用户对 V1 的答复。\r\n1、" + reply).encode()
        original = basis.encode() + b"\r\n" + section
        qa = self.root / "conversation.md"
        qa.write_bytes(original + "\r\n## 阶段5覆盖复核\r\n".encode())
        basis_cite = dict(self.cite, line=1, sha256=hashlib.sha256(basis.encode()).hexdigest(), quote=basis)
        reply_cite = dict(self.cite, line=2, end_line=4, sha256=hashlib.sha256(section).hexdigest(), quote=reply)
        self.decision.update(kind="confirm", evidence=[{"basis": basis_cite, "reply": reply_cite}])
        self.assertEqual(self.check()["status"], "allow")
        qa.write_bytes(original.replace("答复。".encode(), "答复（修订）。".encode()))
        self.assertEqual(self.check()["status"], "block")

    def test_unreadable_request_returns_a_block_result(self):
        run = subprocess.run([sys.executable, "-X", "utf8", str(CHECK), str(self.root / "missing.json")],
                             capture_output=True)
        self.assertEqual(run.returncode, 1)
        self.assertEqual(json.loads(run.stdout)["status"], "block")

if __name__ == "__main__":
    unittest.main()
