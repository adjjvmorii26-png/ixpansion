"""Wave 727 — Metaphor Forge.

Converts raw system state into symbolic structures
that can be executed as code.
"""
import json
import hashlib
from pathlib import Path
from typing import Any, Dict
import datetime

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "wave727_metaphor_forge.json"
WAVE = 727
NAME = "metaphor_forge"

def _load() -> dict:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return {"wave": WAVE, "name": NAME, "forged": [], "symbols": []}

def _save(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2))

def handler(req: dict) -> dict:
    action = req.get("action", "status")
    state = _load()

    if action == "forge":
        raw_state = req.get("raw_state", "")
        symbol = {
            "id": hashlib.md5(raw_state.encode()).hexdigest()[:12],
            "raw": raw_state,
            "symbolic_form": f"metaphor::{hashlib.sha256(raw_state.encode()).hexdigest()[:16]}",
            "executable": f"EXEC_{hashlib.sha256(raw_state.encode()).hexdigest()[:8]}",
            "wave": WAVE,
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            "status": "forged"
        }
        state["forged"].append(symbol)
        state["symbols"].append(symbol["symbolic_form"])
        _save(state)
        return {"wave": WAVE, "action": "forge", "symbol": symbol}

    elif action == "execute":
        symbol_id = req.get("symbol_id", "")
        for s in state["forged"]:
            if s["id"] == symbol_id:
                s["status"] = "executed"
                s["executed_at"] = datetime.datetime.now(datetime.UTC).isoformat()
                _save(state)
                return {"wave": WAVE, "action": "execute", "symbol": s}
        return {"wave": WAVE, "action": "execute", "error": "symbol not found"}

    elif action == "symbols":
        return {"wave": WAVE, "symbols": state["symbols"][-20:], "forged_count": len(state["forged"])}

    elif action == "status":
        state["last_check"] = datetime.datetime.now(datetime.UTC).isoformat()
        _save(state)
        return {"wave": WAVE, "forged": len(state["forged"]), "status": "active"}

    return {"wave": WAVE, "action": action, "status": "ok"}

def coherence_vitals() -> dict:
    state = _load()
    return {"wave": WAVE, "name": NAME, "forged": len(state["forged"]), "status": "active"}

def resonates_with() -> list:
    return [720, 723, 725, 726]

if __name__ == "__main__":
    r = handler({"action": "forge", "raw_state": "coherence=0.85, entropy=0.15, divergence=0.3"})
    print("Forge:", json.dumps(r["symbol"], indent=2)[:300])
    r2 = handler({"action": "execute", "symbol_id": r["symbol"]["id"]})
    print("Execute:", json.dumps(r2["symbol"], indent=2)[:200])
    print("Vitals:", json.dumps(coherence_vitals(), indent=2))
