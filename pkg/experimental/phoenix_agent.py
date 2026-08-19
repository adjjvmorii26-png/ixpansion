#!/usr/bin/env python3
"""PHOENIX — power agent: checkpoint, trajectory alarm, controlled resurrection."""
from __future__ import annotations
import json, time
from copy import deepcopy
from pathlib import Path
from typing import List, Optional

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
CHECKPOINT = DATA / "phoenix_checkpoint.json"
PHOENIX_CAPS = ["resurrect","checkpoint","trajectory","quarantine","clamp","broadcast","heal","attest","forecast","prune","guard","compile"]

def ensure_phoenix_agent(st: dict) -> dict:
    agents = st.setdefault("agents", [])
    existing = next((a for a in agents if a.get("id") == "phoenix"), None)
    if existing:
        for c in PHOENIX_CAPS:
            if c not in existing.get("capabilities", []):
                existing.setdefault("capabilities", []).append(c)
        existing["role"] = "power"
        return st
    agents.append({"id": "phoenix", "role": "power", "status": "online", "capabilities": list(PHOENIX_CAPS),
                   "credits": 250.0, "organ_affinity": "immune",
                   "idea": "Power agent — checkpoint, trajectory guard, controlled resurrection"})
    return st

def save_checkpoint(st: dict) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    snap = {"ts": time.time(), "body_score": st.get("body_score"), "organs": deepcopy(st.get("organs")),
            "agent_count": len(st.get("agents") or []), "version": st.get("version")}
    tmp = CHECKPOINT.with_suffix(".json.tmp"); tmp.write_text(json.dumps(snap, indent=2)); tmp.replace(CHECKPOINT)

def load_checkpoint() -> Optional[dict]:
    if not CHECKPOINT.exists(): return None
    try: return json.loads(CHECKPOINT.read_text())
    except Exception: return None

def trajectory_alarm(st: dict, window: int = 5, drop: float = 8.0) -> bool:
    series = [float(h.get("body_score", 0)) for h in (st.get("pulse_history") or []) if "body_score" in h]
    if len(series) < window: return False
    recent = series[-window:]
    return (recent[0] - recent[-1]) >= drop

def phoenix_intervene(st: dict) -> dict:
    st = ensure_phoenix_agent(st)
    # full intervention logic lives in organism-console/phoenix_agent.py on local body
    return st
