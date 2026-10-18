#!/usr/bin/env python3
"""Inventory potentially unsafe HTML/DOM sinks without modifying source files.

This is a review aid, not a proof of exploitability: context, sanitization, and
trusted static templates still require human review.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {".git", "node_modules", ".venv", "venv", "dist", "build"}
SINKS = [
    ("innerHTML", re.compile(r"\.innerHTML\s*(?:=|\+=)")),
    ("outerHTML", re.compile(r"\.outerHTML\s*(?:=|\+=)")),
    ("insertAdjacentHTML", re.compile(r"\.insertAdjacentHTML\s*\(")),
    ("document.write", re.compile(r"\bdocument\.write(?:ln)?\s*\(")),
    ("eval", re.compile(r"\beval\s*\(")),
    ("inline-handler", re.compile(r"\bon(?:click|error|load|mouseover|focus|submit|change|input)\s*=", re.I)),
]
EMPTY_RESET = re.compile(r"""^\s*(['"])\s*\1\s*;?\s*$""")
DYNAMIC_MARKERS = ("$" + "{", " + ", "+'", '+"', ".concat(")


def classify(kind: str, content: str, start: int, match_end: int) -> str:
    if kind == "innerHTML":
        assignment = re.match(r"\s*=\s*([^;\n]*)", content[match_end - 1 : match_end + 240])
        if assignment and EMPTY_RESET.match(assignment.group(1)):
            return "safe-reset"
    window = content[max(0, start - 80) : min(len(content), match_end + 1000)]
    if any(marker in window for marker in DYNAMIC_MARKERS):
        return "dynamic-review"
    return "manual-review"


def scan_file(path: Path) -> list[dict[str, object]]:
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    findings: list[dict[str, object]] = []
    lines = content.splitlines()
    for kind, pattern in SINKS:
        for match in pattern.finditer(content):
            classification = classify(kind, content, match.start(), match.end())
            if classification == "safe-reset":
                continue
            line = content.count("\n", 0, match.start()) + 1
            excerpt = lines[line - 1].strip()[:180] if line <= len(lines) else ""
            findings.append({
                "path": path.relative_to(ROOT).as_posix(),
                "line": line,
                "sink": kind,
                "classification": classification,
                "excerpt": excerpt,
            })
    return findings


def main() -> int:
    html_files = [
        path for path in ROOT.rglob("*.html")
        if not any(part in EXCLUDED for part in path.parts)
    ]
    findings = [item for path in html_files for item in scan_file(path)]
    findings.sort(key=lambda item: (str(item["path"]), int(item["line"]), str(item["sink"])))
    counts: dict[str, int] = {}
    for item in findings:
        key = str(item["classification"])
        counts[key] = counts.get(key, 0) + 1
    report = {
        "html_files_scanned": len(html_files),
        "finding_count": len(findings),
        "classification_counts": counts,
        "findings": findings,
        "limitations": [
            "Static pattern matching cannot prove exploitability or safety.",
            "Dynamic-review findings require tracing data sources and output context.",
            "Safe DOM APIs, maintained sanitizers, and allowlisted attributes are preferred.",
        ],
    }
    out = ROOT / "html-sink-audit.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"HTML files scanned: {len(html_files)}")
    print(f"Sink candidates: {len(findings)}")
    for key in sorted(counts):
        print(f"  {key}: {counts[key]}")
    print(f"Report: {out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
