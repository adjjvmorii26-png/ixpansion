#!/usr/bin/env python3
"""Lifecycle manager for neuro-swarm micro-agents."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

AGENTS = Path(__file__).resolve().parent / "agents"
REGISTRY = {
    "scout": AGENTS / "scout_agent" / "behavior.py",
    "builder": AGENTS / "builder_agent" / "construct.py",
    "sentinel": AGENTS / "sentinel_agent" / "defend.py",
}

def run_agent(name: str, *args) -> dict:
    path = REGISTRY.get(name)
    if not path or not path.exists():
        return {"ok": False, "err": f"unknown agent {name}"}
    r = subprocess.run([sys.executable, str(path)] + list(args), capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"ok": r.returncode == 0, "out": (r.stdout or "")[-200:]}

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "scout"
    print(json.dumps(run_agent(name, *sys.argv[2:]), indent=2))
