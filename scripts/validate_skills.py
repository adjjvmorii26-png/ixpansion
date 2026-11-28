#!/usr/bin/env python3
"""Static health gate for IXPANSION SKILL.md files (stdlib only)."""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
SECRET_PATTERNS = (
    re.compile(r"\\b\\d{8,}:[A-Za-z0-9_-]{30,}\\b"),
    re.compile(r"\\bgh[pousr]_[A-Za-z0-9]{20,}\\b"),
    re.compile(r"\\bgithub_pat_[A-Za-z0-9_]{20,}\\b"),
    re.compile(r"\\bsk-[A-Za-z0-9]{20,}\\b"),
)
UNSAFE_COMMANDS = (
    re.compile(r"(?im)^\\s*(?:\\d+\\.\\s*)?git\\s+push\\s+(?:origin\\s+)?main\\b"),
    re.compile(r"(?im)^\\s*(?:\\d+\\.\\s*)?vercel\\s+--(?:yes\\s+)?prod\\b"),
    re.compile(r"(?im)^\\s*(?:\\d+\\.\\s*)?git\\s+push\\s+--force\\b"),
)
HIGH_IMPACT = re.compile(r"\\b(?:prune|delete|remove|archive|mutate|deploy|overwrite|publish)\\b", re.I)
SAFETY_CUES = re.compile(r"\\b(?:approval|approved|dry.run|rollback|backup|proposal.only|human review|explicitly authorize)\\b", re.I)
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".tox"}


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    checked: int = 0


def _scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1]
    return value.strip()


def parse_frontmatter(content: str, path: Path, report: Report) -> dict[str, str]:
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        report.errors.append(f"{path}: missing YAML frontmatter")
        return {}
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        report.errors.append(f"{path}: frontmatter is not closed")
        return {}
    fields: dict[str, str] = {}
    for number, line in enumerate(lines[1:end], start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            report.errors.append(f"{path}:{number}: malformed frontmatter field")
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", key):
            report.errors.append(f"{path}:{number}: invalid metadata key")
            continue
        if key in fields:
            report.errors.append(f"{path}:{number}: duplicate '{key}' field")
            continue
        fields[key] = _scalar(value)
    for required in ("name", "description"):
        if not fields.get(required):
            report.errors.append(f"{path}: frontmatter requires non-empty '{required}'")
    name = fields.get("name", "")
    if name and not NAME_RE.fullmatch(name):
        report.errors.append(f"{path}: invalid skill name '{name}'")
    description = fields.get("description", "")
    if description and len(description) < 20:
        report.errors.append(f"{path}: description must be at least 20 characters")
    return fields


def discover_skills(root: Path) -> list[Path]:
    found: list[Path] = []
    for path in root.rglob("SKILL.md"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_symlink() or not path.is_file():
            continue
        found.append(path)
    return sorted(found)


def validate_skills(root: Path) -> Report:
    report = Report()
    if not root.is_dir():
        report.errors.append(f"{root}: repository root does not exist")
        return report
    paths = discover_skills(root)
    if not paths:
        report.errors.append(f"{root}: no SKILL.md files found")
        return report
    names: dict[str, Path] = {}
    for path in paths:
        report.checked += 1
        rel = path.relative_to(root).as_posix()
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            report.errors.append(f"{rel}: cannot read UTF-8 ({type(exc).__name__})")
            continue
        if not content.strip():
            report.errors.append(f"{rel}: empty skill document")
            continue
        metadata = parse_frontmatter(content, Path(rel), report)
        name = metadata.get("name", "")
        if name:
            if name in names:
                report.errors.append(f"{rel}: duplicate skill name '{name}' also used by {names[name]}")
            else:
                names[name] = Path(rel)
        for pattern in SECRET_PATTERNS:
            if pattern.search(content):
                report.errors.append(f"{rel}: possible credential literal detected")
                break
        for pattern in UNSAFE_COMMANDS:
            if pattern.search(content):
                report.errors.append(f"{rel}: direct production/default-branch command requires replacement with an approval-gated workflow")
                break
        if HIGH_IMPACT.search(content) and not SAFETY_CUES.search(content):
            report.warnings.append(f"{rel}: high-impact action language lacks an explicit safety boundary")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--json", action="store_true", help="emit machine-readable report")
    args = parser.parse_args()
    report = validate_skills(args.root.resolve())
    payload = {
        "status": "FAIL" if report.errors else ("WARN" if report.warnings else "PASS"),
        "checked": report.checked,
        "errors": report.errors,
        "warnings": report.warnings,
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for item in report.errors:
            print(f"ERROR: {item}")
        for item in report.warnings:
            print(f"WARNING: {item}")
        print(f"Skill health: {payload['status']} | checked={report.checked} errors={len(report.errors)} warnings={len(report.warnings)}")
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
