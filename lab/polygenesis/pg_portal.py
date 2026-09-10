#!/usr/bin/env python3
"""Polygenesis portal — boot / genome / cells / agents / ethics / sim."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
ACTS = {
    "genome": ROOT / "genome" / "genome_engine.py",
    "cells": ROOT / "organism" / "cells_engine.py",
    "agents": ROOT / "agents" / "agent_kernel.py",
    "ethics": ROOT / "ethics" / "ethics_gate.py",
    "sim": ROOT / "simulation" / "sim_runner.py",
}

def boot() -> dict:
    steps = []
    ok = True
    for name in ("ethics", "genome", "cells", "agents"):
        r = subprocess.run([sys.executable, str(ACTS[name])], capture_output=True, text=True)
        steps.append({"step": name, "ok": r.returncode == 0})
        ok &= r.returncode == 0
    ledger = REPO / "lab" / "unique_path" / "proof_ledger.jsonl"
    try:
        ledger.parent.mkdir(parents=True, exist_ok=True)
        with ledger.open("a") as f:
            f.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(), "type": "polygenesis_boot", "ref": f"ok={ok}"}) + "\n")
    except OSError:
        pass
    return {"boot": True, "ok": ok, "steps": steps}

def main() -> int:
    act = (sys.argv[1] if len(sys.argv) > 1 else "help").lower()
    if act in ("help", "-h", "--help"):
        print(json.dumps({"acts": sorted(list(ACTS) + ["boot"]), "usage": "python pg_portal.py <act>"}, indent=2))
        return 0
    if act == "boot":
        print(json.dumps(boot(), indent=2))
        return 0
    if act == "sim":
        name = sys.argv[2] if len(sys.argv) > 2 else "growth"
        r = subprocess.run([sys.executable, str(ACTS["sim"]), name], capture_output=True, text=True)
        print(r.stdout or r.stderr)
        return r.returncode
    if act not in ACTS:
        print(json.dumps({"ok": False, "err": "unknown act"}))
        return 1
    r = subprocess.run([sys.executable, str(ACTS[act])] + sys.argv[2:], capture_output=True, text=True)
    print(r.stdout or r.stderr)
    return r.returncode

if __name__ == "__main__":
    raise SystemExit(main())
