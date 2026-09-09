"""
entropy_cartographer — Maps the entropy landscape across the organism.
Identifies high-entropy zones (creative chaos) and low-entropy zones (crystalline order).
"""
import json
import time
import math
import hashlib
from typing import Dict, List, Optional

_skill_active = False
_entropy_map = {}
_zone_history = []

def activate_skill(params=None):
    global _skill_active
    _skill_active = True
    return {"status": "activated", "skill": "entropy_cartographer", "activated_at": time.time()}

def map_entropy(modules: Dict, connections: List[tuple] = None) -> Dict:
    global _entropy_map
    
    zones = {}
    for key, mod in modules.items():
        r = mod.get("resonance", 0.5) if isinstance(mod, dict) else 0.5
        caps = mod.get("capabilities", []) if isinstance(mod, dict) else []
        
        # Entropy is inversely related to resonance stability
        entropy = 1.0 - abs(r - 0.5) * 2
        entropy = max(0.0, min(1.0, entropy))
        
        zone = "chaos" if entropy > 0.7 else "ordered" if entropy < 0.3 else "liminal"
        
        zones[key] = {
            "entropy": round(entropy, 4),
            "zone": zone,
            "resonance": r,
            "capability_count": len(caps),
            "glyph": _zone_glyph(zone, entropy)
        }
    
    _entropy_map = zones
    
    # Summary statistics
    entropies = [z["entropy"] for z in zones.values()]
    zone_counts = {}
    for z in zones.values():
        zone_counts[z["zone"]] = zone_counts.get(z["zone"], 0) + 1
    
    summary = {
        "total_modules": len(zones),
        "mean_entropy": round(sum(entropies) / len(entropies), 4) if entropies else 0,
        "zone_distribution": zone_counts,
        "hottest_zone": max(zones.keys(), key=lambda k: zones[k]["entropy"]) if zones else None,
        "coldest_zone": min(zones.keys(), key=lambda k: zones[k]["entropy"]) if zones else None,
        "zones": zones,
        "timestamp": time.time()
    }
    
    _zone_history.append({"mean_entropy": summary["mean_entropy"], "zones": zone_counts, "timestamp": time.time()})
    if len(_zone_history) > 50:
        _zone_history.pop(0)
    
    return summary

def _zone_glyph(zone: str, entropy: float) -> str:
    if zone == "chaos":
        return "✸" if entropy > 0.9 else "∆"
    elif zone == "ordered":
        return "◇" if entropy < 0.1 else "□"
    else:
        return "◈"

def get_entropy_trend() -> Dict:
    if len(_zone_history) < 2:
        return {"trend": "insufficient_data"}
    
    recent = _zone_history[-10:]
    values = [h["mean_entropy"] for h in recent]
    trend = values[-1] - values[0]
    
    return {
        "current_mean": values[-1],
        "trend": round(trend, 4),
        "direction": "expanding" if trend > 0.01 else "crystallizing" if trend < -0.01 else "stable",
        "readings": len(_zone_history)
    }

def get_skill_state():
    return {
        "name": "entropy_cartographer",
        "active": _skill_active,
        "capabilities": ["map_entropy", "get_entropy_trend"],
        "zones_mapped": len(_entropy_map),
        "history_length": len(_zone_history)
    }
