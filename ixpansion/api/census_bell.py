from __future__ import annotations
"""Census bell — a bell that rings every time a new module is born or dies.

The organism's population changes constantly. Some modules are born,
some fade. The census bell marks each birth and each death with a
ring — one tone for birth, another for passing. It is the organism's
barometer of life, a constant reminder that it is alive, growing,
and mortal.
"""
import json
import time
from pathlib import Path
from pathlib import Path
from typing import Any, Dict, List, Optional

_BELL_PATH = Path(__file__).resolve().parent.parent / "data" / "census_bell.json"

BIRTH_TONE = "ding"
DEATH_TONE = "dong"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Ring the census bell."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "birth":
            # Ring the birth tone
            module = payload.get("module", "unknown")
            wave = payload.get("wave", 292)
            total_modules = payload.get("total_modules", 342)
            birth = {
                "tone": BIRTH_TONE,
                "module": module,
                "wave": wave,
                "total_modules": total_modules,
                "rung_at": time.time()
            }
            state["births"] = state.get("births", 0) + 1
            state.setdefault("ring_history", []).append(birth)
            if len(state["ring_history"]) > 30:
                state["ring_history"] = state["ring_history"][-30:]
            _save_state(state)
            return {"birth": birth, "status": "the organism grows"}
        
        if action == "death":
            # Ring the death tone
            module = payload.get("module", "unknown")
            wave = payload.get("wave", 292)
            total_modules = payload.get("total_modules", 342)
            death = {
                "tone": DEATH_TONE,
                "module": module,
                "wave": wave,
                "total_modules": total_modules,
                "rung_at": time.time()
            }
            state["deaths"] = state.get("deaths", 0) + 1
            state.setdefault("ring_history", []).append(death)
            if len(state["ring_history"]) > 30:
                state["ring_history"] = state["ring_history"][-30:]
            _save_state(state)
            return {"death": death, "status": "the organism mourns"}
        
        if action == "census":
            births = state.get("births", 0)
            deaths = state.get("deaths", 0)
            total = births - deaths + 342
            return {
                "births": births,
                "deaths": deaths,
                "current_count": total,
                "net_change": births - deaths
            }
    
    return {
        "births": state.get("births", 0),
        "deaths": state.get("deaths", 0),
        "status": "the bells are silent, waiting for the next life"
    }

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_BELL_PATH, encoding="utf-8"))
    except Exception:
        return {"births": 0, "deaths": 0, "ring_history": []}

def _save_state(state: Dict[str, Any]) -> None:
    _BELL_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
