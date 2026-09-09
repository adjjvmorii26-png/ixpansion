"""
pattern_alchemist — Discovers hidden patterns across disparate data sources.
Transmutes raw observations into golden insights by finding non-obvious connections.
"""
import hashlib
import time
import math
from typing import Dict, List, Any

_skill_active = False
_observations = []
_insights = []

def activate_skill(params=None):
    global _skill_active
    _skill_active = True
    return {"status": "activated", "skill": "pattern_alchemist", "activated_at": time.time()}

def observe(data: Any, source: str = "unknown", tags: List[str] = None) -> Dict:
    obs = {"data": str(data)[:200], "source": source, "tags": tags or [], "timestamp": time.time()}
    _observations.append(obs)
    if len(_observations) > 200: _observations.pop(0)
    insights = _find_patterns()
    return {"observed": True, "total": len(_observations), "new_insights": len(insights)}

def _find_patterns() -> List[Dict]:
    if len(_observations) < 3: return []
    new_insights = []
    
    # Tag frequency analysis
    tag_freq = {}
    for obs in _observations[-50:]:
        for tag in obs.get("tags", []):
            tag_freq[tag] = tag_freq.get(tag, 0) + 1
    
    for tag, freq in tag_freq.items():
        if freq >= 3:
            insight = {"type": "tag_cluster", "tag": tag, "frequency": freq,
                      "description": f"Tag '{tag}' appears {freq} times — possible pattern cluster",
                      "confidence": min(freq / 10, 1.0)}
            if not any(i.get("tag") == tag for i in _insights[-10:]):
                new_insights.append(insight)
                _insights.append(insight)
    
    # Source correlation
    source_groups = {}
    for obs in _observations[-30:]:
        src = obs.get("source", "unknown")
        source_groups.setdefault(src, []).append(obs)
    
    for src, obs_list in source_groups.items():
        if len(obs_list) >= 3:
            new_insights.append({"type": "source_cluster", "source": src, "count": len(obs_list),
                                "description": f"Source '{src}' has {len(obs_list)} related observations"})
    
    return new_insights

def get_alchemist_state() -> Dict:
    return {"observations": len(_observations), "insights": len(_insights),
            "recent_insights": _insights[-5:]}

def get_skill_state():
    return {"name": "pattern_alchemist", "active": _skill_active,
            "capabilities": ["observe", "find_patterns"], "observations": len(_observations)}
