"""Read-only validator for exported skill registry snapshots."""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REQUIRED = ("id", "slug", "title", "provider", "source_of_truth", "evidence_state")
ALLOWED_EVIDENCE = {"NOT_RUN", "PARTIAL", "VERIFIED", "BLOCKED", "CONFLICTING", "PENDING"}
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def validate_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate records without mutating them or changing any canonical source."""
    findings: list[dict[str, str]] = []
    valid_records = [record for record in records if isinstance(record, dict)]
    ids = Counter(str(r.get("id", "")).strip() for r in valid_records if r.get("id"))
    slugs = Counter(str(r.get("slug", "")).strip() for r in valid_records if r.get("slug"))
    known_ids = set(ids)

    def add(code: str, severity: str, record: str, detail: str) -> None:
        findings.append({"code": code, "severity": severity,
                         "record": record or "<unknown>", "detail": detail})

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            add("INVALID_RECORD", "error", str(index), "Record must be a JSON object.")
            continue
        rid = str(record.get("id", "")).strip()
        label = rid or str(record.get("title", "")).strip() or str(index)
        for field in REQUIRED:
            if not str(record.get(field, "")).strip():
                add("MISSING_FIELD", "error", label, f"Required field '{field}' is empty.")
        if rid and ids[rid] > 1:
            add("DUPLICATE_ID", "error", label, f"ID '{rid}' occurs {ids[rid]} times.")
        slug = str(record.get("slug", "")).strip()
        if slug and not SLUG_RE.fullmatch(slug):
            add("INVALID_SLUG", "error", label, f"Slug '{slug}' is not normalized kebab-case.")
        if slug and slugs[slug] > 1:
            add("DUPLICATE_SLUG", "error", label, f"Slug '{slug}' occurs {slugs[slug]} times.")
        evidence = str(record.get("evidence_state", "")).strip()
        if evidence and evidence not in ALLOWED_EVIDENCE:
            add("UNKNOWN_EVIDENCE_STATE", "error", label, f"Unsupported evidence state '{evidence}'.")
        dependencies = record.get("dependencies", [])
        if dependencies is None:
            dependencies = []
        if not isinstance(dependencies, list):
            add("INVALID_DEPENDENCIES", "error", label, "'dependencies' must be a list of skill IDs.")
            dependencies = []
        for dependency in dependencies:
            if not isinstance(dependency, str) or dependency not in known_ids:
                add("ORPHAN_DEPENDENCY", "error", label, f"Dependency '{dependency}' is not present in this snapshot.")
        binding = record.get("runtime_binding")
        if not isinstance(binding, str) or not binding.strip() or binding == "unknown":
            add("UNDECLARED_RUNTIME_BINDING", "warning", label, "Runtime binding status must be explicit.")
        if evidence in {"NOT_RUN", "PARTIAL", "PENDING"}:
            add("INCOMPLETE_EVIDENCE", "warning", label, f"Evidence state is {evidence}; do not promote as tested.")

    findings.sort(key=lambda f: (f["severity"], f["code"], f["record"], f["detail"]))
    errors = sum(f["severity"] == "error" for f in findings)
    warnings = sum(f["severity"] == "warning" for f in findings)
    return {"schema_version": "1.0", "mode": "read_only", "record_count": len(records),
            "error_count": errors, "warning_count": warnings,
            "promotion_allowed": errors == 0 and warnings == 0, "findings": findings}


def load_snapshot(path: str | Path) -> list[Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        payload = payload.get("skills")
    if not isinstance(payload, list):
        raise ValueError("Snapshot must be a JSON array or an object with a 'skills' array.")
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", help="JSON snapshot file")
    parser.add_argument("--output", help="Optional report path; never overwrites input")
    args = parser.parse_args(argv)
    try:
        source = Path(args.snapshot).resolve()
        report = validate_records(load_snapshot(source))
        rendered = json.dumps(report, indent=2, sort_keys=True) + "\\n"
        if args.output:
            destination = Path(args.output).resolve()
            if destination == source:
                print("refusing to overwrite input snapshot", file=sys.stderr)
                return 2
            destination.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"snapshot error: {exc}", file=sys.stderr)
        return 2
    return 1 if report["error_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
