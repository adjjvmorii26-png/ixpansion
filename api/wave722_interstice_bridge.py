"""Wave 722 — Interstice Bridge Engine.

Turns the 75 untouched interstice bridges into live, navigable
project blueprints. Each bridge becomes a portal module.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict
import datetime

ROOT = Path(__file__).resolve().parent.parent
BRIDGE_MAP = ROOT / "interstice" / "data" / "bridge_map.json"
DATA_FILE = ROOT / "data" / "wave722_interstice_bridge.json"
WAVE = 722
NAME = "interstice_bridge"

def _load() -> dict:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return {"wave": WAVE, "name": NAME, "bridges": [], "build_queue": []}

def _save(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2))

def handler(req: dict) -> dict:
    action = req.get("action", "status")
    state = _load()

    if action == "status":
        state["last_check"] = datetime.datetime.now(datetime.UTC).isoformat()
        _save(state)
        return {"wave": WAVE, "action": "status", "bridge_count": len(state.get("bridges", [])), "coherence": state.get("coherence", 0.0)}

    elif action == "scan":
        if BRIDGE_MAP.exists():
            bm = json.loads(BRIDGE_MAP.read_text())
            top = bm.get("top_bridges", [])[:75]
            state["bridges"] = top
            state["coherence"] = sum(b.get("resonance", 0) for b in top) / max(len(top), 1)
            state["repo_count"] = len(set(b.get("repo", "") for b in top))
            _save(state)
        return {"wave": WAVE, "action": "scan", "bridges_found": len(state.get("bridges", [])), "coherence": state.get("coherence", 0)}

    elif action == "proposals":
        """Generate build proposals from untouched bridges."""
        bridges = state.get("bridges", [])
        proposals = []
        for b in bridges[:20]:
            repo = b.get("repo", "")
            organ = b.get("organ", "")
            proposals.append({
                "repo": repo,
                "organ": organ,
                "resonance": b.get("resonance", 0),
                "proposal": f"Build {repo} ↔ {organ} integration module",
                "priority": "high" if b.get("resonance", 0) > 0.25 else "medium"
            })
        return {"wave": WAVE, "proposals": proposals}

    elif action == "build":
        repo = req.get("repo", "")
        organ = req.get("organ", "")
        bridge = {"repo": repo, "organ": organ, "status": "building", "wave": WAVE, "started": datetime.datetime.now(datetime.UTC).isoformat()}
        if "build_queue" not in state:
            state["build_queue"] = []
        state["build_queue"].append(bridge)
        _save(state)
        return {"wave": WAVE, "action": "build", "bridge": bridge}

    elif action == "top_bridges":
        return {"wave": WAVE, "top_bridges": state.get("bridges", [])[:20]}

    return {"wave": WAVE, "action": action, "status": "ok"}

def coherence_vitals() -> dict:
    state = _load()
    return {"wave": WAVE, "name": NAME, "coherence": state.get("coherence", 0.0), "bridge_count": len(state.get("bridges", [])), "status": "active"}

def resonates_with() -> list:
    return [720, 721, 715, 708]

if __name__ == "__main__":
    print(json.dumps(handler({"action": "scan"}), indent=2)[:600])
    print(json.dumps(coherence_vitals(), indent=2))
