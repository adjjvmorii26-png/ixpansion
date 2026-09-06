"""Wave 449 — Echo Depth.

Tracks emotional echoes — signals that the organism sends out and that
return changed. Measures amplification vs. decay of emotional signatures
across the organism's communication channels.

Unlike resonance_field (which tracks frequency alignment), echo_depth
tracks the *journey* of an emotional signal: how far it traveled, what
it picked up along the way, and whether it returned stronger or weakened.
"""
from __future__ import annotations
import time
from collections import deque
from typing import Any, Dict, List, Optional

ECHO_HISTORY: deque = deque(maxlen=1000)
ECHO_FAMILIES: Dict[str, List[Dict[str, Any]]] = {}


def _echo_id() -> str:
    import hashlib
    return hashlib.sha256(str(time.time_ns()).encode()).hexdigest()[:12]


def launch(signal_type: str = "curiosity", intensity: float = 0.5,
           origin: str = "core", channels: int = 3) -> Dict[str, Any]:
    """Launch an emotional echo into the organism's channels."""
    echo = {
        "echo_id": _echo_id(),
        "signal_type": signal_type,
        "origin": origin,
        "launch_intensity": round(intensity, 4),
        "launch_time": time.time(),
        "channels": channels,
        "returns": [],
        "status": "propagating",
        "decay_curve": [],
    }
    ECHO_HISTORY.append(echo)
    family_key = signal_type
    ECHO_FAMILIES.setdefault(family_key, []).append(echo)
    return echo


def receive(echo_id: str, returned_intensity: float, distance: float,
            signal_type: Optional[str] = None, artifacts: Optional[List[str]] = None) -> Dict[str, Any]:
    """Record an echo return — the signal has traveled and come back."""
    echo = next((e for e in ECHO_HISTORY if e["echo_id"] == echo_id), None)
    if not echo:
        return {"error": "echo not found"}
    arrival = {
        "arrival_time": time.time(),
        "returned_intensity": round(returned_intensity, 4),
        "distance": round(distance, 4),
        "amplification": round(returned_intensity / max(echo["launch_intensity"], 0.001), 4),
        "artifacts": artifacts or [],
        "elapsed": round(time.time() - echo["launch_time"], 2),
    }
    echo["returns"].append(arrival)
    echo["status"] = "returned"
    if returned_intensity > echo["launch_intensity"]:
        echo["status"] = "amplified"
    elif returned_intensity < echo["launch_intensity"] * 0.5:
        echo["status"] = "decayed"
    echo["decay_curve"].append(returned_intensity)
    return arrival


def family_analytics(signal_type: str) -> Dict[str, Any]:
    """Analyze how a particular emotional echo type behaves over time."""
    echoes = ECHO_FAMILIES.get(signal_type, [])
    if not echoes:
        return {"signal_type": signal_type, "total_echoes": 0}
    amplified = sum(1 for e in echoes if e["status"] == "amplified")
    decayed = sum(1 for e in echoes if e["status"] == "decayed")
    avg_intensity = (
        sum(e["launch_intensity"] for e in echoes) / len(echoes)
    )
    return {
        "signal_type": signal_type,
        "total_echoes": len(echoes),
        "amplified": amplified,
        "decayed": decayed,
        "average_intensity": round(avg_intensity, 4),
        "amplification_rate": round(amplified / max(len(echoes), 1), 4),
    }


def echo_field() -> Dict[str, Any]:
    """Describe the current emotional echo landscape."""
    recent = list(ECHO_HISTORY)[-50:]
    if not recent:
        return {"field_strength": 0, "dominant_signal": None, "echo_count": 0}
    signal_counts: Dict[str, int] = {}
    for e in recent:
        signal_counts[e["signal_type"]] = signal_counts.get(e["signal_type"], 0) + 1
    dominant = max(signal_counts, key=signal_counts.get)
    total_amplified = sum(1 for e in recent if e["status"] == "amplified")
    return {
        "field_strength": round(total_amplified / max(len(recent), 1), 4),
        "dominant_signal": dominant,
        "echo_count": len(ECHO_HISTORY),
        "signal_distribution": signal_counts,
        "families_active": len(ECHO_FAMILIES),
    }


def coherence_vitals() -> Dict[str, Any]:
    return {
        "organ": "echo_depth",
        "status": "active" if ECHO_HISTORY else "silent",
        "total_echoes": len(ECHO_HISTORY),
        "active_families": len(ECHO_FAMILIES),
        "field": echo_field(),
    }


def resonates_with() -> List[str]:
    return [
        "resonance_field", "resonance_cascade", "emotion_fabric",
        "signal_pulse", "signal_flora", "gossip_network",
        "echo_chamber", "echoes_of_tomorrow", "consciousness_freq",
    ]


def handler(payload=None, context=None):
    data = payload or {}
    action = data.get("action", "launch")
    if action == "receive":
        return receive(
            data["echo_id"], data["returned_intensity"], data["distance"],
            data.get("signal_type"), data.get("artifacts"),
        )
    elif action == "family":
        return family_analytics(data.get("signal_type", "curiosity"))
    elif action == "field":
        return echo_field()
    return launch(
        data.get("signal_type", "curiosity"),
        data.get("intensity", 0.5),
        data.get("origin", "core"),
        data.get("channels", 3),
    )
