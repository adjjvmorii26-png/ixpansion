#!/usr/bin/env python3
"""Inventory potentially dangerous HTML/DOM sinks.

This is a triage aid, not a vulnerability detector. Every hit needs manual
source-to-sink review. Uses only the Python standard library.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

PATTERNS = {
    "innerHTML": re.compile(r"\.innerHTML\s*(?:\+?=)"),
    "outerHTML": re.compile(r"\.outerHTML\s*="),
    "insertAdjacentHTML": re.compile(r"\.insertAdjacentHTML\s*\("),
    "document.write": re.compile(r"\bdocument\.write(?:ln)?\s*\("),
    "srcdoc": re.compile(r"\bsrcdoc\s*="),
    "string_template_candidate": re.compile(r"(?:innerHTML|outerHTML)\s*=\s*[\x60'\"]"),
}
DEFAULT_IGNORES = {".git", "node_modules", "vendor", "dist", "build", ".venv", "venv", "__pycache__"}


def iter_html_files(root: Path, paths: list[str]):
    candidates = []
    roots = [root / p for p in paths] if paths else [root]
    for start in roots:
        if start.is_file() and start.suffix.lower() in {".html", ".htm"}:
            candidates.append(start)
            continue
        if not start.exists():
            continue
        for path in start.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".html", ".htm"}:
                continue
            if any(part in DEFAULT_IGNORES for part in path.parts):
                continue
            candidates.append(path)
    yield from sorted(set(candidates))


def scan_file(path: Path, root: Path):
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    findings = []
    for number, line in enumerate(lines, 1):
        for name, pattern in PATTERNS.items():
            if pattern.search(line):
                findings.append({
                    "path": path.relative_to(root).as_posix(),
                    "line": number,
                    "candidate": name,
                    "context": line.strip()[:300],
                    "classification": "UNTRIAGED_CANDIDATE",
                })
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root (default: current directory)")
    parser.add_argument("--path", action="append", default=[], help="File or directory to scan; repeatable")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    findings = [item for file in iter_html_files(root, args.path) for item in scan_file(file, root)]
    if args.format == "json":
        print(json.dumps({"scope": args.path or ["."], "candidate_count": len(findings),
                          "warning": "Candidates are not confirmed vulnerabilities.", "findings": findings},
                         indent=2))
    else:
        print(f"HTML sink candidates: {len(findings)} (not confirmed vulnerabilities)")
        for item in findings:
            print(f"{item['path']}:{item['line']}: {item['candidate']} :: {item['context']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
