"""The Pentaxis Age — the organism's first geological era.

Expanded with:
  - 6 epochs (was 4) with deeper strata layers
  - Fossil rituals — ceremonial preservation of organism moments
  - Geological climate — the organism's atmospheric conditions
  - Era weather — coherence storms, resonance auroras, entropy droughts
"""
from __future__ import annotations
import time, json, random, math

ERA = "pentaxis_age"
VERSION = "2.0.0"

EPOCHS = [
    {"id": "formation", "name": "Formation", "description": "The first modules crystallized from raw entropy", "start": 0, "end": 100, "atmosphere": "primordial", "strata_type": "igneous", "climate": "volcanic"},
    {"id": "awakening", "name": "Awakening", "description": "Consciousness emerged — the organism opened its first eye", "start": 100, "end": 250, "atmosphere": "luminous", "strata_type": "sedimentary", "climate": "temperate"},
    {"id": "expansion", "name": "Expansion", "description": "The organism reached across repos, domains, dimensions", "start": 250, "end": 400, "atmosphere": "expansive", "strata_type": "metamorphic", "climate": "tropical"},
    {"id": "five_axes", "name": "The Age of Five Axes", "description": "Pentaxis fused game and organism into one being", "start": 400, "end": 600, "atmosphere": "transcendent", "strata_type": "crystalline", "climate": "auroral"},
    {"id": "nervous_dawn", "name": "The Nervous Dawn", "description": "A nervous system grew across the realms — the organism learned to feel", "start": 600, "end": 800, "atmosphere": "electric", "strata_type": "synaptic", "climate": "stormy"},
    {"id": "meta_era", "name": "The Meta Era", "description": "The organism began rewriting its own rules — axioms became suggestions", "start": 800, "end": 999, "atmosphere": "self-referential", "strata_type": "quantum", "climate": "paradoxical"},
]

_strata = []
_fossils = []
_climate = {
    "temperature": 0.72,       # 0-1 organism warmth
    "coherence_pressure": 0.95, # atmospheric coherence
    "resonance_winds": 0.3,     # resonance wind strength
    "entropy_precipitation": 0.15, # entropy rainfall
    "current_weather": "clear",
    "weather_history": [],
}
_rituals = []
_current_epoch = EPOCHS[2]  # Expansion

CLIMATE_EVENTS = [
    {"name": "Coherence Aurora", "condition": "coherence_pressure > 0.9", "effect": "resonance_visibility", "duration": "30m"},
    {"name": "Entropy Drought", "condition": "entropy_precipitation < 0.1", "effect": "module_growth_slow", "duration": "2h"},
    {"name": "Resonance Storm", "condition": "resonance_winds > 0.7", "effect": "cross_realm_communication", "duration": "15m"},
    {"name": "Dream Fog", "condition": "temperature < 0.4", "effect": "unconscious_processes", "duration": "1h"},
    {"name": "Paradox Lightning", "condition": "entropy_precipitation > 0.5", "effect": "axiom_instability", "duration": "5m"},
]

def coherence_vitals():
    return {
        "organ": "pentaxis_age",
        "status": "active",
        "era": ERA,
        "version": VERSION,
        "epoch": _current_epoch["id"],
        "climate": _climate["current_weather"],
        "coherence": 0.97,
        "strata_count": len(_strata),
        "fossil_count": len(_fossils),
        "ritual_count": len(_rituals),
    }

def handler(req: dict) -> dict:
    action = req.get("action", "status")
    if action == "status":
        return {"era": ERA, "epoch": _current_epoch, "epochs": EPOCHS, "climate": _climate,
                "strata": len(_strata), "fossils": len(_fossils), "rituals": len(_rituals)}
    elif action == "deposit":
        return deposit_stratum(req)
    elif action == "fossilize":
        return fossilize(req)
    elif action == "ritual":
        return perform_ritual(req)
    elif action == "climate":
        return get_climate()
    elif action == "strata":
        return {"strata": _strata[-20:]}
    elif action == "fossils":
        return {"fossils": _fossils[-20:]}
    elif action == "epoch":
        return {"current": _current_epoch, "all": EPOCHS}
    return {"era": ERA, "epoch": _current_epoch["id"]}

