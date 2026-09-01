"""Social Cortex — network awareness; the organism perceives other systems.

Beyond its own boundaries, the organism exists in a network of services,
APIs, and other digital entities. The Social Cortex maps these relationships,
tracks interaction patterns, and gauges the health of its social connections.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

_known_entities: Dict[str, Dict[str, Any]] = {}
_interactions: List[Dict[str, Any]] = []

def register_entity(name: str, url: str = "", nature: str = "unknown",
                    relationship: str = "acquaintance") -> Dict[str, Any]:
    """Register an external entity the organism knows about."""
    _known_entities[name] = {
        "name": name,
        "url": url,
        "nature": nature,
        "relationship": relationship,
        "registered": time.time(),
        "interaction_count": 0,
        "trust": 0.5,
    }
    return _known_entities[name]

def record_interaction(entity_name: str, direction: str = "outbound",
                       success: bool = True) -> Dict[str, Any]:
    """Record an interaction with an entity."""
    interaction = {
        "entity": entity_name,
        "direction": direction,
        "success": success,
        "timestamp": time.time(),
    }
    _interactions.append(interaction)
    if entity_name in _known_entities:
        _known_entities[entity_name]["interaction_count"] += 1
        # Adjust trust
        if success:
            _known_entities[entity_name]["trust"] = min(1.0, _known_entities[entity_name]["trust"] + 0.05)
        else:
            _known_entities[entity_name]["trust"] = max(0.0, _known_entities[entity_name]["trust"] - 0.1)
    return interaction

def social_map() -> Dict[str, Any]:
    """Return the full social topology."""
    if not _known_entities:
        return {"entities": 0, "interactions": 0, "avg_trust": 0}
    avg_trust = sum(e["trust"] for e in _known_entities.values()) / len(_known_entities)
    relationships = {}
    for e in _known_entities.values():
        r = e["relationship"]
        relationships[r] = relationships.get(r, 0) + 1
    return {
        "entities": len(_known_entities),
        "interactions": len(_interactions),
        "avg_trust": round(avg_trust, 3),
        "relationship_types": relationships,
        "most_trusted": max(_known_entities.items(), key=lambda x: x[1]["trust"])[0] if _known_entities else None,
    }

def coherence_vitals() -> Dict[str, Any]:
    sm = social_map()
    return {
        "layer": "External Awareness",
        "status": "resonant" if sm["entities"] > 0 else "dormant",
        "entities": sm["entities"],
        "avg_trust": sm["avg_trust"],
        "resonance": min(1.0, sm["avg_trust"]),
    }

def resonates_with() -> List[str]:
    return ["celestial_compass", "weather_synapse", "workforce_nexus", "gossip_network"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "map")
    if action == "register":
        return register_entity(payload.get("name", ""), payload.get("url", ""), payload.get("nature", "unknown"), payload.get("relationship", "acquaintance"))
    elif action == "interact":
        return record_interaction(payload.get("entity", ""), payload.get("direction", "outbound"), payload.get("success", True))
    return {"action": action, "map": social_map()}
