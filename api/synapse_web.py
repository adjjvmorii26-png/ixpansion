"""Wave 516: Synapse Web — the nervous system connecting modules."""
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
    signal_words = ["entropy", "coherence", "resonance", "dream", "paradox", "silence", "wave", "module", "mood", "memory"]
    synapses = []
    for name in KNOWN_LIVING_MODULES[:80]:
        fpath = os.path.join(api_dir, f"{name}.py")
        if not os.path.exists(fpath):
            continue
        try:
            with open(fpath) as f:
                content = f.read().lower()
            found = [w for w in signal_words if w in content]
            if found:
                synapses.append({"neuron": name, "signals": found, "strength": len(found)})
        except Exception:
            pass
    synapses.sort(key=lambda s: s["strength"], reverse=True)
    strongest = synapses[:15]
    return {
        "action": "synapse_web",
        "neurons": len(synapses),
        "strongest_synapses": strongest,
        "total_signal_connections": sum(s["strength"] for s in synapses),
        "time": time.time(),
        "vitals": coherence_vitals(),
    }
