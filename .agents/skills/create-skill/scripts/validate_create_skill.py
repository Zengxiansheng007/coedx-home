#!/usr/bin/env python3
"""Validate a Codex Agent Skill package for structure, safety, and maintainability."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
RESOURCE_RE = re.compile(r"(?<![\w.-])((?:references|scripts|assets)/[A-Za-z0-9_./ -]+\.[A-Za-z0-9]+)")
SECRET_RE = re.compile(
    r"sk-[A-Za-z0-9_-]{20,}|Bearer\s+[A-Za-z0-9._-]+|(?i:password|token|cookie)\s*[:=]\s*\S+"
)
DANGEROUS_PATTERNS = [
    r"\b" + "rm" + r"\s+-rf",
    "Remove" + r"-Item\b[^\n]*-Recurse[^\n]*-Force",
    "Invoke" + r"-WebRequest\b[^\n|]*\|\s*" + "Invoke" + r"-Expression",
    "curl" + r"\b[^\n|]*\|\s*(?:sh|bash)",
]
DANGEROUS_RE = re.compile(r"(?:%s)" % "|".join(DANGEROUS_PATTERNS), re.IGNORECASE)
CHANGE_RECORD_STATUSES = {"proposed", "applied", "validated", "blocked", "superseded", "reverted"}
CHANGE_ID_RE = re.compile(r"CR-\d{8}-\d{3}")
GATE_ID_RE = re.compile(r"^[A-Z][A-Z0-9-]*$")
GATE_BINDINGS = {"action", "arguments", "target", "state"}
CHANGE_RECORD_REQUIRED_ENTRY_SECTIONS = [
    "## Summary",
    "## Context And Problem",
    "## Sections Changed",
    "## Decision And Alternatives",
    "## Impact Analysis",
    "## Validation Evidence",
    "## Safety And Privacy",
    "## Risks And Follow-up",
]


@dataclass
class Finding:
    severity: str
    rule: str
    file: str
    message: str
    fix: str


def add(findings: list[Finding], severity: str, rule: str, file: Path | str, message: str, fix: str) -> None:
    findings.append(Finding(severity, rule, str(file), message, fix))


def parse_frontmatter(skill_file: Path, findings: list[Finding]) -> tuple[dict[str, Any] | None, str]:
    text = skill_file.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---\n"):
        add(findings, "P0", "frontmatter-missing", skill_file, "SKILL.md is missing YAML frontmatter.", "Add name and description frontmatter.")
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        add(findings, "P0", "frontmatter-unclosed", skill_file, "YAML frontmatter is not closed.", "Close frontmatter with --- on its own line.")
        return None, text
    raw = text[4:end]
    try:
        data = yaml.safe_load(raw) or {}
    except yaml.YAMLError as error:
        add(findings, "P0", "frontmatter-invalid", skill_file, f"YAML parse failed: {error}", "Fix YAML syntax.")
        return None, text
    if not isinstance(data, dict):
        add(findings, "P0", "frontmatter-object", skill_file, "Frontmatter must be a mapping.", "Use name and description keys.")
        return None, text
    extra = sorted(set(data) - {"name", "description"})
    if extra:
        add(findings, "P1", "frontmatter-extra-fields", skill_file, f"Extra frontmatter fields: {', '.join(extra)}.", "Remove unless target runtime explicitly supports them.")
    return data, text


def validate(root: Path, require_gate_contract: bool = False) -> dict[str, Any]:
    findings: list[Finding] = []
    skill_file = root / "SKILL.md"
    if not root.exists() or not root.is_dir():
        add(findings, "P0", "root-missing", root, "Skill folder does not exist.", "Provide a valid skill folder.")
        return result(root, None, findings)
    if not skill_file.exists():
        add(findings, "P0", "skill-md-missing", skill_file, "SKILL.md is required.", "Create SKILL.md.")
        return result(root, None, findings)

    frontmatter, text = parse_frontmatter(skill_file, findings)
    if frontmatter:
        name = frontmatter.get("name")
        description = frontmatter.get("description")
        if not isinstance(name, str) or not NAME_RE.fullmatch(name):
            add(findings, "P1", "name-format", skill_file, "name must be lowercase hyphen-case.", "Rename the skill and folder consistently.")
        elif name != root.name:
            add(findings, "P1", "name-folder-mismatch", skill_file, f"name '{name}' does not match folder '{root.name}'.", "Make frontmatter name match folder.")
        if not isinstance(description, str) or len(description.strip()) < 80:
            add(findings, "P1", "description-too-weak", skill_file, "description is missing or too short for reliable triggering.", "Name capability and specific trigger contexts.")
        elif not re.search(r"\bUse when\b|when asked|Use if|Use for", description, re.IGNORECASE):
            add(findings, "P2", "description-trigger-wording", skill_file, "description lacks explicit trigger wording.", "Add 'Use when...' style trigger phrases.")

    if "## Validation" not in text:
        add(findings, "P1", "validation-section-missing", skill_file, "Validation section is missing.", "Add commands or checks proving the skill works.")
    if "## Escalation" not in text and "## Safety" not in text:
        add(findings, "P1", "safety-section-missing", skill_file, "Safety or escalation section is missing.", "Document approval and refusal conditions.")
    if len(text.splitlines()) > 500:
        add(findings, "P2", "skill-md-sprawl", skill_file, "SKILL.md is over 500 lines.", "Move long rules or examples to references/.")

    all_files = [
        path
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix.lower() not in {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".ico"}
    ]
    for path in all_files:
        rel = path.relative_to(root).as_posix()
        content = path.read_text(encoding="utf-8", errors="replace")
        for line in content.splitlines():
            if "SECRET_RE =" in line or "DANGEROUS_RE =" in line:
                continue
            if SECRET_RE.search(line):
                add(findings, "P0", "secret-pattern", rel, "Potential secret or credential pattern detected.", "Remove secret and rotate if real.")
                break
        for line in content.splitlines():
            if "DANGEROUS_RE =" in line:
                continue
            if DANGEROUS_RE.search(line):
                add(findings, "P0", "dangerous-command", rel, "Potential dangerous command pattern detected.", "Remove or gate behind explicit approval and sandboxing.")
                break

    for match in LINK_RE.finditer(text):
        target = match.group(1).split("#", 1)[0].strip()
        if not target or re.match(r"^(?:https?://|mailto:)", target):
            continue
        if not (root / target).exists():
            add(findings, "P1", "link-missing", skill_file, f"Linked resource is missing: {target}", "Fix or remove the link.")

    referenced: set[str] = set()
    for match in RESOURCE_RE.finditer(text):
        target = match.group(1).strip()
        referenced.add(target.split("/", 1)[0])
        if not (root / target).exists():
            add(findings, "P1", "resource-missing", skill_file, f"Referenced resource is missing: {target}", "Create it or update the path.")

    for folder in ["references", "scripts", "assets"]:
        candidate = root / folder
        if candidate.exists() and not any(str(path).startswith(str(candidate)) for path in all_files):
            add(findings, "P2", "empty-resource-folder", candidate, f"{folder}/ is empty.", "Remove empty resource folder.")
        if candidate.exists() and folder not in referenced and folder != "assets":
            add(findings, "P2", "resource-folder-unreferenced", candidate, f"{folder}/ is not mentioned from SKILL.md.", "Add a context pointer or remove the folder.")

    validate_change_records(root, findings, require=False)
    validate_gate_contract(root, findings, require=require_gate_contract)

    return result(root, frontmatter, findings)


def validate_gate_contract(root: Path, findings: list[Finding], require: bool = False) -> None:
    """Check the untrusted declaration's shape, never its runtime enforcement claim."""
    path = root / "gate-contract.json"
    if not path.exists():
        if require:
            add(findings, "P1", "gate-contract-missing", path, "Host promotion requires gate-contract.json.", "Declare required gates or an explicit none mode for independent host review.")
        return
    try:
        contract = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        add(findings, "P1", "gate-contract-invalid-json", path, f"Gate contract cannot be read as JSON: {error}", "Repair the JSON declaration.")
        return
    if not isinstance(contract, dict):
        add(findings, "P1", "gate-contract-object", path, "Gate contract must be a JSON object.", "Use the documented contract shape.")
        return
    if contract.get("schemaVersion") != "1.0":
        add(findings, "P1", "gate-contract-version", path, "Unsupported gate contract schemaVersion.", "Use schemaVersion 1.0.")
    if not isinstance(contract.get("targetRuntime"), str) or not contract["targetRuntime"].strip():
        add(findings, "P1", "gate-contract-runtime", path, "targetRuntime must name the controlled runtime.", "Name the runtime whose host will verify this contract.")
    mode = contract.get("mode")
    gates = contract.get("gates")
    if mode not in {"none", "required"}:
        add(findings, "P1", "gate-contract-mode", path, "mode must be none or required.", "Declare whether mandatory gates are claimed.")
    if not isinstance(gates, list):
        add(findings, "P1", "gate-contract-gates", path, "gates must be an array.", "Provide an array, empty only with mode none.")
        return
    if (mode == "none" and gates) or (mode == "required" and not gates):
        add(findings, "P1", "gate-contract-mode-gates", path, "mode and gates disagree.", "Use required with nonempty gates or none with an empty array.")
    seen: set[str] = set()
    required_text = ("id", "condition", "protectedEffect", "protectedAction", "enforcementEntry", "decisionProvider")
    for number, gate in enumerate(gates, start=1):
        label = f"{path} gate #{number}"
        if not isinstance(gate, dict):
            add(findings, "P1", "gate-contract-gate-object", label, "Each gate must be an object.", "Use the documented gate fields.")
            continue
        for field in required_text:
            if not isinstance(gate.get(field), str) or not gate[field].strip():
                add(findings, "P1", "gate-contract-required-field", label, f"{field} must be nonempty text.", "Provide an explicit mapping; do not rely on prose alone.")
        gate_id = gate.get("id")
        if isinstance(gate_id, str):
            if not GATE_ID_RE.fullmatch(gate_id):
                add(findings, "P1", "gate-contract-id", label, "Gate id must be uppercase letters, digits, and hyphens.", "Use a stable id such as G-001.")
            if gate_id in seen:
                add(findings, "P1", "gate-contract-duplicate-id", label, "Duplicate gate id.", "Give each mandatory condition a unique id.")
            seen.add(gate_id)
        if gate.get("decisionAuthority") not in {"program", "human", "policy"}:
            add(findings, "P1", "gate-contract-authority", label, "decisionAuthority must be program, human, or policy.", "Name the independent decision type.")
        if gate.get("freshness") != "per-action":
            add(findings, "P1", "gate-contract-freshness", label, "freshness must be per-action.", "Recheck each protected action.")
        if gate.get("failureMode") != "deny":
            add(findings, "P1", "gate-contract-failure-mode", label, "failureMode must be deny.", "Fail closed on missing, stale, failed, or inconclusive checks.")
        bindings = gate.get("bindTo")
        if not isinstance(bindings, list) or not all(isinstance(item, str) for item in bindings) or not GATE_BINDINGS.issubset(bindings):
            add(findings, "P1", "gate-contract-bindings", label, "bindTo must include action, arguments, target, and state.", "Bind the decision to exact current inputs.")
        paths = gate.get("alternatePaths")
        if not isinstance(paths, list):
            add(findings, "P1", "gate-contract-alternate-paths", label, "alternatePaths must be an array.", "Declare known alternate paths for independent host verification.")
            continue
        for path_number, alternate in enumerate(paths, start=1):
            if not isinstance(alternate, dict) or any(not isinstance(alternate.get(field), str) or not alternate[field].strip() for field in ("path", "verificationRef")) or alternate.get("disposition") not in {"gated", "disabled"}:
                add(findings, "P1", "gate-contract-alternate-path", f"{label} alternate #{path_number}", "Alternate path needs path, gated/disabled disposition, and verificationRef.", "Document a testable path claim; the host must verify it.")


