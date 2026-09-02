from __future__ import annotations
"""Metaphor forge — converts raw system state into symbolic structures that can be executed as code."""
import json
import time
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

_METAPHOR_PATH = Path(__file__).resolve().parent.parent / "data" / "metaphor_registry.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Forge metaphors from system state."""
    registry = _load_registry()
    if payload and "state_snapshot" in payload:
        metaphors = _generate_metaphors(payload["state_snapshot"])
        registry["last_forged"] = time.time()
        registry["metaphor_count"] = len(registry.get("metaphors", []))
        registry.setdefault("metaphors", []).extend(metaphors)
        _save_registry(registry)
    return {"metaphors_generated": len(registry.get("metaphors", [])), "latest": registry.get("metaphors", [])[-1] if registry.get("metaphors") else None}

def _generate_metaphors(state_snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
    metaphors = []
    # Convert numerical thresholds to symbolic language
    if "modules_active" in state_snapshot:
        count = state_snapshot["modules_active"]
        metaphors.append({
            "type": "population_metaphor",
            "symbol": f"collective_{count}_if",
            "description": f"{count} agents weaving as one",
            "generated": time.time()
        })
    if "entropy" in state_snapshot:
        ent = state_snapshot["entropy"]
        metaphors.append({
            "type": "entropy_metaphor",
            "symbol": f"__{ent:.2f}_decay",
            "description": "controlled drift toward organized complexity",
            "generated": time.time()
        })
    if "waves_completed" in state_snapshot:
        waves = state_snapshot["waves_completed"]
        metaphors.append({
            "type": "evolution_metaphor",
            "symbol": f"spiral_wave_{waves}",
            "description": "the organism spirals upward through waves",
            "generated": time.time()
        })
    return metaphors

def _load_registry() -> Dict[str, Any]:
    try:
        return json.load(open(_METAPHOR_PATH, encoding="utf-8"))
    except Exception:
        return {"metaphors": [], "last_forged": None, "metaphor_count": 0}

def _save_registry(registry: Dict[str, Any]) -> None:
    _METAPHOR_PATH.write_text(json.dumps(registry, indent=2, ensure_ascii=False))
