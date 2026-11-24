"""Plan-bound, double-CAS compile/sync coordinator for immutable v2 releases."""

from __future__ import annotations

import json
import base64
from hashlib import sha256
import os
import re
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Any, Callable

from .case_contracts import canonical_hash, validate_document
from .file_lock import exclusive_file_lock
from .human_view_handoff import HUMAN_VIEW_JOURNAL, TCA_RENDERER_VERSION, required_view_digest
from .path_utils import canonical_display_path, io_path
from .release_verifier import verify_release
from .strict_json import load_strict_json


class CaseSyncError(RuntimeError):
    """同步错误只暴露稳定错误码。"""


def _active_build(target: Path) -> str | None:
    path = target / "active.json"
    if not path.is_file():
        return None
    document = load_strict_json(path)
    return document.get("build_fingerprint") if isinstance(document, dict) else None


def _active_identity_matches(root, case_id, branch_id):
    path = root / "active.json"
    if not path.is_file():
        return True
    document = load_strict_json(path)
    return isinstance(document, dict) and (document.get("case_id"), document.get("branch_id")) == (case_id, branch_id)


def _serialize(content: Any) -> str:
    return content if isinstance(content, str) else json.dumps(content, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _atomic_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        if path.read_bytes() != data:
            raise CaseSyncError("E_SYNC_READBACK_FAILED")
    finally:
        temporary.unlink(missing_ok=True)


def _atomic_json(path: Path, document: dict[str, Any]) -> None:
    payload = json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    _atomic_bytes(path, payload.encode("utf-8"))
    if load_strict_json(path) != document:
        raise CaseSyncError("E_SYNC_READBACK_FAILED")


def _requires_tca(root, active_build, digest):
    if digest or not active_build or re.fullmatch(r"sha256:[0-9a-f]{64}", active_build) is None:
        return False
    current = root / "releases" / active_build.removeprefix("sha256:") / "manifest.json"
    if not current.is_file():
        return False  # 既有兼容路径仍由当前发布验证器处理缺失记录。
    manifest = load_strict_json(current)
    return manifest.get("renderer_version") == TCA_RENDERER_VERSION


def create_sync_plan(compiled: dict[str, Any], target: str | Path, *, operation_id: str | None = None) -> dict[str, Any]:
    """Create a write-free plan bound to exact inputs and expected active state."""
    display_root = canonical_display_path(target)
    root = io_path(display_root)
    plan = {
        "schema_version": "ui-test.compile-plan.v2",
        "operation_id": operation_id or f"sync-{uuid.uuid4().hex}",
        "case_id": compiled["manifest"]["case_id"],
        "branch_id": compiled["manifest"]["branch_id"],
        "target": str(display_root),
        "expected_active_build": _active_build(root),
        "input_identity_hash": canonical_hash(compiled["identity"]),
        "build_fingerprint": compiled["manifest"]["build_fingerprint"],
        "artifact_names": sorted([*compiled["outputs"], "manifest.json"]),
    }
    try:
        view_digest = required_view_digest(compiled)
    except ValueError as error:
        raise CaseSyncError(str(error)) from error
    if view_digest is not None:
        plan["human_view_sha256"] = view_digest  # 发布计划绑定正式成品实际字节。
    if _requires_tca(root, plan["expected_active_build"], view_digest):
        raise CaseSyncError("E_SYNC_HUMAN_VIEW_TAKEOVER_REQUIRED:" + plan["case_id"])
    if not _active_identity_matches(root, plan["case_id"], plan["branch_id"]):
        raise CaseSyncError("E_SYNC_BRANCH_IDENTITY:" + plan["case_id"])
    plan["plan_hash"] = canonical_hash(plan)
    if validate_document(plan, "compile-plan-v2.schema.json"):
        raise CaseSyncError("E_SYNC_PLAN_SCHEMA_INVALID")
    return plan


def dry_run(compiled: dict[str, Any], target: str | Path, *, operation_id: str | None = None) -> dict[str, Any]:
    """Alias with explicit write-free semantics for command wrappers."""
    return create_sync_plan(compiled, target, operation_id=operation_id)


def _result(plan: dict[str, Any], status: str, active_build: str | None, *, no_op: bool, issues: list[str], release_path: Path | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema_version": "ui-test.sync-result.v2",
        "status": status,
        "case_id": plan["case_id"],
        "branch_id": plan["branch_id"],
        "build_fingerprint": plan["build_fingerprint"],
        "active_build": active_build,
        "no_op": no_op,
        "issues": issues,
    }
    if release_path is not None:
        result["release_path"] = str(release_path)
    return result


def _validate_plan(plan: dict[str, Any], display_root: Path, root: Path) -> dict[str, Any] | None:
    """Validate the immutable plan envelope before any release write occurs."""
    supplied_hash = plan.get("plan_hash")
    material = {key: value for key, value in plan.items() if key != "plan_hash"}
    if supplied_hash != canonical_hash(material) or validate_document(plan, "compile-plan-v2.schema.json"):
        return _result(plan, "plan_stale", _active_build(root), no_op=False, issues=["E_SYNC_PLAN_HASH_MISMATCH"])
    if str(display_root) != plan.get("target"):
        return _result(plan, "blocked", _active_build(root), no_op=False, issues=["E_SYNC_TARGET_MISMATCH"])
    return None


def _load_bound_compiled(plan: dict[str, Any], input_loader: Callable[[], dict[str, Any]]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Re-read compilation inputs so a stale plan cannot publish a candidate."""
    compiled = input_loader()
    if (canonical_hash(compiled["identity"]) != plan["input_identity_hash"]
            or any(compiled["manifest"].get(field) != plan[field] for field in ("case_id", "branch_id", "build_fingerprint"))):
        return None, _result(plan, "plan_stale", None, no_op=False, issues=["E_SYNC_INPUT_CHANGED"])
    try:
        digest = required_view_digest(compiled)
    except ValueError:
        digest = ""
    if digest != plan.get("human_view_sha256"):
        return None, _result(plan, "plan_stale", None, no_op=False,
                             issues=["E_SYNC_HUMAN_VIEW_CHANGED:" + plan["case_id"]])
    return compiled, None


def _ensure_release(plan: dict[str, Any], compiled: dict[str, Any], root: Path, *, fail_after_artifacts: int | None = None) -> tuple[Path | None, list[str]]:
    """Create and validate one immutable release without changing active.json."""
    release = root / "releases" / plan["build_fingerprint"].removeprefix("sha256:")
    if release.exists():
        state = verify_release(release, current_identity=compiled["identity"])
        if (state["release_integrity"] != "valid" or state["input_sync"] != "in_sync"
                or not _matches_archived_view(plan, release)):
            return None, ["E_SYNC_EXISTING_RELEASE_INVALID"]
        return release, []
    staging_parent = root / "_staging"
    staging_parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f"{plan['operation_id']}-", dir=staging_parent))
    try:
        files = {**compiled["outputs"], "manifest.json": compiled["manifest"]}
        for index, (name, content) in enumerate(sorted(files.items()), 1):
            destination = staging / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(_serialize(content).encode("utf-8"))
            if fail_after_artifacts is not None and index >= fail_after_artifacts:
                raise CaseSyncError("E_SYNC_INJECTED_GENERATION_FAILURE")
        state = verify_release(staging, current_identity=compiled["identity"])
        if state["release_integrity"] != "valid" or state["input_sync"] != "in_sync":
            raise CaseSyncError("E_SYNC_STAGING_VALIDATION_FAILED")
        release.parent.mkdir(parents=True, exist_ok=True)
        os.replace(staging, release)
        return release, []
    except Exception as exc:
        if staging.exists() and staging.parent == staging_parent:
            # 仅清理本 operation 的唯一 staging，不触碰其他发布或历史资产。
            shutil.rmtree(staging)
        return None, [str(exc).split(":", 1)[0]]


def _matches_view(path, digest):
    try:
        return path.is_file() and "sha256:" + sha256(path.read_bytes()).hexdigest() == digest
    except OSError:
        return False


def _matches_archived_view(plan, release):
    digest = plan.get("human_view_sha256")
    return digest is None or _matches_view(release / "human.md", digest)


def _active_noop(plan, root, active_build):
    digest = plan.get("human_view_sha256")
    if digest:
        release = root / "releases" / active_build.removeprefix("sha256:")
        active_pointer = load_strict_json(root / 'active.json')
        state = verify_release(release, active_pointer=active_pointer)
        if (state['release_integrity'] != 'valid' or not _matches_archived_view(plan, release)
                or not _matches_view(root / "views" / "human.md", digest)):
            return _result(plan, "validation_failed", active_build, no_op=False,
                           issues=["E_SYNC_ACTIVE_HUMAN_VIEW_DRIFT:" + plan["case_id"]])
    return _result(plan, "in_sync", active_build, no_op=True, issues=[])


def _recover_human_handoff(root):
    """Recover the stable detail and pointer after interruption under the branch lock."""
    journal = root / HUMAN_VIEW_JOURNAL
    if not journal.is_file():
        return False
    saved = load_strict_json(journal)
    if saved.get("schema_version") != "ui-test.human-view-activation.v1":
        raise CaseSyncError("E_SYNC_HUMAN_VIEW_RECOVERY_JOURNAL")
    active = root / "active.json"
    view = root / "views" / "human.md"
    current = _active_build(root)
    if current == saved["candidate"] and _matches_view(view, saved["digest"]):
        journal.unlink()  # 两处均已更新时，恢复只补记完成。
        return True
    if current not in (saved["previous_build"], saved["candidate"]):
        raise CaseSyncError("E_SYNC_HUMAN_VIEW_RECOVERY_CONFLICT")
    for path, key in ((view, "previous_view"), (active, "previous_pointer")):
        encoded = saved[key]
        if encoded is None:
            path.unlink(missing_ok=True)
        else:
            data = base64.b64decode(encoded, validate=True)
            if not path.is_file() or path.read_bytes() != data:
                _atomic_bytes(path, data)  # 按已保存原字节恢复，释放历史归档保持不可变。
    journal.unlink()
    return False


def _guard_active_handoff(root, plan):
    try:
        _recover_human_handoff(root)
        if not _active_identity_matches(root, plan["case_id"], plan["branch_id"]):
            return _result(plan, "blocked", _active_build(root), no_op=False,
                           issues=["E_SYNC_BRANCH_IDENTITY:" + plan["case_id"]])
    except (OSError, ValueError, KeyError, TypeError, AttributeError, CaseSyncError):
        return _result(plan, "blocked", None, no_op=False,
                       issues=["E_SYNC_HUMAN_VIEW_RECOVERY_REQUIRED:" + plan["case_id"]])
    return None


def _activate_pointer(root, release, pointer, plan):
    active = root / "active.json"
    if not plan.get("human_view_sha256"):
        _atomic_json(active, pointer)
        return
    view = root / "views" / "human.md"
    journal = root / HUMAN_VIEW_JOURNAL

    def snapshot(path):
        return base64.b64encode(path.read_bytes()).decode("ascii") if path.is_file() else None

    _atomic_json(journal, {
        "schema_version": "ui-test.human-view-activation.v1",
        "candidate": plan["build_fingerprint"],
        "digest": plan["human_view_sha256"],
        "previous_build": _active_build(root),
        "previous_pointer": snapshot(active),
        "previous_view": snapshot(view),
    })
    try:
        _atomic_json(active, pointer)
        _atomic_bytes(view, (release / "human.md").read_bytes())
        if not _matches_view(view, plan["human_view_sha256"]):
            raise CaseSyncError("E_SYNC_ACTIVE_HUMAN_VIEW_READBACK")
    except (OSError, CaseSyncError):
        if not _recover_human_handoff(root):
            raise
    else:
        journal.unlink()


def prepare_sync_plan(
    plan: dict[str, Any],
    input_loader: Callable[[], dict[str, Any]],
    target: str | Path,
    *,
    fail_after_artifacts: int | None = None,
) -> dict[str, Any]:
    """Publish a validated immutable successor while preserving the current active pointer."""
    display_root = canonical_display_path(target)
    root = io_path(display_root)
    rejected = _validate_plan(plan, display_root, root)
    if rejected:
        return rejected
    root.mkdir(parents=True, exist_ok=True)
    lock_name = f"{plan['case_id']}--{plan['branch_id']}.lock".replace("/", "_").replace("\\", "_")
    with exclusive_file_lock(root / ".locks" / lock_name):
        rejected = _guard_active_handoff(root, plan)
        if rejected:
            return rejected
        active_build = _active_build(root)
        if _requires_tca(root, active_build, plan.get("human_view_sha256")):
            return _result(plan, "blocked", active_build, no_op=False,
                           issues=["E_SYNC_HUMAN_VIEW_TAKEOVER_REQUIRED:" + plan["case_id"]])
        if active_build != plan.get("expected_active_build"):
            return _result(plan, "concurrent_update", active_build, no_op=False, issues=["E_SYNC_EXPECTED_ACTIVE_MISMATCH"])
        compiled, error = _load_bound_compiled(plan, input_loader)
        if error:
            error["active_build"] = active_build
            return error
        assert compiled is not None
        if active_build == plan["build_fingerprint"]:
            return _active_noop(plan, root, active_build)
        release, issues = _ensure_release(plan, compiled, root, fail_after_artifacts=fail_after_artifacts)
        if issues:
            status = "validation_failed" if issues == ["E_SYNC_EXISTING_RELEASE_INVALID"] else "generation_failed"
            return _result(plan, status, active_build, no_op=False, issues=issues)
        return _result(plan, "prepared", active_build, no_op=False, issues=[], release_path=release)


def activate_prepared_sync_plan(plan: dict[str, Any], input_loader: Callable[[], dict[str, Any]], target: str | Path) -> dict[str, Any]:
    """CAS-activate a previously prepared and revalidated immutable release."""
    display_root = canonical_display_path(target)
    root = io_path(display_root)
    rejected = _validate_plan(plan, display_root, root)
    if rejected:
        return rejected
    lock_name = f"{plan['case_id']}--{plan['branch_id']}.lock".replace("/", "_").replace("\\", "_")
    with exclusive_file_lock(root / ".locks" / lock_name):
        rejected = _guard_active_handoff(root, plan)
        if rejected:
            return rejected
        active_build = _active_build(root)
        if _requires_tca(root, active_build, plan.get("human_view_sha256")):
            return _result(plan, "blocked", active_build, no_op=False,
                           issues=["E_SYNC_HUMAN_VIEW_TAKEOVER_REQUIRED:" + plan["case_id"]])
        if active_build == plan["build_fingerprint"]:
            if plan.get("human_view_sha256"):
                _, error = _load_bound_compiled(plan, input_loader)
                if error:
                    error["active_build"] = active_build
                    return error
            return _active_noop(plan, root, active_build)
        if active_build != plan.get("expected_active_build"):
            return _result(plan, "concurrent_update", active_build, no_op=False, issues=["E_SYNC_EXPECTED_ACTIVE_MISMATCH"])
        compiled, error = _load_bound_compiled(plan, input_loader)
        if error:
            error["active_build"] = active_build
            return error
        assert compiled is not None
        release = root / "releases" / plan["build_fingerprint"].removeprefix("sha256:")
        if not release.is_dir():
            return _result(plan, "blocked", active_build, no_op=False, issues=["E_SYNC_PREPARED_RELEASE_MISSING"])
        state = verify_release(release, current_identity=compiled["identity"])
        if (state["release_integrity"] != "valid" or state["input_sync"] != "in_sync"
                or not _matches_archived_view(plan, release)):
            return _result(plan, "validation_failed", active_build, no_op=False, issues=["E_SYNC_PREPARED_RELEASE_INVALID"])
        pointer = {
            "schema_version": "ui-test.active-pointer.v2",
            "case_id": plan["case_id"],
            "branch_id": plan["branch_id"],
            "build_fingerprint": plan["build_fingerprint"],
            "manifest_ref": f"releases/{plan['build_fingerprint'].removeprefix('sha256:')}/manifest.json",
        }
        try:
            _activate_pointer(root, release, pointer, plan)
        except (OSError, CaseSyncError):
            return _result(plan, "validation_failed", _active_build(root), no_op=False,
                           issues=["E_SYNC_ACTIVE_HUMAN_VIEW_WRITE:" + plan["case_id"]])
        if _active_build(root) != plan["build_fingerprint"]:
            return _result(plan, "validation_failed", active_build, no_op=False, issues=["E_SYNC_ACTIVE_READBACK_FAILED"])
        return _result(plan, "applied", plan["build_fingerprint"], no_op=False, issues=[], release_path=release)


def apply_sync_plan(
    plan: dict[str, Any],
    input_loader: Callable[[], dict[str, Any]],
    target: str | Path,
    *,
    fail_after_artifacts: int | None = None,
) -> dict[str, Any]:
    """Compatibility wrapper: prepare the immutable release, then CAS-activate it."""
    prepared = prepare_sync_plan(plan, input_loader, target, fail_after_artifacts=fail_after_artifacts)
    if prepared["status"] not in {"prepared", "in_sync"}:
        return prepared
    if prepared["status"] == "in_sync":
        return prepared
    return activate_prepared_sync_plan(plan, input_loader, target)
