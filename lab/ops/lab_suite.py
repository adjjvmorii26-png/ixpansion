#!/usr/bin/env python3
"""Lab Suite v2 — run creative + memory organs in order."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
OPS = Path(__file__).resolve().parent
JOBS = [
    ("ticket", ["epoch_ticket.py", "issue", "--ttl", "3600"]),
    ("smoke", None),
    ("graft", ["pr_graft_advisor.py"]),
    ("scar", ["route_scar.py"]),
    ("silence", ["silence_ledger.py"]),
    ("tide", ["proof_tide.py"]),
    ("weather", ["glyph_weather.py"]),
    ("choir", ["absence_choir.py"]),
    ("compass", ["invert_compass.py"]),
    ("constellation", ["lab_constellation.py"]),
    ("dual", ["dual_track_card.py"]),
    ("heartbeat", ["lab_heartbeat.py"]),
    ("echo", ["echo_archive.py"]),
]
def run_args(args):
    r = subprocess.run([sys.executable, *args], capture_output=True, text=True, timeout=90)
    return r.returncode == 0
def main():
    results, ok = [], True
    for name, args in JOBS:
        if name == "smoke":
            script = REPO / "lab" / "smoke_lab.py"
            good = run_args([str(script)]) if script.exists() else False
        else:
            script = OPS / args[0]
            if not script.exists():
                results.append({"name": name, "ok": False, "err": "missing"}); ok = False; continue
            good = run_args([str(script), *args[1:]])
        results.append({"name": name, "ok": good}); ok &= good
    out = {"ok": ok, "suite": "lab_suite_v2", "n": len(results), "passed": sum(1 for r in results if r["ok"]), "results": results, "ts": datetime.now(timezone.utc).isoformat()}
    print(json.dumps(out, indent=2)); return 0 if ok else 1
if __name__ == "__main__":
    raise SystemExit(main())
