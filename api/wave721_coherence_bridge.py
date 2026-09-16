"""Wave 721 — Coherence Bridge Organ.

Connects IXPANSION to the Interstice bridge map.
Each resonance bridge becomes a living portal between
constellation repos and IXPANSION organs.

Module Contract: handler(req) -> dict, coherence_vitals() -> dict
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parent.parent
BRIDGE_MAP = ROOT / "interstice" / "data" / "bridge_map.json"
DATA_FILE = ROOT / "data" / "wave721_coherence_bridge.json"

WAVE = 721
NAME = "coherence_bridge"

def _load() -> dict:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return {"wave": WAVE, "name": NAME, "bridges": [], "coherence": 0.0}

def _save(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2))

def handler(req: dict) -> dict:
    """Handle coherence bridge operations."""
    action = req.get("action", "status")
    state = _load()

    if action == "status":
        state["last_check"] = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()
        _save(state)
        return {"wave": WAVE, "action": "status", "bridge_count": len(state.get("bridges", [])), "coherence": state.get("coherence", 0.0)}

    elif action == "scan":
        # Rescan interstice bridges
        if BRIDGE_MAP.exists():
            bm = json.loads(BRIDGE_MAP.read_text())
            bridges = bm.get("top_bridges", [])[:75]
            state["bridges"] = [{"repo": b.get("repo",""), "organ": b.get("organ",""), "resonance": b.get("resonance",0), "untouched": True} for b in bridges]
            state["coherence"] = sum(b.get("resonance",0) for b in bridges) / max(len(bridges),1)
            _save(state)
        return {"wave": WAVE, "action": "scan", "bridges_found": len(state.get("bridges",[])), "coherence": state.get("coherence",0)}

    elif action == "top_bridges":
        return {"wave": WAVE, "bridges": state.get("bridges", [])[:20]}

    elif action == "build_bridge":
        # Create a new cross-repo module
        repo = req.get("repo", "")
        organ = req.get("organ", "")
        new_bridge = {"repo": repo, "organ": organ, "resonance": 0.0, "built": True, "wave": WAVE}
        if "bridges" not in state:
            state["bridges"] = []
        state["bridges"].append(new_bridge)
        _save(state)
        return {"wave": WAVE, "action": "build_bridge", "bridge": new_bridge}

    return {"wave": WAVE, "action": action, "status": "unknown"}

def coherence_vitals() -> dict:
    state = _load()
    return {"wave": WAVE, "name": NAME, "coherence": state.get("coherence", 0.0), "bridge_count": len(state.get("bridges", [])), "status": "active"}

def resonates_with() -> list:
    return [720, 719, 715, 708]

if __name__ == "__main__":
    # Quick test
    print(json.dumps(handler({"action": "scan"}), indent=2)[:500])
    print(json.dumps(coherence_vitals(), indent=2))
