#!/usr/bin/env python3
"""Inventory potentially dangerous HTML/DOM sinks.

This is a triage aid, not a vulnerability detector. Every hit needs manual
source-to-sink review. Uses only the Python standard library.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

PATTERNS = {
    "innerHTML": re.compile(r"\\.innerHTML\\s*(?:\\+?=)"),
    "outerHTML": re.compile(r"\\.outerHTML\\s*="),
    "insertAdjacentHTML": re.compile(r"\\.insertAdjacentHTML\\s*\\("),
    "document.write": re.compile(r"\\bdocument\\.write(?:ln)?\\s*\\("),
    "srcdoc": re.compile(r"\\bsrcdoc\\s*="),
    "event_handler_attribute": re.compile(r"\\bon[a-z]+\\s*=", re.IGNORECASE),
    "javascript_url": re.compile(r"""(?:href|src|action|formaction)\\s*=\\s*["\\']?\\s*javascript\\s*:""", re.IGNORECASE),
    "string_template_candidate": re.compile(r"(?:innerHTML|outerHTML)\\s*=\\s*[\\x60'\\"]"),
}
DEFAULT_IGNORES = {".git", "node_modules", "vendor", "dist", "build", ".venv", "venv", "__pycache__"}


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError, RuntimeError):
        return False


def _has_symlink_component(path: Path, root: Path) -> bool:
    """Reject symlinks in the requested path, not merely the final file."""
    try:
        relative = path.relative_to(root)
    except ValueError:
        return True
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            return True
    return False


def iter_html_files(root: Path, paths: list[str]):
    root = root.resolve()
    candidates = set()
    roots = [root / p for p in paths] if paths else [root]
    for requested in roots:
        if not _is_within(requested, root) or _has_symlink_component(requested, root):
            continue
        start = requested.resolve()
        if start.is_file():
            if start.suffix.lower() in {".html", ".htm"}:
                candidates.add(start)
            continue
        if not start.is_dir():
            continue
        for current, dirs, files in os.walk(start, followlinks=False):
            current_path = Path(current)
            dirs[:] = sorted(
                name for name in dirs
                if name not in DEFAULT_IGNORES
                and not (current_path / name).is_symlink()
            )
            for name in files:
                path = current_path / name
                if path.suffix.lower() not in {".html", ".htm"} or path.is_symlink():
                    continue
                if _is_within(path, root):
                    candidates.add(path.resolve())
    yield from sorted(candidates)


def scan_file(path: Path, root: Path):
    root = root.resolve()
    if not _is_within(path, root) or _has_symlink_component(path, root):
        return []
    path = path.resolve()
    try:
        relative = path.relative_to(root).as_posix()
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except (OSError, ValueError, RuntimeError):
        return []
    findings = []
    for number, line in enumerate(lines, 1):
        for name, pattern in PATTERNS.items():
            if pattern.search(line):
                findings.append({
                    "path": relative,
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
