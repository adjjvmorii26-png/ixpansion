"""Chaos Amplifier — scales controlled instability for creative generation.

Sometimes order is the enemy of discovery. The Chaos Amplifier takes
small instabilities and amplifies them into productive turbulence —
turning noise into signal, glitches into innovations.
"""
from __future__ import annotations

import random
import time
from typing import Any, Dict, List, Optional

_amplifications: List[Dict[str, Any]] = []
_amp_counter = 0

def amplify(source: str = "entropy", gain: float = 1.0,
            targets: Optional[List[str]] = None) -> Dict[str, Any]:
    """Amplify instability to generate creative turbulence."""
    global _amp_counter
    _amp_counter += 1
    amplified = {
        "id": f"chaos_{_amp_counter:04d}",
        "source": source,
        "gain": round(gain, 3),
        "targets": targets or [],
        "amplified_at": time.time(),
        "output_signal": round(min(2.0, gain * (0.3 + random.random() * 0.7)), 3),
        "innovations_suggested": random.randint(0, 5),
        "stability_cost": round(min(1.0, gain * 0.25), 3),
    }
    _amplifications.append(amplified)
    return amplified

def chaos_report() -> Dict[str, Any]:
    """Current chaos amplification state."""
    total_signal = sum(a["output_signal"] for a in _amplifications)
    total_innovations = sum(a["innovations_suggested"] for a in _amplifications)
    return {
        "total_runs": len(_amplifications),
        "total_signal": round(total_signal, 3),
        "innovations": total_innovations,
        "avg_gain": round(sum(a["gain"] for a in _amplifications) / max(len(_amplifications), 1), 3),
    }

def coherence_vitals() -> Dict[str, Any]:
    r = chaos_report()
    return {"layer": "Chaos Engineering", "status": "resonant", "runs": r["total_runs"],
            "innovations": r["innovations"], "resonance": min(1.0, r["innovations"] / 10)}

def resonates_with() -> List[str]:
    return ["paradox_injector", "entropy_spike", "destabilizer", "thought_meteorology"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "report")
    if action == "amplify":
        return amplify(payload.get("source", "entropy"), payload.get("gain", 1.0), payload.get("targets"))
    elif action == "report":
        return {"report": chaos_report()}
    return {"action": action, "status": "amplifying"}
