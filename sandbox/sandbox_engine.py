#!/usr/bin/env python3
"""
IXPANSION Sandbox Engine
------------------------
Lightweight local tick loop for mesh / NEXUS experiments.
Usage:
  python sandbox_engine.py --ticks 10
  python sandbox_engine.py --status
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

STATE_PATH = Path(__file__).resolve().parent / "sandbox_state.json"


def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {
        "ticks": 0,
        "organisms": 1000,
        "last_tick_ms": 0.0,
        "status": "idle",
        "version": "IXPANSION/sandbox-1.0",
    }


def save_state(st: dict) -> None:
    STATE_PATH.write_text(json.dumps(st, indent=2))


def run_ticks(n: int) -> dict:
    st = load_state()
    st["status"] = "running"
    t0 = time.perf_counter()
    energy = 100.0
    for i in range(n):
        energy = max(0.0, energy - 0.05 * (1 + (i % 7) * 0.01))
        st["ticks"] += 1
        st["organisms"] = 1000 + (st["ticks"] % 50) - 25
    elapsed_ms = (time.perf_counter() - t0) * 1000
    st["last_tick_ms"] = round(elapsed_ms, 3)
    st["energy"] = round(energy, 3)
    st["status"] = "idle"
    save_state(st)
    return st


def status() -> dict:
    st = load_state()
    try:
        from mesh_core import IXPANSIONMesh
        m = IXPANSIONMesh(2)
        st["mesh_leader"] = m.leader_id
        st["mesh_nodes"] = len(m.nodes)
    except Exception as e:
        st["mesh"] = f"unavailable:{e.__class__.__name__}"
    return st


def main():
    p = argparse.ArgumentParser(description="IXPANSION sandbox engine")
    p.add_argument("--ticks", type=int, default=0, help="Run N simulation ticks")
    p.add_argument("--status", action="store_true", help="Print sandbox status")
    args = p.parse_args()

    if args.ticks > 0:
        st = run_ticks(args.ticks)
        print(json.dumps({"ok": True, "ran_ticks": args.ticks, "state": st}, indent=2))
    if args.status or args.ticks == 0:
        st = status()
        print(json.dumps({"ok": True, "status": st}, indent=2))


if __name__ == "__main__":
    main()
