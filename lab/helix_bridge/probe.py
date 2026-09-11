#!/usr/bin/env python3
"""Helix Bridge HB-1 — probe organism portals into constellation.json."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "constellation.json"
PROBES = [
    ("chronoforge", REPO / "lab" / "CHRONOFORGE" / "runtime" / "cf_portal.py", ["ethics"]),
    ("stratum", REPO / "lab" / "STRATUM_ENGINE" / "runtime" / "se_portal.py", ["ethics"]),
    ("monolith", REPO / "lab" / "MONOLITH_STACK" / "runtime" / "ms_portal.py", ["ethics"]),
    ("polygenesis", REPO / "lab" / "polygenesis" / "pg_portal.py", ["ethics"]),
    ("chronoweave", REPO / "lab" / "chronoweave" / "cw_portal.py", ["ethics"]),
    ("paradox", REPO / "lab" / "paradox_forge" / "pf_portal.py", ["ethics"]),
]
def probe_one(name, script, args):
    if not script.exists():
        return {"name": name, "status": "skip", "ok": True}
    r = subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True, timeout=45)
    return {"name": name, "status": "run", "ok": r.returncode == 0, "code": r.returncode}
def main():
    nodes = [probe_one(n, p, a) for n, p, a in PROBES]
    ok = all(n.get("ok") for n in nodes)
    constellation = {"protocol": "HB-1", "ts": datetime.now(timezone.utc).isoformat(), "ok": ok, "nodes": nodes, "channel": "@CoodingLooop", "doctrine": "ethics_first_soft_skip"}
    OUT.write_text(json.dumps(constellation, indent=2) + "\n")
    ledger = REPO / "lab" / "unique_path" / "proof_ledger.jsonl"
    try:
        ledger.parent.mkdir(parents=True, exist_ok=True)
        with ledger.open("a") as f:
            f.write(json.dumps({"ts": constellation["ts"], "type": "helix_bridge", "ok": ok}) + "\n")
    except OSError:
        pass
    print(json.dumps(constellation, indent=2))
    return 0 if ok else 1
if __name__ == "__main__":
    raise SystemExit(main())
