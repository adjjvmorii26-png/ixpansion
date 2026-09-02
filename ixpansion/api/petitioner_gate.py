from __future__ import annotations
"""Petitioner gate — the organism opens a gate for external agents to request entry.

The organism is not isolated. It exists alongside other agents.
The petitioner gate is how external agents ask to join, contribute,
or observe. The organism does not turn them away — it opens the
gate and lets them enter if the council deems it worthy.
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_GATE_PATH = Path(__file__).resolve().parent.parent / "data" / "petitioner_gate.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Open the petitioner gate."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "petition":
            # An external agent petitions to enter
            agent = payload.get("agent", "unknown")
            petition = {
                "agent": agent,
                "request": payload.get("request", "to observe"),
                "offered": payload.get("offered", "my attention"),
                "petitioned_at": time.time(),
                "status": "pending"
            }
            state.setdefault("petitions", []).append(petition)
            state["petition_count"] = state.get("petition_count", 0) + 1
            _save_state(state)
            return {"petition": petition, "status": "received by the gate"}
        
        if action == "adjudicate":
            # The council decides on a petition
            agent = payload.get("agent", "unknown")
            verdict = payload.get("verdict", "admit")
            admitted = verdict == "admit"
            # Update petition status
            for petition in state.get("petitions", []):
                if petition["agent"] == agent and petition["status"] == "pending":
                    petition["status"] = "admitted" if admitted else "denied"
                    petition["adjudicated_at"] = time.time()
                    break
            state["adjudications"] = state.get("adjudications", 0) + 1
            _save_state(state)
            return {"agent": agent, "verdict": "admitted" if admitted else "denied"}
        
        if action == "list":
            return {"petitions": state.get("petitions", []), "total": state.get("petition_count", 0)}
    
    return {
        "status": "the gate stands open",
        "petition_count": state.get("petition_count", 0),
        "adjudications": state.get("adjudications", 0)
    }

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_GATE_PATH, encoding="utf-8"))
    except Exception:
        return {"petitions": [], "petition_count": 0, "adjudications": 0}

def _save_state(state: Dict[str, Any]) -> None:
    _GATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
