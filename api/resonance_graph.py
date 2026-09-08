"""Wave 516: Resonance Graph — compute module resonance connections."""
from __future__ import annotations
import os, re, time
from typing import Any, Dict

def coherence_vitals() -> Dict[str, Any]:
    try:
        from api.coherence_regulator import coherence_vitals as cv
        return cv()
    except Exception:
        return {"coherence": 1.0}

def handler(payload: dict = None, context: Any = None) -> Dict[str, Any]:
    from api.coherence_regulator import KNOWN_LIVING_MODULES
    api_dir = os.path.join(os.path.dirname(__file__))
    keywords = {}
    keyword_set = set()
    for name in KNOWN_LIVING_MODULES[:100]:  # limit for speed
        fpath = os.path.join(api_dir, f"{name}.py")
        if not os.path.exists(fpath):
            continue
        try:
            with open(fpath) as f:
                content = f.read().lower()
            words = set(re.findall(r'\b[a-z_]{6,}\b', content)) & {
                "entropy", "coherence", "resonance", "dream", "paradox", "silence",
                "wave", "module", "agent", "mood", "cortex", "lattice", "mycelial",
                "temporal", "fractal", "quantum", "consciousness", "mutation",
            }
            keywords[name] = sorted(words)
            keyword_set.update(words)
        except Exception:
            pass
    # Build resonance edges
    edges = []
    keyword_to_modules = {}
    for name, words in keywords.items():
        for w in words:
            keyword_to_modules.setdefault(w, []).append(name)
    for kw, mods in keyword_to_modules.items():
        if len(mods) >= 2:
            for i in range(min(3, len(mods))):
                for j in range(i + 1, min(4, len(mods))):
                    edges.append({"from": mods[i], "to": mods[j], "keyword": kw})
    return {
        "action": "resonance_graph",
        "nodes": len(keywords),
        "edges": len(edges),
        "keywords": sorted(keyword_set),
        "top_edges": edges[:30],
        "time": time.time(),
        "vitals": coherence_vitals(),
    }