def validate_change_records(root: Path, findings: list[Finding], require: bool = False) -> None:
    record_root = root / "change-records"
    if not record_root.exists():
        if require:
            add(findings, "P0", "change-records-missing", record_root, "change-records/ is required for an existing-skill update.", "Create index, category ledgers, and a detail record.")
        return
    if not record_root.is_dir():
        add(findings, "P0", "change-records-not-directory", record_root, "change-records must be a directory.", "Replace it with the required record directory structure.")
        return

    index = record_root / "index.md"
    categories = record_root / "categories"
    entries = record_root / "entries"
    for path, rule, message in [
        (index, "change-records-index-missing", "change-records/index.md is required."),
        (categories, "change-records-categories-missing", "change-records/categories/ is required."),
        (entries, "change-records-entries-missing", "change-records/entries/ is required."),
    ]:
        if not path.exists():
            add(findings, "P0", rule, path, message, "Create the missing change-record artifact.")

    if index.exists():
        text = index.read_text(encoding="utf-8", errors="replace")
        for section in ["## Latest Changes", "## Category Index", "## Open Risks"]:
            if section not in text:
                add(findings, "P1", "change-records-index-section-missing", index, f"Index is missing {section}.", "Add the required section.")
        if not CHANGE_ID_RE.search(text):
            add(findings, "P1", "change-records-index-no-change-id", index, "Index does not reference any Change ID.", "Add at least one CR-YYYYMMDD-NNN entry.")

    if categories.exists() and categories.is_dir():
        category_files = sorted(categories.glob("*.md"))
        if not category_files:
            add(findings, "P0", "change-records-no-category-ledgers", categories, "No category ledger Markdown files found.", "Create at least one impacted category ledger.")
        for path in category_files:
            text = path.read_text(encoding="utf-8", errors="replace")
            for section in ["## Purpose", "## Outline", "## Detailed Records"]:
                if section not in text:
                    add(findings, "P1", "change-records-category-section-missing", path, f"Category ledger is missing {section}.", "Add the required ledger section.")
            if not CHANGE_ID_RE.search(text):
                add(findings, "P1", "change-records-category-no-change-id", path, "Category ledger does not reference a Change ID.", "Add a CR-YYYYMMDD-NNN outline/detail entry.")

    if entries.exists() and entries.is_dir():
        detail_files = sorted(entries.rglob("CR-*.md"))
        if not detail_files:
            add(findings, "P0", "change-records-no-detail-record", entries, "No detail record files found under entries/.", "Create a CR-YYYYMMDD-NNN detail record.")
        seen: set[str] = set()
        for path in detail_files:
            rel = path.relative_to(root).as_posix()
            match = CHANGE_ID_RE.search(path.name)
            if not match:
                add(findings, "P1", "change-records-detail-name-format", rel, "Detail record filename must include CR-YYYYMMDD-NNN.", "Rename the detail record.")
                continue
            change_id = match.group(0)
            if change_id in seen:
                add(findings, "P1", "change-records-duplicate-change-id", rel, f"Duplicate Change ID: {change_id}.", "Allocate a unique Change ID.")
            seen.add(change_id)
            parts = path.relative_to(entries).parts
            if len(parts) < 3 or not re.fullmatch(r"\d{4}", parts[0]) or not re.fullmatch(r"\d{4}-\d{2}", parts[1]):
                add(findings, "P1", "change-records-detail-path-format", rel, "Detail record should be under entries/YYYY/YYYY-MM/.", "Move it into the required dated directory.")
            text = path.read_text(encoding="utf-8", errors="replace")
            if "| Status |" not in text or not any(f"| {status} |" in text or f"| {status} /" in text for status in CHANGE_RECORD_STATUSES):
                add(findings, "P1", "change-records-detail-status-missing", rel, "Detail record is missing a recognized Status metadata row.", "Add a Status row with a supported status.")
            for section in CHANGE_RECORD_REQUIRED_ENTRY_SECTIONS:
                if section not in text:
                    add(findings, "P1", "change-records-detail-section-missing", rel, f"Detail record is missing {section}.", "Add the required detail record section.")


