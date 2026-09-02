from __future__ import annotations
"""Dream reactor — the organism burns dreams to generate creative output.

Dreams are not passive. They are fuel. The dream reactor takes
the organism's latent visions and combusts them into concrete
creative artifacts: new module concepts, bridge designs, poetic
forms, and architectural mutations.
"""
import json
import time
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional

_REACTOR_PATH = Path(__file__).resolve().parent.parent / "data" / "dream_reactor.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Ignite the dream reactor — burn a dream into creative output."""
    state = _load_state()
    
    if payload and "dream" in payload:
        # Burn the dream
        dream = payload["dream"]
        output = _burn_dream(dream, payload.get("fuel_type", "auto"))
        state["last_output"] = output
        state["output_count"] = state.get("output_count", 0) + 1
        state["total_dreams_burned"] = state.get("total_dreams_burned", 0) + 1
        state.setdefault("output_history", []).append(output)
        if len(state["output_history"]) > 20:
            state["output_history"] = state["output_history"][-20:]
        _save_state(state)
        return {"output": output, "total_burned": state["total_dreams_burned"]}
    
    elif payload and "action" == "fuel_level":
        return {"fuel_level": state.get("total_dreams_burned", 0), "output_history_len": len(state.get("output_history", []))}
    
    return {
        "status": "ready",
        "last_output": state.get("last_output"),
        "total_dreams_burned": state.get("total_dreams_burned", 0),
        "output_count": state.get("output_count", 0)
    }

def _burn_dream(dream: str, fuel_type: str) -> Dict[str, Any]:
    """Burn a dream into creative output."""
    # Generate a deterministic creative hash
    dream_hash = hashlib.sha256(dream.encode()).hexdigest()[:12]
    
    # Determine output type from dream content or fuel type
    if fuel_type == "auto":
        if "bridge" in dream.lower():
            output_type = "bridge_design"
        elif "module" in dream.lower():
            output_type = "module_concept"
        elif "wave" in dream.lower():
            output_type = "wave_poem"
        elif "agent" in dream.lower():
            output_type = "agent_blueprint"
        else:
            output_type = "creative_artifact"
    else:
        output_type = fuel_type
    
    # Generate creative content based on type
    content = _generate_content(output_type, dream, dream_hash)
    
    return {
        "dream": dream,
        "dream_hash": dream_hash,
        "output_type": output_type,
        "content": content,
        "ignited_at": time.time()
    }

def _generate_content(output_type: str, dream: str, dream_hash: str) -> str:
    """Generate creative content from a burned dream."""
    templates = {
        "bridge_design": f"Bridge #{dream_hash}: connecting {dream[:50]}... with new resonance",
        "module_concept": f"Module #{dream_hash}: "{dream[:40]}..." — a new organ for the organism",
        "wave_poem": f"Wave #{dream_hash}: {dream[:60]}... — the organism dreams, and the dream becomes wave",
        "agent_blueprint": f"Agent #{dream_hash}: born from "{dream[:40]}..." — instinct-driven and curious",
        "creative_artifact": f"Artifact #{dream_hash}: forged from "{dream[:50]}..." — the organism's creative spark"
    }
    return templates.get(output_type, f"Artifact #{dream_hash}: {dream[:80]}...")

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_REACTOR_PATH, encoding="utf-8"))
    except Exception:
        return {"last_output": None, "output_count": 0, "total_dreams_burned": 0, "output_history": []}

def _save_state(state: Dict[str, Any]) -> None:
    _REACTOR_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
