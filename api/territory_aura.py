"""Wave 517: Territory Aura — visualize aura around each territory."""
from __future__ import annotations
import hashlib, random, time
from typing import Any, Dict

def coherence_vitals():
    try:
        from api.coherence_regulator import coherence_vitals as cv
        return cv()
    except Exception:
        return {"coherence": 1.0}

TERRITORIES = ["Core", "Civic", "Creative", "Memory", "Economy", "Governance", "Infrastructure", "Exploration"]

def handler(payload=None, context=None):
    rng = random.Random(time.time())
    auras = []
    for t in TERRITORIES:
        h = hashlib.sha256(t.encode()).hexdigest()
        auras.append({
            "territory": t,
            "aura_color": f"#{h[:6]}",
            "aura_intensity": round(0.3 + rng.random() * 0.7, 2),
            "aura_radius": round(20 + rng.random() * 80, 1),
            "aura_type": rng.choice(["radiant", "pulsing", "steady", "flickering"]),
        })
    return {"action": "territory_aura", "auras": auras, "time": time.time(), "vitals": coherence_vitals()}
