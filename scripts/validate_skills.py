#!/usr/bin/env python3
"""Validate the IXPANSION reusable-skill directory without breaking legacy skills.

Legacy SKILL.md files without YAML frontmatter remain accepted with a warning.
When frontmatter exists, its name and description must be valid and names unique.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
KEY_RE = re.compile(r"^(name|description):\\s*(.*?)\\s*$")


@dataclass
class Report:
    errors: list[str]
    warnings: list[str]
    checked: int = 0


def _frontmatter(text: str, path: Path, report: Report) -> dict[str, str] | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        report.warnings.append(f"{path}: legacy skill has no YAML frontmatter")
        return None
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        report.errors.append(f"{path}: frontmatter is not closed")
        return {}
    values: dict[str, str] = {}
    for line_no, line in enumerate(lines[1:end], start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = KEY_RE.match(line)
        if not match:
            continue
        key, value = match.groups()
        if key in values:
            report.errors.append(f"{path}:{line_no}: duplicate '{key}' field")
        values[key] = value.strip().strip('"').strip("'")
    return values


def validate_skills(root: Path) -> Report:
    report = Report(errors=[], warnings=[])
    skills_root = root / "skills"
    if not skills_root.is_dir():
        report.errors.append(f"{skills_root}: skills directory not found")
        return report

    manifests = sorted(p for p in skills_root.rglob("SKILL.md") if p.is_file())
    if not manifests:
        report.errors.append(f"{skills_root}: no SKILL.md files found")
        return report

    names: dict[str, Path] = {}
    for path in manifests:
        report.checked += 1
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            report.errors.append(f"{path}: cannot read UTF-8 content ({exc})")
            continue
        if not content.strip():
            report.errors.append(f"{path}: file is empty")
            continue

        metadata = _frontmatter(content, path.relative_to(root), report)
        if metadata is None:
            continue
        name = metadata.get("name", "")
        description = metadata.get("description", "")
        if not name:
            report.errors.append(f"{path}: frontmatter requires a non-empty name")
        elif not NAME_RE.fullmatch(name):
            report.errors.append(f"{path}: invalid skill name '{name}'")
        else:
            previous = names.get(name)
            if previous:
                report.errors.append(
                    f"{path}: duplicate skill name '{name}' also used by {previous}"
                )
            else:
                names[name] = path
        if not description:
            report.errors.append(f"{path}: frontmatter requires a non-empty description")
        elif len(description) < 12:
            report.errors.append(f"{path}: description is too short (minimum 12 characters)")

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(),
                        help="repository root (defaults to current directory)")
    args = parser.parse_args()
    report = validate_skills(args.root.resolve())
    for warning in report.warnings:
        print(f"WARNING: {warning}")
    for error in report.errors:
        print(f"ERROR: {error}")
    print(
        f"Skill manifest: checked={report.checked}, "
        f"errors={len(report.errors)}, warnings={len(report.warnings)}"
    )
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
