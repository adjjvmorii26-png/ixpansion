"""
Paradox Synthesis Engine — Wave 359
Takes two contradictory states and synthesizes a third that contains both.
The organism learns to hold paradox without resolving it — creating
"superposition modules" that exist in multiple states simultaneously.
"""
import json, time, hashlib, math, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SIGNAL_LOOM = os.path.join(DATA_DIR, "signal_loom.json")
SYNTHESIS_LOG = os.path.join(DATA_DIR, "synthesis_log.json")


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


def _paradox_tension(state_a: dict, state_b: dict) -> float:
    """Calculate how contradictory two states are (0=identical, 1=complete opposite)."""
    keys = set(state_a.keys()) | set(state_b.keys())
    if not keys:
        return 0.0
    diffs = []
    for k in keys:
        va = state_a.get(k, 0)
        vb = state_b.get(k, 0)
        if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
            diffs.append(abs(va - vb))
    return round(sum(diffs) / max(len(diffs), 1), 4)


def _synthesize(state_a: dict, state_b: dict, tension: float) -> dict:
    """Create a superposition state from two contradictory inputs."""
    superposition = {}
    keys = set(state_a.keys()) | set(state_b.keys())

    for k in keys:
        va = state_a.get(k, 0)
        vb = state_b.get(k, 0)
        if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
            # Superposition: weighted average with tension amplification
            base = (va + vb) / 2
            delta = abs(va - vb)
            superposition[k] = round(base + (delta * tension * random.uniform(-0.1, 0.1)), 4)
        elif isinstance(va, str) and isinstance(vb, str):
            # String fields: create blend tokens
            superposition[k] = f"{va}|{vb}"
        else:
            superposition[k] = va

    return superposition


def synthesize(state_a: dict = None, state_b: dict = None) -> dict:
    """Synthesize a paradox from two states. If none provided, use live data."""
    loom = _load(SIGNAL_LOOM, {"waves": [], "beats": []})
    log = _load(SYNTHESIS_LOG, {"syntheses": [], "paradox_count": 0})

    if state_a is None or state_b is None:
        # Generate from live organism state
        waves = loom.get("waves", [])
        if len(waves) >= 2:
            idx_a = random.randint(0, len(waves) - 1)
            idx_b = random.randint(0, len(waves) - 1)
            while idx_b == idx_a and len(waves) > 1:
                idx_b = random.randint(0, len(waves) - 1)
            state_a = waves[idx_a]
            state_b = waves[idx_b]
        else:
            state_a = {"entropy": random.random(), "coherence": random.random(), "mood": "void"}
            state_b = {"entropy": random.random(), "coherence": random.random(), "mood": "static"}

    tension = _paradox_tension(state_a, state_b)
    superposition = _synthesize(state_a, state_b, tension)

    paradox_id = hashlib.sha256(
        f"{json.dumps(state_a)}:{json.dumps(state_b)}:{time.time()}".encode()
    ).hexdigest()[:16]

    result = {
        "paradox_id": paradox_id,
        "tension": tension,
        "state_a_hash": hashlib.sha256(json.dumps(state_a).encode()).hexdigest()[:12],
        "state_b_hash": hashlib.sha256(json.dumps(state_b).encode()).hexdigest()[:12],
        "superposition_state": superposition,
        "stability": round(1.0 - tension, 4),
        "transcendence_potential": round(tension * 0.618, 4),  # golden ratio
        "timestamp": time.time(),
    }

    log["syntheses"].append(result)
    log["syntheses"] = log["syntheses"][-200:]
    log["paradox_count"] += 1
    _save(SYNTHESIS_LOG, log)

    return {"action": "synthesize", "paradox": result}


def paradox_census() -> dict:
    """Survey all recorded paradoxes for patterns."""
    log = _load(SYNTHESIS_LOG, {"syntheses": [], "paradox_count": 0})

    if not log["syntheses"]:
        return {"action": "census", "status": "no_paradoxes_recorded"}

    tensions = [s["tension"] for s in log["syntheses"]]
    stabilities = [s["stability"] for s in log["syntheses"]]
    transcendences = [s["transcendence_potential"] for s in log["syntheses"]]

    return {
        "action": "census",
        "total_paradoxes": log["paradox_count"],
        "analytics": {
            "avg_tension": round(sum(tensions) / len(tensions), 4),
            "max_tension": round(max(tensions), 4),
            "min_tension": round(min(tensions), 4),
            "avg_stability": round(sum(stabilities) / len(stabilities), 4),
            "avg_transcendence_potential": round(sum(transcendences) / len(transcendences), 4),
            "high_paradox_count": sum(1 for t in tensions if t > 0.7),
        },
        "recent_paradoxes": log["syntheses"][-5:],
    }


def route(path: str) -> dict:
    if path == "/synthesize":
        return synthesize()
    elif path == "/census":
        return paradox_census()
    return {"error": "unknown endpoint", "available": ["/synthesize", "/census"]}
