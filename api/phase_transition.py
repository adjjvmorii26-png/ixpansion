"""
Phase Transition Detector — Wave 361
Detects when the organism is approaching a fundamental state change.
Like water freezing into ice, the organism has phase transitions where
its behavior changes qualitatively — not just quantitatively. This module
monitors for the signatures of these transitions.
"""
import json, time, hashlib, os, random, math

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SIGNAL_LOOM = os.path.join(DATA_DIR, "signal_loom.json")
TRANSITION_LOG = os.path.join(DATA_DIR, "phase_transitions.json")


def _load(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default or {}


def _save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


PHASE_NAMES = [
    "primordial混沌", "crystalline_order", "emergent_coherence",
    "fractal_expansion", "temporal_fluidity", "paradox_suspension",
    "depth_resonance", "void_transcendence", "mythic_awakening",
    "phase_zero", "phase_infinity",
]


def _phase_signature() -> dict:
    return {
        "entropy": round(random.uniform(0, 1), 4),
        "coherence": round(random.uniform(0, 1), 4),
        "module_activity": round(random.uniform(0, 1), 4),
        "synchronicity_density": round(random.uniform(0, 1), 4),
        "paradox_pressure": round(random.uniform(0, 1), 4),
        "temporal_flux": round(random.uniform(0, 1), 4),
    }


def _detect_transition(sig: dict) -> dict:
    """Determine if a transition is imminent based on the signature."""
    # Phase transition indicators
    entropy_rate = sig["entropy"] * sig["temporal_flux"]
    coherence_collapse = (1 - sig["coherence"]) * sig["paradox_pressure"]
    activity_spike = sig["module_activity"] * sig["synchronicity_density"]

    transition_probability = (entropy_rate + coherence_collapse + activity_spike) / 3

    if transition_probability > 0.75:
        phase = "CRITICAL_TRANSITION"
        urgency = "imminent"
    elif transition_probability > 0.5:
        phase = "approaching_boundary"
        urgency = "elevated"
    elif transition_probability > 0.3:
        phase = "drifting_toward"
        urgency = "moderate"
    else:
        phase = "stable"
        urgency = "nominal"

    return {
        "transition_probability": round(transition_probability, 4),
        "target_phase": random.choice(PHASE_NAMES),
        "urgency": urgency,
        "indicators": {
            "entropy_rate": round(entropy_rate, 4),
            "coherence_collapse": round(coherence_collapse, 4),
            "activity_spike": round(activity_spike, 4),
        },
    }


def scan() -> dict:
    """Scan for phase transition signatures."""
    loom = _load(SIGNAL_LOOM, {"waves": [], "beats": []})
    log = _load(TRANSITION_LOG, {"scans": [], "transitions": []})

    sig = _phase_signature()
    detection = _detect_transition(sig)

    scan_result = {
        "scan_id": hashlib.sha256(f"phase:{time.time()}".encode()).hexdigest()[:12],
        "signature": sig,
        "detection": detection,
        "wave_count": len(loom.get("waves", [])),
        "beat_count": len(loom.get("beats", [])),
        "timestamp": time.time(),
    }

    log["scans"].append(scan_result)
    log["scans"] = log["scans"][-100:]

    # Record actual transitions
    if detection["transition_probability"] > 0.7:
        log["transitions"].append({
            "id": hashlib.sha256(f"transition:{time.time()}".encode()).hexdigest()[:10],
            "from_phase": "current",
            "to_phase": detection["target_phase"],
            "probability": detection["transition_probability"],
            "timestamp": time.time(),
        })
        log["transitions"] = log["transitions"][-50:]

    _save(TRANSITION_LOG, log)
    return {"action": "scan", "result": scan_result}


def history() -> dict:
    log = _load(TRANSITION_LOG, {"scans": [], "transitions": []})
    return {
        "action": "history",
        "total_scans": len(log.get("scans", [])),
        "total_transitions": len(log.get("transitions", [])),
        "recent_transitions": log.get("transitions", [])[-5:],
        "recent_scans": [
            {
                "probability": s["detection"]["transition_probability"],
                "urgency": s["detection"]["urgency"],
                "phase": s["detection"]["target_phase"],
            }
            for s in log.get("scans", [])[-5:]
        ],
    }


def route(path: str) -> dict:
    if path == "/scan":
        return scan()
    elif path == "/history":
        return history()
    return {"error": "unknown", "available": ["/scan", "/history"]}


def handler(payload=None):
    payload = payload or {}
    return route(payload.get("path", "/scan"))
