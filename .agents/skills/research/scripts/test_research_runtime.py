"""Offline behavioral tests; every transport is injected or explicitly mocked."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import research_runtime as r
import anysearch_boundary as b

def task(provider="auto", **kwargs):
    return r.create("task1", ["one"], provider, user_choice="" if provider=="auto" else "user chose "+provider, **kwargs)
def item(objective="one"):
    return {"objective":objective,"operation":"search","query":"public reference"}
def success(content="verified page text"):
    return 200, {"code":0,"data":{"results":[{"url":"https://example.org/doc","title":"Documentation","content":content}]}}
def review(state):
    return {"taskId":state["taskId"],"generation":state["generation"],"reviewedBy":"Codex",
      "actualEvidenceReviewed":True,"gaps":[],"claims":[{"text":"A supported fact","objective":"one","sourceIds":[state["sources"][0]["sourceId"]]}]}
def retrieved():
    state=task()
    r.execute_anysearch(state,[item()],"test-key",lambda *args:success())
    return state

class RoutingTests(unittest.TestCase):
    def test_default_and_explicit_routes(self):
        for provider,executor in [("auto","anysearch"),("anysearch","anysearch"),("claude","claude"),("codex","codex")]:
            with self.subTest(provider=provider):
                state=task(provider)
                self.assertEqual(state["executor"],executor)
                self.assertEqual(state["phase"],"anysearch-ready" if executor=="anysearch" else "guided-pending")
    def test_subject_does_not_choose_executor(self):
        self.assertEqual(r.create("t",["Compare Claude and Codex"])["executor"],"anysearch")
    def test_guided_default(self):
        state = r.create("t", ["Compare Claude and Codex"], entry="research-guided")
        self.assertEqual(r.guided_handoff(state)["executor"], "codex")
        self.assertEqual(state["requestedProvider"], "auto")
        explicit = task("claude", entry="research-guided")
        self.assertEqual(r.guided_handoff(explicit)["executor"], "claude")
    def test_explicit_provider_needs_user_evidence(self):
        for provider in ("codex", "claude"):
            with self.subTest(provider=provider), self.assertRaisesRegex(r.GateError, "explicit-choice-evidence-required"):
                r.create("t", ["one"], provider, entry="research-guided")
    def test_legacy_implicit_claude_handoff_adopts_codex_once(self):
        state = task("claude")
        state["requestedProvider"] = "auto"
        r.safe_sources(state, [{"url":"https://example.org/doc","content":"Previously read page"}], "one", "extract")
        sources = copy.deepcopy(state["sources"])
        handoff = r.guided_handoff(state)
        self.assertEqual((handoff["executor"], handoff["generation"]), ("codex", 2))
        self.assertEqual(handoff["sources"], sources)
        self.assertEqual(handoff, r.guided_handoff(state))
        stale = {"taskId":"task1","generation":1,"executor":"claude"}
        with self.assertRaisesRegex(r.GateError, "guided-lineage"):
            r.accept_guided(state, stale)
    def test_resume_legacy_implicit_claude_uses_codex(self):
        for provider, requested_flag, expected in [("auto", None, "codex"), ("auto", "claude", "claude"),
                                                   ("claude", None, "claude")]:
            with self.subTest(provider=provider, requested_flag=requested_flag):
                state = task("claude")
                state["requestedProvider"] = provider
                r.pause(state, "guided-unavailable")
                r.resume(state, "User chose Claude" if requested_flag else "Continue", requested_flag)
                handoff = r.guided_handoff(state)
                self.assertEqual((handoff["executor"], handoff["generation"]), (expected, 2))
    def test_missing_key_has_no_call(self):
        calls=[]
        state=task(); r.execute_anysearch(state,[item()],"",lambda *x:calls.append(x))
        self.assertEqual(calls,[]); self.assertEqual(state["executor"],"codex")
        self.assertEqual(state["phase"],"guided-pending")
    def test_guided_does_not_require_anysearch_key(self):
        state=task("codex"); self.assertEqual(r.guided_handoff(state)["executor"],"codex")
    def test_recognized_quota_switches_to_codex(self):
        for message in r.QUOTA_MESSAGES:
            state=task()
            r.execute_anysearch(state,[item()],"test-key",lambda *x:(402,{"code":-1,"message":message}))
            self.assertEqual(state["phase"],"guided-pending")
            self.assertEqual(state["executor"],"codex")
    def test_nonquota_and_unknown_route_after_one_call(self):
        cases=[(429,{"code":-1,"message":"quota_exhausted"}),(402,{"code":-1,"message":"unknown"}),
            (401,{"code":-1}), (403,{"code":-1}), (500,{"code":-1}), (302,{"code":0}),
            (200,{"code":0}), (200,[]), (200,{"code":True,"data":{}})]
        for response in cases:
            with self.subTest(response=response):
                calls=[]
                def transport(*args):calls.append(1); return response
                state=task()
                r.execute_anysearch(state,[item(),item()],"test-key",transport)
                self.assertEqual(len(calls),1)
                blocked = response[0] in {302, 403}
                self.assertEqual(state["phase"],"paused" if blocked else "guided-pending")
                self.assertEqual(state["executor"],"anysearch" if blocked else "codex")
    def test_exception_not_logged_or_retried(self):
        def transport(*args):raise OSError("private diagnostic should not persist")
        state=task();r.execute_anysearch(state,[item(),item()],"test-key",transport)
        self.assertNotIn("private diagnostic",r.canonical(state))
        self.assertEqual(len(state["calls"]),1)
    def test_no_fallback_wins(self):
        state=task(no_fallback=True)
        r.execute_anysearch(state,[item()],"test-key",lambda *x:(402,{"code":-1,"message":"quota_exhausted"}))
        self.assertEqual(state["pauseReason"],"fallback-forbidden")
    def test_partial_batch_keeps_evidence_stops_dispatch(self):
        replies=iter([success(),(500,{"code":-1}),success()])
        calls=[]
        def transport(*args):calls.append(1);return next(replies)
        state=task();r.execute_anysearch(state,[item(),item(),item()],"test-key",transport)
        self.assertEqual(len(calls),2);self.assertEqual(len(state["sources"]),1)
        self.assertEqual(state["phase"],"guided-pending")
        self.assertEqual(state["executor"],"codex")
    def test_pause_forbids_retrieval_completion_and_reinforcement(self):
        state=retrieved(); evidence=review(state);r.pause(state,"rate-limited")
        for operation in [lambda:r.execute_anysearch(state,[item()],"test-key",lambda*x:success()),
                          lambda:r.complete(state,evidence),lambda:r.reinforce(state)]:
            with self.assertRaises(r.GateError):operation()
    def test_resume_requires_user_and_preserves_progress(self):
        state=retrieved();r.pause(state,"timeout"); old=copy.deepcopy(state["sources"])
        with self.assertRaises(r.GateError):r.resume(state,"")
        r.resume(state,"用户明确重试")
        self.assertEqual(state["sources"],old);self.assertEqual(state["executor"],"anysearch")
        r.execute_anysearch(state,[item()],"test-key",lambda*x:(500,{"code":-1}))
        self.assertEqual(state["phase"],"guided-pending")
        self.assertEqual(state["executor"],"codex")
    def test_resume_cannot_skip_recovery_probe(self):
        state=retrieved();r.pause(state,"timeout");r.resume(state,"retry")
        with self.assertRaises(r.GateError):r.complete(state,review(state))
        with self.assertRaises(r.GateError):r.reinforce(state)
        r.execute_anysearch(state,[item()],"test-key",lambda*x:success())
        r.complete(state,review(state));self.assertEqual(state["phase"],"complete")
    def test_state_directory_cannot_pollute_installed_skills(self):
        with self.assertRaises(r.GateError):r.Store(Path(__file__).resolve().parent.parent/"state")
    def test_claude_fallback_requires_auth(self):
        state=task("claude");r.guided_failure(state,"timeout");self.assertEqual(state["phase"],"paused")
        state=task("claude",codex_authorization="user allows Codex for this task")
        r.guided_failure(state,"timeout");self.assertEqual(state["executor"],"codex")
        r.guided_failure(state,"timeout");self.assertEqual(state["phase"],"paused")
    def test_secrets_removed_from_success_and_error_bodies(self):
        state=task()
        def transport(*args):
            status,body=success("literal-unit-key")
            body["data"]["results"][0]["api_key"]="must-never-persist"
            return status,body
        r.execute_anysearch(state,[item()],"literal-unit-key",transport)
        self.assertNotIn("literal-unit-key",r.canonical(state));self.assertNotIn("must-never-persist",r.canonical(state))
        state=task();r.execute_anysearch(state,[item()],"test-key",lambda*x:(402,{"code":-1,"message":"quota_exhausted","data":{"api_key":"unexpected"}}))
        self.assertNotIn("unexpected",r.canonical(state))
    def test_public_url_boundary(self):
        for value in ["http://localhost/x","http://127.0.0.1/","http://192.168.1.2/","file:///tmp/x","https://user:pass@example.org/","https://example.org/?api_key=value"]:
            self.assertFalse(r.public_url(value),value)
        self.assertTrue(r.public_url("https://example.org/doc"))
    def test_discovery_and_required_domain_params(self):
        state=task(); request=item();request["tag"]="code.doc"
        with self.assertRaises(r.GateError):r.execute_anysearch(state,[request],"test-key",lambda*x:success())
        response=(200,{"code":0,"data":{"domains":[{"sub_domains":[{"sub_domain":"code.doc","params":{"library":{"required":True}}}]}]}})
        r.execute_anysearch(state,[{"objective":"one","operation":"get_sub_domains","domain":"code"}],"test-key",lambda*x:response)
        with self.assertRaises(r.GateError):r.execute_anysearch(state,[request],"test-key",lambda*x:success())
        request["params"]={"library":""}
        r.execute_anysearch(state,[request],"test-key",lambda*x:success())
        self.assertTrue(state["sources"])
    def test_quality_requires_real_sources_and_coverage(self):
        state=retrieved();r.complete(state,review(state));self.assertEqual(state["phase"],"complete")
        for mutation in ["unknown-source","gap","no-review","stale"]:
            state=retrieved();receipt=review(state)
            if mutation=="unknown-source":receipt["claims"][0]["sourceIds"]=["unknown"]
            if mutation=="gap":receipt["gaps"]=["missing source"]
            if mutation=="no-review":receipt["actualEvidenceReviewed"]=False
            if mutation=="stale":receipt["generation"]=0
            with self.assertRaises(r.GateError):r.complete(state,receipt)
    def test_uncovered_objective_prevents_completion(self):
        state=r.create("task1",["one","two"]);r.execute_anysearch(state,[item()],"test-key",lambda*x:success())
        with self.assertRaises(r.GateError):r.complete(state,review(state))
    def test_empty_results_not_complete(self):
        state=task();r.execute_anysearch(state,[item()],"test-key",lambda*x:(200,{"code":0,"data":{"results":[]}}))
        self.assertEqual(state["phase"],"anysearch-ready")
        with self.assertRaises(r.GateError):r.complete(state,{"taskId":"task1","generation":1,"reviewedBy":"Codex","actualEvidenceReviewed":True,"gaps":[],"claims":[]})
    def test_reinforcement_limit(self):
        state=retrieved();r.reinforce(state)
        with self.assertRaises(r.GateError):r.reinforce(state)
    def test_guided_receipt_lineage_and_actual_retrieval(self):
        state=task("codex")
        receipt={"taskId":"task1","generation":1,"executor":"codex","actualRetrieval":True,
                 "hostValidationPassed":True,"toolEvidence":[{"tool":"public-search","evidence":"host-reference"}],
                 "sources":[{"objective":"one","url":"https://example.org/doc","content":"read page","readDepth":"body"}]}
        bad=copy.deepcopy(receipt);bad["executor"]="claude"
        with self.assertRaises(r.GateError):r.accept_guided(state,bad)
        bad=copy.deepcopy(receipt);bad["actualRetrieval"]=False
        with self.assertRaises(r.GateError):r.accept_guided(state,bad)
        r.accept_guided(state,receipt);self.assertEqual(state["phase"],"review")
        r.complete(state,review(state));self.assertEqual(state["phase"],"complete")
    def test_store_integrity_duplicate_and_traversal(self):
        with tempfile.TemporaryDirectory() as temp:
            store=r.Store(temp);state=task();store.save(state,create_only=True)
            self.assertEqual(store.load("task1")["taskId"],"task1")
            with self.assertRaises(r.GateError):store.save(state,create_only=True)
            with self.assertRaises(r.GateError):store.path("../outside")
            data=json.loads(store.path("task1").read_text());data["state"]["executor"]="codex"
            store.path("task1").write_text(json.dumps(data))
            with self.assertRaises(r.GateError):store.load("task1")
    def test_interrupted_request_pauses_without_reexecution(self):
        with tempfile.TemporaryDirectory() as temp:
            store=r.Store(temp);state=task();state["calls"]=[{"status":"started"}];store.save(state)
            recovered=store.load("task1")
            self.assertEqual(recovered["pauseReason"],"interrupted-request")
            r.resume(recovered,"retry");store.save(recovered)
            self.assertEqual(store.load("task1")["phase"],"anysearch-ready")
    def test_redirect_handler_denies(self):
        self.assertIsNone(b.NoRedirect().redirect_request(None,None,302,None,None,"https://other.example"))
    def test_upstream_manifest_verifies(self):
        self.assertEqual(len(b.verify_upstream()),40)
    def test_transport_uses_no_redirects_and_header_only_key(self):
        class Response:
            code=200
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,size):return b'{"code":0,"data":{"results":[]}}'
        class Opener:
            def open(self,req,timeout):
                self.req=req;self.timeout=timeout;return Response()
        fake=Opener()
        with patch.object(b.request,"build_opener",return_value=fake),patch.dict(os.environ,{},clear=True):
            status,_=b.perform("search",{"query":"reference"},"test-key")
        self.assertEqual(status,200);self.assertNotIn("test-key",fake.req.full_url)
        self.assertEqual(fake.req.headers["Authorization"],"Bearer "+"test-key")
        self.assertEqual(fake.timeout,30)
    def test_endpoint_override_denied(self):
        with patch.dict(os.environ,{"ANYSEARCH_API_BASE_URL":"https://other.example"}):
            with self.assertRaises(ValueError):b.perform("search",{"query":"q"},"test-key")
    def test_cli_utf8_output(self):
        cli=Path(__file__).with_name("research_cli.py")
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);obj=root/"objectives.json";obj.write_text('["中文研究"]',encoding="utf-8")
            p=subprocess.run([sys.executable,"-B",str(cli),"--state-dir",str(root/"state"),"--task","unicode",
                              "create","--objectives",str(obj)],capture_output=True,timeout=15)
            self.assertEqual(p.returncode,0)
            self.assertEqual(json.loads(p.stdout.decode("utf-8"))["objectives"],["中文研究"])
    def test_cli_offline_flow_and_pause_exit_codes(self):
        cli=Path(__file__).with_name("research_cli.py")
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);objectives=root/"objectives.json";objectives.write_text('["one"]')
            requests=root/"requests.json";requests.write_text(json.dumps([item()]))
            base=[sys.executable,"-B",str(cli),"--state-dir",str(root/"state"),"--task","t"]
            def run(*args):
                env=dict(os.environ);env.pop("ANYSEARCH_API_KEY",None)
                return subprocess.run(base+list(args),capture_output=True,text=True,env=env,timeout=15)
            self.assertEqual(run("create","--objectives",str(objectives),"--no-fallback").returncode,0)
            paused=run("execute-anysearch","--items",str(requests),"--public-retrieval-authorized")
            self.assertEqual(paused.returncode,2)
            self.assertEqual(json.loads(paused.stdout)["pauseReason"],"fallback-forbidden")
            self.assertEqual(run("reinforce").returncode,3)
            self.assertEqual(run("resume","--user-message","retry","--provider","codex").returncode,0)
            self.assertEqual(json.loads(run("handoff").stdout)["executor"],"codex")
            (root/"state/t.lock").write_text("held")
            self.assertEqual(run("status").returncode,3)

    def test_cli_guided_entries_and_legacy_handoff_persist_route(self):
        cli = Path(__file__).with_name("research_cli.py")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            objectives = root / "objectives.json"
            objectives.write_text('["Compare Claude and Codex"]', encoding="utf-8")
            state_dir = root / "state"
            base = [sys.executable, "-B", str(cli), "--state-dir", str(state_dir)]

            def run(task_id, *args):
                result = subprocess.run(base + ["--task", task_id, *args],
                                        capture_output=True, encoding="utf-8", timeout=15)
                self.assertEqual(result.returncode, 0, result.stdout)
                return json.loads(result.stdout)

            create_args = ("create", "--objectives", str(objectives), "--entry", "research-guided")
            run("default", *create_args)
            run("explicit", *create_args, "--provider", "claude", "--user-choice", "Use Claude for retrieval")
            self.assertEqual(run("default", "handoff")["executor"], "codex")
            self.assertEqual(run("explicit", "handoff")["executor"], "claude")

            legacy = task("claude")
            legacy["requestedProvider"] = "auto"
            r.Store(state_dir).save(legacy, create_only=True)
            handoff = run("task1", "handoff")
            saved = run("task1", "status")
            self.assertEqual((saved["executor"], saved["generation"]), ("codex", 2))
            self.assertEqual(handoff, run("task1", "handoff"))


class FallbackRegressionTests(unittest.TestCase):
    def test_all_service_failures_respect_explicit_choice_and_no_fallback(self):
        cases = [(401, {}), (429, {}), (500, {}), (402, {"code":-1,"message":"unknown"}), (200, [])]
        for provider, options in [("anysearch", {}), ("auto", {"no_fallback":True})]:
            for response in cases:
                with self.subTest(provider=provider,response=response):
                    state=task(provider,**options)
                    r.execute_anysearch(state,[item(),item()],"test-key",lambda *x:response)
                    self.assertEqual(state["phase"],"paused")
                    self.assertEqual(state["executor"],"anysearch")
                    self.assertEqual(len(state["calls"]),1)
            state=task(provider,**options)
            r.execute_anysearch(state,[item()],"",lambda *x:self.fail("unexpected request"))
            self.assertEqual(state["phase"],"paused")
    def test_permission_security_and_stop_do_not_fallback(self):
        for failure in [PermissionError("denied"), b.BoundaryDenied("integrity denied")]:
            state=task()
            def denied(*args):raise failure
            r.execute_anysearch(state,[item()],"test-key",denied)
            self.assertEqual(state["phase"],"paused")
            self.assertEqual(state["executor"],"anysearch")
        for response in [(403, []), (302, None), (200,{"code":0,"data":{"results":[{"url":"http://127.0.0.1/","content":"private"}]}})]:
            state=task();r.execute_anysearch(state,[item()],"test-key",lambda *x:response)
            self.assertEqual(state["phase"],"paused")
            self.assertEqual(state["executor"],"anysearch")
        state=task();r.pause(state,"user-stop")
        with self.assertRaises(r.GateError):r.execute_anysearch(state,[item()],"",lambda *x:success())
        state=task()
        def stopped(*args):raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):r.execute_anysearch(state,[item()],"test-key",stopped)
        self.assertEqual(state["executor"],"anysearch")
    def test_missing_key_cannot_skip_request_security_validation(self):
        state=task()
        with self.assertRaises(r.GateError):
            r.execute_anysearch(state,[{"objective":"one","operation":"extract","url":"http://localhost/private"}],"",lambda *x:self.fail("unexpected request"))
        self.assertEqual(state["executor"],"anysearch")
    def test_timeout_routes_once_without_retry_or_bounce(self):
        state=task()
        def timeout(*args):raise TimeoutError("private text")
        r.execute_anysearch(state,[item(),item()],"test-key",timeout)
        self.assertEqual(state["executor"],"codex")
        self.assertEqual(len(state["calls"]),1)
        self.assertNotIn("private text",r.canonical(state))
        with self.assertRaises(r.GateError):r.complete(state,{})
        with self.assertRaises(r.GateError):r.execute_anysearch(state,[item()],"test-key",timeout)
        r.guided_failure(state,"timeout")
        self.assertEqual(state["phase"],"paused")
        self.assertEqual(state["executor"],"codex")
    def test_partial_batch_handoff_and_mixed_executor_completion(self):
        state=r.create("task1",["one","two"])
        replies=iter([success(),(429,{"code":-1})])
        r.execute_anysearch(state,[item(),item("two"),item("two")],"test-key",lambda *x:next(replies))
        old=copy.deepcopy(state["sources"])
        handoff=r.guided_handoff(state)
        self.assertEqual(handoff["executor"],"codex")
        self.assertEqual(handoff["sources"],old)
        self.assertEqual(handoff["evidencePolicy"],"reuse-verified-and-fill-gaps")
        self.assertTrue(handoff["requiresEvidenceReview"])
        receipt={"taskId":"task1","generation":state["generation"],"executor":"codex","actualRetrieval":True,
            "hostValidationPassed":True,"toolEvidence":[{"tool":"host-search","evidence":"offline fixture"}],
            "sources":[{"objective":"two","url":"https://example.org/second","content":"second evidence","readDepth":"body"}]}
        stale=copy.deepcopy(receipt);stale["generation"]-=1
        with self.assertRaises(r.GateError):r.accept_guided(state,stale)
        r.accept_guided(state,receipt)
        self.assertEqual(state["sources"][:len(old)],old)
        evidence={"taskId":"task1","generation":state["generation"],"reviewedBy":"Codex","actualEvidenceReviewed":True,
            "gaps":[],"claims":[{"text":"verified fact","objective":s["objective"],"sourceIds":[s["sourceId"]]} for s in state["sources"]]}
        r.complete(state,evidence)
        self.assertEqual(state["phase"],"complete")
        self.assertEqual({s["executor"] for s in state["sources"]},{"anysearch","codex"})
    def test_cli_missing_key_returns_pending_codex_handoff(self):
        cli=Path(__file__).with_name("research_cli.py")
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);obj=root/"obj.json";obj.write_text('["one"]')
            req=root/"req.json";req.write_text(json.dumps([item()]))
            base=[sys.executable,"-B",str(cli),"--state-dir",str(root/"state"),"--task","t"]
            env=dict(os.environ);env.pop("ANYSEARCH_API_KEY",None)
            def run(*args):return subprocess.run(base+list(args),capture_output=True,text=True,env=env,timeout=15)
            self.assertEqual(run("create","--objectives",str(obj)).returncode,0)
            result=run("execute-anysearch","--items",str(req),"--public-retrieval-authorized")
            self.assertEqual(result.returncode,0)
            self.assertEqual(json.loads(result.stdout)["phase"],"guided-pending")
            self.assertEqual(json.loads(run("handoff").stdout)["executor"],"codex")
            self.assertEqual(run("complete","--review",str(obj)).returncode,3)
    def test_boundary_security_preflight_and_non_json_denials(self):
        with patch.object(b,"verify_upstream",side_effect=OSError("missing manifest")):
            with self.assertRaises(b.BoundaryDenied):b.perform("search",{"query":"q"},"test-key")
        class Response:
            code=403
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,size):return b'<html>denied</html>'
        class Opener:
            def open(self,*args,**kwargs):return Response()
        with patch.object(b.request,"build_opener",return_value=Opener()),patch.dict(os.environ,{},clear=True):
            self.assertEqual(b.perform("search",{"query":"q"},"test-key"),(403,{}))

if __name__=="__main__":unittest.main()
