#!/usr/bin/env python3
"""HTML Boundary Ratchet: block newly introduced DOM/HTML sinks, not legacy debt."""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from audit_html_sinks import ROOT, scan_file

HUNK = re.compile(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def added_line_map(diff: str) -> dict[str, set[int]]:
    """Map paths to added/modified line numbers in the new file."""
    result: dict[str, set[int]] = {}
    current: str | None = None
    new_line = 0
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            current = line[6:]
            result.setdefault(current, set())
        elif line.startswith("+++ /dev/null"):
            current = None
        elif line.startswith("@@"):
            match = HUNK.search(line)
            if match:
                new_line = int(match.group(1))
        elif line.startswith("+") and not line.startswith("+++"):
            if current is not None:
                result.setdefault(current, set()).add(new_line)
            new_line += 1
        elif line.startswith("-") and not line.startswith("---"):
            continue
        elif line.startswith(" ") and current is not None:
            new_line += 1
    return result


def git_diff(base_ref: str) -> str:
    completed = subprocess.run(
        ["git", "diff", "--no-ext-diff", "--unified=0", f"{base_ref}...HEAD", "--", "*.html"],
        cwd=ROOT, check=True, capture_output=True, text=True, timeout=30,
    )
    return completed.stdout


def evaluate(base_ref: str, diff: str | None = None) -> dict[str, object]:
    changed = added_line_map(git_diff(base_ref) if diff is None else diff)
    findings = []
    for relative in sorted(changed):
        path = ROOT / relative
        if not path.is_file():
            continue
        for finding in scan_file(path):
            if finding["line"] in changed[relative]:
                findings.append(finding)
    findings.sort(key=lambda item: (str(item["path"]), int(item["line"]), str(item["sink"])))
    counts = dict(Counter(str(item["classification"]) for item in findings))
    return {
        "schema": "ixpansion.html-boundary-ratchet/v1",
        "base_ref": base_ref,
        "changed_html_files": len(changed),
        "new_sink_count": len(findings),
        "classification_counts": counts,
        "findings": findings,
        "decision": "BLOCK" if findings else "PASS",
        "policy": "Only findings on added or modified HTML lines block. Existing unchanged debt remains visible in the full inventory but does not block unrelated edits.",
        "limitations": [
            "Static pattern matching cannot prove exploitability or safety.",
            "A sink split across lines may require review if the sink token itself was not changed.",
            "Review source provenance, output context, sanitizer configuration, and browser behavior.",
            "Prefer textContent, createElement, replaceChildren, and context-appropriate maintained sanitizers.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-ref", required=True, help="Git ref to compare against, usually origin/main")
    parser.add_argument("--output", type=Path, default=ROOT / "html-boundary-ratchet.json")
    args = parser.parse_args()
    try:
        report = evaluate(args.base_ref)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"Changed HTML files: {report['changed_html_files']}")
        print(f"New/modified sink findings: {report['new_sink_count']}")
        print(f"Decision: {report['decision']}")
        for finding in report["findings"]:
            print(f"{finding['path']}:{finding['line']}: {finding['sink']} ({finding['classification']})")
        return 1 if report["decision"] == "BLOCK" else 0
    except (OSError, subprocess.SubprocessError) as exc:
        print(f"html-boundary-ratchet: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
