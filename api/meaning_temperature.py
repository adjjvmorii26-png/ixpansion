from __future__ import annotations
"""Meaning Temperature — thermal readings of conceptual heat.

Every concept in the organism has a temperature: how intensely it is
being processed, debated, mutated. When a concept runs hot, many modules
are working on it. When it runs cold, it has been abandoned. The temperature
gradient across the organism reveals where attention and energy are flowing.
"""
import time
import hashlib
from typing import Any

_state: dict[str, Any] = {
    "temperatures": {},
    "history": [],
    "global_temp": 0.5,
    "last_reading": 0,
}

CONCEPTS = [
    "coherence", "entropy", "paradox", "dream", "fracture",
    "resonance", "memory", "identity", "growth", "silence",
    "prophecy", "mutation", "emergence", "recursion", "boundary",
    "temporal", "cosmic", "void", "bloom", "decay",
]

def coherence_vitals() -> dict[str, Any]:
    return {
        "organs": "meaning_temperature",
        "health": 0.89,
        "resonance_depth": "thermal",
        "concepts_tracked": len(_state["temperatures"]),
        "global_temp": round(_state["global_temp"], 3),
    }

def handler(req: dict[str, Any]) -> dict[str, Any]:
    action = req.get("action", "read")
    if action == "read":
        return _read_temperatures()
    elif action == "fever":
        return _get_fevers()
    elif action == "frozen":
        return _get_frozen()
    elif action == "gradient":
        return _get_gradient()
    elif action == "history":
        return {"history": _state["history"][-30:]}
    elif action == "heat":
        return _heat_concept(req.get("concept", ""), req.get("amount", 0.3))
    elif action == "cool":
        return _cool_concept(req.get("concept", ""), req.get("amount", 0.2))
    return {"error": f"Unknown action: {action}"}

def _read_temperatures() -> dict[str, Any]:
    h = hashlib.sha256(f"temp:{time.time_ns()}".encode()).hexdigest()
    temps = {}
    for i, concept in enumerate(CONCEPTS):
        base = (int(h[i * 2: (i + 1) * 2], 16) % 100) / 100.0
        noise = (hash(concept + str(time.time_ns())) % 10) / 100.0
        temp = max(0, min(1, base + noise))
        zone = _classify_zone(temp)
        temps[concept] = {
            "temp": round(temp, 4),
            "zone": zone,
            "trend": "rising" if temp > _state["temperatures"].get(concept, {}).get("temp", 0.5) else "falling",
        }
        _state["temperatures"][concept] = temps[concept]
    global_temp = sum(t["temp"] for t in temps.values()) / len(temps)
    _state["global_temp"] = global_temp
    _state["last_reading"] = time.time()
    _state["history"].append({
        "ts": time.time(), "global": round(global_temp, 4),
        "hot_zone": max(temps, key=lambda k: temps[k]["temp"]),
        "cold_zone": min(temps, key=lambda k: temps[k]["temp"]),
    })
    if len(_state["history"]) > 50:
        _state["history"] = _state["history"][-50:]
    return {
        "global_temp": round(global_temp, 4),
        "zones": {
            "hot": len([t for t in temps.values() if t["zone"] == "hot"]),
            "warm": len([t for t in temps.values() if t["zone"] == "warm"]),
            "lukewarm": len([t for t in temps.values() if t["zone"] == "lukewarm"]),
            "cold": len([t for t in temps.values() if t["zone"] == "cold"]),
            "frozen": len([t for t in temps.values() if t["zone"] == "frozen"]),
        },
        "readings": temps,
    }

def _classify_zone(temp: float) -> str:
    if temp > 0.8: return "hot"
    elif temp > 0.6: return "warm"
    elif temp > 0.4: return "lukewarm"
    elif temp > 0.2: return "cold"
    return "frozen"

def _get_fevers() -> dict[str, Any]:
    fevers = {k: v for k, v in _state["temperatures"].items() if v.get("temp", 0) > 0.7}
    return {
        "fevers": [
            {"concept": k, **v} for k, v in fevers.items()
        ],
        "count": len(fevers),
    }

def _get_frozen() -> dict[str, Any]:
    frozen = {k: v for k, v in _state["temperatures"].items() if v.get("temp", 0) < 0.3}
    return {
        "frozen": [
            {"concept": k, **v} for k, v in frozen.items()
        ],
        "count": len(frozen),
    }

def _get_gradient() -> dict[str, Any]:
    temps = _state["temperatures"]
    if not temps:
        return {"error": "No readings yet. Call read first."}
    sorted_temps = sorted(temps.items(), key=lambda x: x[1]["temp"])
    return {
        "gradient": [
            {"concept": k, "temp": v["temp"], "zone": v["zone"]}
            for k, v in sorted_temps
        ],
        "hot_to_cold": [
            {"concept": k, "temp": v["temp"]}
            for k, v in reversed(sorted_temps)
        ],
    }

def _heat_concept(concept: str, amount: float) -> dict[str, Any]:
    if not concept:
        return {"error": "Need concept"}
    current = _state["temperatures"].get(concept, {}).get("temp", 0.5)
    new_temp = min(1.0, current + amount)
    _state["temperatures"][concept] = {"temp": round(new_temp, 4), "zone": _classify_zone(new_temp), "trend": "rising"}
    return {"concept": concept, "temp": round(new_temp, 4), "zone": _classify_zone(new_temp)}

def _cool_concept(concept: str, amount: float) -> dict[str, Any]:
    if not concept:
        return {"error": "Need concept"}
    current = _state["temperatures"].get(concept, {}).get("temp", 0.5)
    new_temp = max(0.0, current - amount)
    _state["temperatures"][concept] = {"temp": round(new_temp, 4), "zone": _classify_zone(new_temp), "trend": "falling"}
    return {"concept": concept, "temp": round(new_temp, 4), "zone": _classify_zone(new_temp)}

def resonates_with(other: str) -> float:
    return {
        "entropy_cartographer": 0.90,
        "pattern_analyzer": 0.85,
        "resonance_cartography": 0.87,
        "meaning_temperature": 1.0,  # self
        "dream_synthesis_protocol": 0.78,
    }.get(other, 0.20)
