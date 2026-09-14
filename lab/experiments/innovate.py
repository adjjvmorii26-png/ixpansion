#!/usr/bin/env python3
"""Innovate — run innovation board in one pass."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
HERE = Path(__file__).resolve().parent
BOARD = ["epoch_weather.py", "testament_diff.py", "spec_gravity.py", "refusal_garden.py", "mercy_protocol.py", "consent_lattice.py", "hex_author.py", "hex_from_consent.py", "hex_from_mercy.py", "hex_bundle.py", "carnival.py",
    "hex_cathedral.py",
    "dashboard_resurrector.py",
    "omnirouter.py"]
def main():
    results = []
    for s in BOARD:
        p = HERE / s
        if not p.exists(): results.append({"m": s, "ok": False}); continue
        args = [sys.executable, str(p)]
        if s == "mercy_protocol.py": args.append("delete ci workflow from stale tip")
        r = subprocess.run(args, capture_output=True, text=True, timeout=45)
        results.append({"m": s, "ok": r.returncode == 0})
    ok = all(x["ok"] for x in results)
    print(json.dumps({"ok": ok, "project": "innovate", "passed": sum(1 for x in results if x["ok"]), "n": len(results), "results": results, "ts": datetime.now(timezone.utc).isoformat()}, indent=2))
    return 0 if ok else 1
if __name__ == "__main__":
    raise SystemExit(main())