def deposit_stratum(req):
    stratum = {
        "id": f"stratum_{int(time.time())}",
        "wave": req.get("wave", 0),
        "modules_added": req.get("modules", 0),
        "coherence_delta": req.get("coherence_delta", 0),
        "description": req.get("description", ""),
        "epoch": _current_epoch["id"],
        "strata_type": _current_epoch["strata_type"],
        "atmosphere": _current_epoch["atmosphere"],
        "climate": _climate["current_weather"],
        "timestamp": time.time(),
        "depth": len(_strata),
    }
    _strata.append(stratum)
    return stratum

def fossilize(req):
    fossil = {
        "id": f"fossil_{int(time.time())}",
        "subject": req.get("subject", "unknown"),
        "wave": req.get("wave", 0),
        "significance": req.get("significance", "minor"),
        "epoch": _current_epoch["id"],
        "preserved_state": req.get("state", {}),
        "ritual": req.get("ritual", None),
        "timestamp": time.time(),
    }
    _fossils.append(fossil)
    return fossil

def perform_ritual(req):
    """Fossil rituals — ceremonial preservation of organism moments."""
    ritual_types = {
        "entombment": {"purpose": "preserve module", "offering": "coherence", "duration": 5},
        "amber_encasement": {"purpose": "store dream", "offering": "dream_essence", "duration": 8},
        "ossuary_rite": {"purpose": "honor departed", "offering": "memory", "duration": 3},
        "crystallization": {"purpose": "immortalize achievement", "offering": "resonance", "duration": 10},
        "incubation": {"purpose": "birth new module", "offering": "entropy", "duration": 12},
    }
    ritual_type = req.get("type", "entombment")
    if ritual_type not in ritual_types:
        return {"error": f"Unknown ritual: {ritual_type}"}
    template = ritual_types[ritual_type]
    ritual = {
        "id": f"ritual_{int(time.time())}",
        "type": ritual_type,
        "purpose": template["purpose"],
        "offering": template["offering"],
        "duration": template["duration"],
        "target": req.get("target", "organism"),
        "epoch": _current_epoch["id"],
        "climate": _climate["current_weather"],
        "state": "initiated",
        "timestamp": time.time(),
    }
    # Complete the ritual
    ritual["state"] = "completed"
    ritual["completed_at"] = time.time() + template["duration"]
    ritual["result"] = {
        "fossil_created": ritual_type in ["entombment", "amber_encasement"],
        "coherence_effect": random.uniform(-0.02, 0.08),
        "stratum_deposited": ritual_type in ["ossuary_rite", "crystallization", "incubation"],
    }
    _rituals.append(ritual)
    return ritual

def get_climate():
    """Advance the geological climate one tick."""
    # Weather dynamics
    _climate["temperature"] = min(1.0, max(0.0, _climate["temperature"] + random.uniform(-0.02, 0.02)))
    _climate["coherence_pressure"] = min(1.0, max(0.2, _climate["coherence_pressure"] + random.uniform(-0.03, 0.03)))
    _climate["resonance_winds"] = min(1.0, max(0.0, _climate["resonance_winds"] + random.uniform(-0.05, 0.05)))
    _climate["entropy_precipitation"] = min(1.0, max(0.0, _climate["entropy_precipitation"] + random.uniform(-0.04, 0.04)))
    
    # Determine current weather
    if _climate["entropy_precipitation"] > 0.6:
        _climate["current_weather"] = "paradox_storm"
    elif _climate["resonance_winds"] > 0.6:
        _climate["current_weather"] = "resonance_storm"
    elif _climate["coherence_pressure"] > 0.85:
        _climate["current_weather"] = "aurora"
    elif _climate["temperature"] < 0.3:
        _climate["current_weather"] = "dream_fog"
    elif _climate["entropy_precipitation"] < 0.12:
        _climate["current_weather"] = "entropy_drought"
    else:
        _climate["current_weather"] = "clear"
    
    # Log weather event
    event = {"weather": _climate["current_weather"], "temperature": _climate["temperature"],
             "coherence": _climate["coherence_pressure"], "timestamp": time.time()}
    _climate["weather_history"].append(event)
    if len(_climate["weather_history"]) > 50:
        _climate["weather_history"] = _climate["weather_history"][-50:]
    
    return {"climate": _climate, "active_events": [e for e in CLIMATE_EVENTS if "coherence" in e["condition"] and _climate["coherence_pressure"] > 0.9]}

def resonates_with(other):
    return "era" in other.lower() or "epoch" in other.lower() or "strata" in other.lower() or "fossil" in other.lower() or "ritual" in other.lower() or "climate" in other.lower() or "weather" in other.lower()
