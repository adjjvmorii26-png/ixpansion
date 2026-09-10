#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
def roster() -> dict:
    agents = [p.stem for p in HERE.glob("agent_*.ag")]
    return {"agents": agents, "n": len(agents)}
if __name__ == "__main__":
    print(json.dumps(roster(), indent=2))