def result(root: Path, frontmatter: dict[str, Any] | None, findings: list[Finding]) -> dict[str, Any]:
    counts = {severity: sum(1 for item in findings if item.severity == severity) for severity in ["P0", "P1", "P2"]}
    status = "rejected" if counts["P0"] else "review-required" if counts["P1"] else "validated-candidate"
    return {
        "skillRoot": str(root.resolve()),
        "frontmatter": frontmatter,
        "summary": counts,
        "status": status,
        "acceptance": {"authority": "trusted-host-only", "verified": False},
        "findings": [asdict(item) for item in findings],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a Codex Agent Skill package")
    parser.add_argument("skill_folder", type=Path)
    parser.add_argument("--json", type=Path, help="Optional JSON report path")
    parser.add_argument("--require-change-records", action="store_true", help="Require the traceable change-record artifact system.")
    parser.add_argument("--require-gate-contract", action="store_true", help="Require an untrusted gate contract declaration for host promotion review.")
    args = parser.parse_args(argv)
    skill_folder = args.skill_folder.resolve()
    report = validate(skill_folder, require_gate_contract=args.require_gate_contract)
    if args.require_change_records:
        findings = [Finding(**item) for item in report["findings"]]
        validate_change_records(skill_folder, findings, require=True)
        report = result(skill_folder, report["frontmatter"], findings)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["summary"]["P0"] or report["summary"]["P1"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
