#!/usr/bin/env python3
"""Run pinned Chrono Forge projects from a versioned manifest."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from lab.runtime_vault import append_jsonl, ledger_path, report_path, write_json

MANIFEST = Path(__file__).resolve().parent / "pinned_projects.json"
REPORT = report_path("pinned-report.json")
LEDGER = ledger_path()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--critical-only", action="store_true")
    parser.add_argument("--fail-fast", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    results: list[dict[str, object]] = []
    ok_all = True
    for project in data.get("projects") or []:
        if args.critical_only and not project.get("critical"):
            continue
        script = ROOT / project["path"]
        if not script.is_file():
            results.append({
                "id": project["id"], "ok": False, "err": "missing",
                "critical": bool(project.get("critical")),
            })
            if project.get("critical"):
                ok_all = False
                if args.fail_fast:
                    break
            continue
        completed = subprocess.run(
            [sys.executable, str(script), *map(str, project.get("args") or [])],
            capture_output=True, text=True, cwd=str(ROOT), check=False,
        )
        entry = {
            "id": project["id"], "ok": completed.returncode == 0,
            "code": completed.returncode, "critical": bool(project.get("critical")),
        }
        results.append(entry)
        if not entry["ok"] and entry["critical"]:
            ok_all = False
            if args.fail_fast:
                break
    timestamp = datetime.now(timezone.utc).isoformat()
    report = {"ts": timestamp, "ok": ok_all, "results": results}
    write_json(REPORT, report)
    append_jsonl(LEDGER, {
        "ts": timestamp, "type": "pinned_run", "ref": f"ok={ok_all}", "n": len(results),
    })
    print(json.dumps(report, indent=2))
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
