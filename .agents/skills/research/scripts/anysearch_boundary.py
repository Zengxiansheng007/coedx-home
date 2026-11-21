"""Guard the documented AnySearch HTTP contract without changing upstream files."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
from urllib import error, parse, request

BASE = "https://api.anysearch.com"
MAX_BYTES = 2 * 1024 * 1024
class BoundaryDenied(ValueError):
    """A permission or integrity denial must never trigger provider fallback."""

class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # Credentials and requests never follow redirect targets.

def verify_upstream(root=None):
    here = Path(__file__).resolve().parent.parent
    source = Path(root) if root else here.parent / "anysearch"
    manifest = json.loads((here / "references/upstream-manifest.json").read_text(encoding="utf-8"))
    for item in manifest["files"]:
        relative = Path(item["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise BoundaryDenied("invalid upstream manifest")
        path = source / relative
        if path.is_symlink() or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise BoundaryDenied("upstream integrity mismatch")
    return manifest["commitSha"]

def perform(operation, payload, key):
    if not isinstance(key, str) or not key.strip():
        raise ValueError("preconfigured key required")
    if os.environ.get("ANYSEARCH_API_BASE_URL", BASE).rstrip("/") != BASE:
        raise BoundaryDenied("endpoint override denied")
    try:
        verify_upstream()
    except (OSError, ValueError):
        raise BoundaryDenied("upstream verification denied") from None
    if operation == "get_sub_domains":
        url = BASE + "/v1/sub-domains?" + parse.urlencode({"domain": payload["domain"]})
        method = "GET"; data = None
    elif operation in {"search", "extract"}:
        url = BASE + "/v1/" + operation
        method = "POST"
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    else:
        raise ValueError("unsupported operation")
    req = request.Request(url, data=data, method=method, headers={
        "Content-Type":"application/json", "Authorization":"Bearer " + key,
        "X-Anysearch-Client":"research-router/1.0"})
    opener = request.build_opener(NoRedirect())
    try:
        response = opener.open(req, timeout=30)
    except error.HTTPError as exc:
        response = exc  # Error bodies stay in memory; caller stores only safe classes.
    with response:
        status = response.code
        if status == 403 or 300 <= status < 400:
            return status, {}  # Denials take precedence over malformed or oversized bodies.
        raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("response too large")
    body = json.loads(raw.decode("utf-8"))
    return status, body
