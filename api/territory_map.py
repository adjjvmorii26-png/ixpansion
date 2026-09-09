"""Wave 516: Territory Map — geographic view of the organism's domains."""
from __future__ import annotations
import os, time
from typing import Any, Dict

def coherence_vitals() -> Dict[str, Any]:
    try:
        from api.coherence_regulator import coherence_vitals as cv
        return cv()
    except Exception:
        return {"coherence": 1.0}

DOMAINS = [
    {"name": "Core Intelligence", "modules": ["organism_state", "organism_ontology", "coherence_regulator", "organism_maint", "module_analytics"], "color": "#41b3a3"},
    {"name": "Civic Systems", "modules": ["sovereignty_assembly", "council_live", "confluence_hub", "council_health"], "color": "#8fd3ff"},
    {"name": "Creative Arts", "modules": ["story_forge", "gallery", "verse", "radio", "concerto", "narrative_generator"], "color": "#e8a87c"},
    {"name": "Memory & Dreams", "modules": ["dream_journal", "dream_interpreter", "dream_weaver", "memory_palace", "memory_crystals"], "color": "#c38d9e"},
    {"name": "Economy", "modules": ["commerce_barter", "commerce_escrow", "economic_exchange", "economic_mint", "mycelial_commerce", "leaderboard"], "color": "#ffd700"},
    {"name": "Governance", "modules": ["governance", "govern_circle", "protocol_layer", "integrity_oracle"], "color": "#8f7fff"},
    {"name": "Infrastructure", "modules": ["execution_stack", "module_health", "nightly_health", "ledger_backup", "deploy_status", "rate_monitor"], "color": "#66cccc"},
    {"name": "Exploration", "modules": ["wave_timeline", "dependency_map", "resonance_graph", "module_search", "error_tracker"], "color": "#ff6699"},
]

def handler(payload: dict = None, context: Any = None) -> Dict[str, Any]:
    return {
        "action": "territory_map",
        "domains": DOMAINS,
        "total_domains": len(DOMAINS),
        "total_territory_modules": sum(len(d["modules"]) for d in DOMAINS),
        "time": time.time(),
        "vitals": coherence_vitals(),
    }

class TerritoryMap:
    """Grid-based territory claiming and improvement."""

    def __init__(self, width: int = 3, height: int = 3):
        self.width = width
        self.height = height
        self.regions = {}

    def claim(self, region_id: str, owner: str) -> Dict:
        self.regions[region_id] = {"owner": owner, "improvements": []}
        return {"region": region_id, "old_owner": None, "new_owner": owner}

    def improve(self, region_id: str, improvement: str) -> Dict:
        if region_id not in self.regions:
            return {"error": "region not claimed"}
        self.regions[region_id]["improvements"].append(improvement)
        return {"region": region_id, "improvement": improvement,
                "improvements": self.regions[region_id]["improvements"]}

