#!/usr/bin/env python3
"""Neuro-Swarm OS portal — map acts to modules."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ACTS = {
    "route": ROOT / "NEURAL_SUBSTRATE" / "dendrite_engine.py",
    "fire": ROOT / "NEURAL_SUBSTRATE" / "synapse_runtime" / "fire.py",
    "scout": ROOT / "AGENT_SWARM" / "swarm_kernel.py",
    "scan": ROOT / "SELF_HEALING_PIPELINE" / "diagnostics" / "scan.py",
    "grow": ROOT / "QUANTUM_SAFE_LAYER" / "hash_forest" / "grow.py",
    "connect": ROOT / "CLOUD_MESH" / "node" / "connect.py",
    "branch": ROOT / "TEMPORAL_EXECUTION" / "timeline_superposed" / "branch.py",
}

def main() -> int:
    act = (sys.argv[1] if len(sys.argv) > 1 else "help").lower()
    if act in ("help", "-h", "--help") or act not in ACTS:
        print(json.dumps({"acts": sorted(ACTS), "usage": "python nsos_portal.py <act>"}, indent=2))
        return 0 if act in ("help", "-h", "--help") else 1
    extra = sys.argv[2:]
    if act == "scout":
        extra = ["scout"] + extra
    r = subprocess.run([sys.executable, str(ACTS[act])] + extra, capture_output=True, text=True)
    print(r.stdout or r.stderr)
    return r.returncode

if __name__ == "__main__":
    raise SystemExit(main())
