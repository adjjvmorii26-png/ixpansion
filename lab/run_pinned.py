#!/usr/bin/env python3
"""Run pinned lab projects from lab/pinned_projects.json."""
from __future__ import annotations
import argparse, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path(__file__).resolve().parent / "pinned_projects.json"
REPORT = Path(__file__).resolve().parent / "pinned_report.json"
LEDGER = ROOT / "lab" / "unique_path" / "proof_ledger.jsonl"

def main_with(argv: list[str] | None = None) -> int:
    sys.argv = [sys.argv[0], *(argv or [])]
    return main()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--critical-only", action="store_true")
    ap.add_argument("--fail-fast", action="store_true")
    args = ap.parse_args()
    data = json.loads(MANIFEST.read_text())
    results = []
    ok_all = True
    for p in data.get("projects") or []:
        if args.critical_only and not p.get("critical"):
            continue
        path = ROOT / p["path"]
        if not path.exists():
            entry = {"id": p["id"], "ok": False, "err": "missing", "critical": bool(p.get("critical"))}
            results.append(entry)
            if p.get("critical"):
                ok_all = False
            if args.fail_fast and p.get("critical"):
                break
            continue
        r = subprocess.run(
            [sys.executable, str(path)] + list(p.get("args") or []),
            capture_output=True, text=True, cwd=str(ROOT),
        )
        entry = {"id": p["id"], "ok": r.returncode == 0, "code": r.returncode, "critical": bool(p.get("critical"))}
        results.append(entry)
        if not entry["ok"] and p.get("critical"):
            ok_all = False
            if args.fail_fast:
                break
    report = {"ts": datetime.now(timezone.utc).isoformat(), "ok": ok_all, "results": results}
    REPORT.write_text(json.dumps(report, indent=2) + "\n")
    try:
        LEDGER.parent.mkdir(parents=True, exist_ok=True)
        with LEDGER.open("a") as f:
            f.write(json.dumps({"ts": report["ts"], "type": "pinned_run", "ref": f"ok={ok_all}", "n": len(results)}) + "\n")
    except OSError:
        pass
    print(json.dumps(report, indent=2))
    return 0 if ok_all else 1

if __name__ == "__main__":
    raise SystemExit(main())
