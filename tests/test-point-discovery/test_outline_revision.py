"""Exercise partial outline revisions through the released CLI."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_outline_gate import CHECK


class OutlineRevisionTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.old = {"module": "附件", "branches": [["拍照", "方式 0"], ["录音"]]}
        self.new = {"module": "附件", "branches": [["拍照", "方式 0"], ["从云盘选择"]]}
        shown = "按这个附件大纲写：拍照 → 方式 0、录音"
        cite = self.conversation("old", [("user", shown)])[0]
        self.save("old.json", {"task": "演练", "kind": "adopt", "outline": self.old,
                               "evidence": [{"basis": cite, "reply": cite}]})
        self.request = {"task": "演练", "module": "附件", "outline": self.new,
                        "scope": [["拍照", "方式 0"]], "previous_decision": "old.json"}

    def save(self, name, data):
        (self.root / name).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def conversation(self, name, turns):
        path = name + "-chat.json"
        self.save(path, [{"role": role, "content": words} for role, words in turns])
        sha = hashlib.sha256((self.root / path).read_bytes()).hexdigest()
        return [{"path": path, "sha256": sha, "quote": words} for _, words in turns]

    def check(self):
        self.save("request.json", self.request)
        run = subprocess.run([sys.executable, "-X", "utf8", str(CHECK), str(self.root / "request.json")],
                             capture_output=True, encoding="utf-8")
        result = json.loads(run.stdout)
        self.assertEqual(run.returncode, 0 if result["status"] == "allow" else 1, run.stderr)
        return result

    def test_unmodified_branch_can_continue_while_changes_await_confirmation(self):
        result = self.check()
        self.assertEqual(result["status"], "allow", result)
        self.assertEqual(result["diff"], {"added": [["从云盘选择"]], "removed": [["录音"]],
                                          "unchanged": [["拍照", "方式 0"]]})
        self.assertNotEqual(result["previous_version"], result["version"])
        self.assertEqual(result["scope"], [["拍照", "方式 0"]])
        for write, remove in [([["从云盘选择"]], []), ([], [["录音"]]),
                              ([["拍照", "方式 0"]], [["录音"]])]:
            with self.subTest(write=write, remove=remove):
                self.request.update(scope=write, remove_scope=remove, decision="old.json")
                blocked = self.check()
                self.assertEqual(blocked["status"], "block")
                self.assertEqual(blocked["diff"], result["diff"])

    def confirm(self, display):
        basis, reply = self.conversation("new", [("assistant", display), ("user", "采用这次调整。")])
        self.save("new.json", {"task": "演练", "kind": "confirm", "outline": self.new,
                               "evidence": [{"basis": basis, "reply": reply}]})
        self.request["decision"] = "new.json"

    def test_confirmed_add_and_removal_target_only_requested_lines(self):
        self.request.update(scope=[["从云盘选择"]], remove_scope=[["录音"]])
        draft = {"拍照": "原检查", "录音": "原正文"}
        blocked = self.check()
        self.assertEqual(blocked["status"], "block")
        self.assertEqual(draft, {"拍照": "原检查", "录音": "原正文"})
        tree = "附件\n  拍照\n    方式 0\n  从云盘选择"
        self.confirm(tree)
        self.assertEqual(self.check()["status"], "block")  # No displayed deletion
        self.confirm(tree + "\n" + blocked["review_text"])
        allowed = self.check()
        self.assertEqual(allowed["status"], "allow", allowed)
        self.assertEqual(allowed["decision_version"], allowed["version"])
        for branch in allowed["scope"]:
            draft[branch[-1]] = "新增检查"
        for branch in allowed["remove_scope"]:
            del draft[branch[-1]]
        self.assertEqual(draft, {"拍照": "原检查", "从云盘选择": "新增检查"})

    def test_retire_all_branches_allows_only_the_confirmed_deletions(self):
        self.new["branches"] = []
        self.request.update(scope=[], remove_scope=self.old["branches"])
        blocked = self.check()
        self.assertEqual(blocked["status"], "block")
        self.confirm("本次移除附件全部分支。\n" + blocked["review_text"])
        result = self.check()
        self.assertEqual(result["status"], "allow", result)
        self.assertEqual(result["scope"], [])
        self.assertEqual(result["remove_scope"], self.old["branches"])
        self.request.update(scope=[["录音"]])
        self.assertEqual(self.check()["status"], "block")
        del self.request["previous_decision"]
        self.request.update(scope=[], remove_scope=[])
        self.assertEqual(self.check()["status"], "block")

    def test_confirmed_revision_cannot_rewrite_unaffected_sibling(self):
        self.request.update(scope=self.new["branches"], remove_scope=[["录音"]])
        result = self.check()
        self.confirm("附件：拍照 → 方式 0、从云盘选择\n" + result["review_text"])
        self.assertEqual(self.check()["status"], "block")

    def test_reopen_after_confirmed_retirement_needs_new_confirmation(self):
        self.new["branches"] = []
        self.request.update(scope=[], remove_scope=self.old["branches"])
        retirement = self.check()
        self.confirm("以下是" + retirement["review_text"].rsplit("\n", 1)[0])
        self.assertEqual(self.check()["status"], "block")
        self.confirm("以下是" + retirement["review_text"] + "。请确认。")
        self.assertEqual(self.check()["status"], "allow")
        # Keep the exact successful decision and both original messages for reuse.
        (self.root / "new.json").rename(self.root / "retired.json")
        self.new["branches"] = [["选取文档"]]
        self.request.update(previous_decision="retired.json", scope=self.new["branches"],
                            remove_scope=[])
        del self.request["decision"]
        reentry = self.check()
        self.assertEqual(reentry["status"], "block")
        self.assertEqual(reentry.get("diff"),
                         {"added": [["选取文档"]], "removed": [], "unchanged": []}, reentry)
        self.assertEqual(reentry["previous_version"], retirement["version"])
        basis, reply = self.conversation("reopen", [
            ("assistant", reentry["review_text"]), ("user", "确认添加选取文档。")])
        self.save("reopen.json", {"task": "演练", "kind": "confirm", "outline": self.new,
                                  "evidence": [{"basis": basis, "reply": reply}]})
        self.request["decision"] = "reopen.json"
        self.assertEqual(self.check()["status"], "allow")
        self.request["previous_decision"] = self.request.pop("decision")
        continued = self.check()
        self.assertEqual(continued["status"], "allow")
        self.assertEqual(continued["diff"]["unchanged"], self.new["branches"])

    def test_empty_baseline_requires_a_retrievable_confirmation_of_this_retirement(self):
        self.new["branches"] = []
        self.request.update(scope=[], remove_scope=self.old["branches"])
        retired = self.check()
        other_module = "外部附件"
        other_outline = dict(self.old, module=other_module)
        cite = self.conversation("other", [("user", "按外部附件大纲写：拍照 → 方式 0、录音")])[0]
        self.save("other.json", {"task": "演练", "kind": "adopt", "outline": other_outline,
                                 "evidence": [{"basis": cite, "reply": cite}]})
        self.request.update(module=other_module, outline=dict(self.new, module=other_module),
                            previous_decision="other.json")
        other_retired = self.check()
        empty = self.new
        self.new = {"module": "附件", "branches": [["选取文档"]]}
        self.request.update(module="附件", outline=self.new, scope=self.new["branches"], remove_scope=[],
                            previous_decision="empty.json")
        diff = retired["review_text"]
        header = diff.splitlines()[0]
        for kind, shown, answer in [
            ("confirm", "空大纲", "同意。"),
            ("adopt", diff, "同意。"),
            ("confirm", diff, ""),
            ("confirm", header, "同意。"),
            ("confirm", diff.replace("附件大纲调整", "另一个模块大纲调整"), "同意。"),
            ("confirm", other_retired["review_text"], "同意。"),
            ("confirm", diff.replace(retired["version"][:12], "0" * 12), "同意。"),
            ("confirm", diff.replace(retired["previous_version"][:12], retired["version"][:12]), "同意。"),
        ]:
            with self.subTest(kind=kind, shown=shown, answer=answer):
                basis, reply = self.conversation("empty", [("assistant", shown), ("user", answer)])
                self.save("empty.json", {"task": "演练", "kind": kind, "outline": empty,
                                         "evidence": [{"basis": basis, "reply": reply}]})
                blocked = self.check()
                self.assertEqual(blocked["status"], "block")
                self.assertNotIn("diff", blocked)

    def test_move_is_an_addition_and_a_deletion_of_full_paths(self):
        self.new["branches"] = [["录像", "方式 0"], ["录音"]]
        self.request.update(scope=[["录像", "方式 0"]], remove_scope=[["拍照", "方式 0"]])
        result = self.check()
        self.assertEqual(result["status"], "block")
        self.assertEqual(result["diff"], {"added": [["录像", "方式 0"]],
                                          "removed": [["拍照", "方式 0"]], "unchanged": [["录音"]]})
        self.confirm("附件：录像 → 方式 0、录音\n" + result["review_text"])
        self.assertEqual(self.check()["status"], "allow")
        self.request.update(remove_scope=[["拍照"]])
        self.assertEqual(self.check()["status"], "block")

    def test_refinement_reuses_original_decision_without_scope_change(self):
        self.request.update(outline=self.old)
        result = self.check()
        self.assertEqual(result["status"], "allow")
        self.assertEqual(result["version"], result["decision_version"])
        self.assertEqual(result["diff"]["added"], [])
        self.assertEqual(result["diff"]["removed"], [])
        self.assertNotIn("review_text", result)

    def test_invalid_baseline_cannot_release_common_branch(self):
        self.request["task"] = "另一次演练"
        self.assertEqual(self.check()["status"], "block")
        self.request.update(task="演练", module="图库", outline=dict(self.new, module="图库"))
        self.assertEqual(self.check()["status"], "block")

    def test_old_leaf_cannot_cover_unconfirmed_children(self):
        self.new["branches"] = self.old["branches"] + [["录音", "长录音"]]
        self.request.update(scope=[["录音"]])
        self.assertEqual(self.check()["status"], "block")
