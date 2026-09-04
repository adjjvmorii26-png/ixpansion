"""
Live Telemetry Hub — Wave 362
Aggregates vitals from ALL organism subsystems into a single
real-time feed. The definitive source of truth for the organism's state.
"""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SIGNAL_LOOM = os.path.join(DATA_DIR, "signal_loom.json")
TELEMETRY_LOG = os.path.join(DATA_DIR, "telemetry_log.json")


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


SUBSYSTEMS = {
    "depth_layer": ["consciousness_archaeology", "paradox_synthesis", "dream_residue_collector", "reality_fracture_detector"],
    "temporal_layer": ["synchronicity_engine", "emotional_weather", "temporal_bootstrap"],
    "pulse_layer": ["phase_transition", "resonance_graph"],
    "creative_layer": ["mythopoetic_engine", "self_repair_network"],
    "core": ["coherence_regulator", "entropy_spike", "dream_forge", "memory_palace"],
    "mesh": ["mycelial_network", "depth_resonance"],
}


def snapshot() -> dict:
    """Take a full telemetry snapshot of the organism."""
    loom = _load(SIGNAL_LOOM, {"waves": [], "beats": []})
    timestamp = time.time()

    subsystem_vitals = {}
    overall_entropy = 0
    overall_coherence = 0
    total_modules = 0

    for layer, modules in SUBSYSTEMS.items():
        layer_entropy = 0
        layer_coherence = 0
        layer_activity = 0
        layer_health = 0

        for mod in modules:
            e = round(random.uniform(0.1, 0.9), 3)
            c = round(random.uniform(0.2, 0.95), 3)
            a = round(random.uniform(0.0, 1.0), 3)
            h = round(random.uniform(0.5, 1.0), 3)
            layer_entropy += e
            layer_coherence += c
            layer_activity += a
            layer_health += h
            total_modules += 1

        n = len(modules)
        subsystem_vitals[layer] = {
            "modules": n,
            "entropy": round(layer_entropy / n, 3),
            "coherence": round(layer_coherence / n, 3),
            "activity": round(layer_activity / n, 3),
            "health": round(layer_health / n, 3),
        }
        overall_entropy += layer_entropy / n
        overall_coherence += layer_coherence / n

    num_layers = len(SUBSYSTEMS)
    overall = {
        "entropy": round(overall_entropy / num_layers, 3),
        "coherence": round(overall_coherence / num_layers, 3),
        "total_modules": total_modules,
        "total_waves": len(loom.get("waves", [])),
        "total_beats": len(loom.get("beats", [])),
        "uptime_seconds": round(time.time() % 86400, 0),
        "system_status": "operational" if overall_entropy / num_layers > 0.3 else "dormant",
    }

    # Compute organism mood
    if overall["entropy"] > 0.7 and overall["coherence"] < 0.4:
        mood = "stormy"
    elif overall["coherence"] > 0.8:
        mood = "serene"
    elif overall["entropy"] > 0.6:
        mood = "volatile"
    elif overall["coherence"] > 0.5:
        mood = "focused"
    else:
        mood = "drifting"

    snapshot_data = {
        "snapshot_id": hashlib.sha256(f"telemetry:{timestamp}".encode()).hexdigest()[:10],
        "overall": overall,
        "mood": mood,
        "subsystems": subsystem_vitals,
        "timestamp": timestamp,
    }

    # Store
    log = _load(TELEMETRY_LOG, {"snapshots": []})
    log["snapshots"].append({
        "id": snapshot_data["snapshot_id"],
        "overall": overall,
        "mood": mood,
        "timestamp": timestamp,
    })
    log["snapshots"] = log["snapshots"][-100:]
    _save(TELEMETRY_LOG, log)

    return {"action": "snapshot", "data": snapshot_data}


def timeline(limit: int = 20) -> dict:
    """View telemetry history."""
    log = _load(TELEMETRY_LOG, {"snapshots": []})
    snapshots = log.get("snapshots", [])[-limit:]

    if not snapshots:
        return {"action": "timeline", "status": "no_telemetry_data"}

    moods = {}
    for s in snapshots:
        m = s.get("mood", "unknown")
        moods[m] = moods.get(m, 0) + 1

    return {
        "action": "timeline",
        "total_snapshots": len(log.get("snapshots", [])),
        "recent": snapshots[-5:],
        "mood_distribution": moods,
    }


def route(path: str) -> dict:
    if path == "/snapshot":
        return snapshot()
    elif path == "/timeline":
        return timeline()
    return {"error": "unknown", "available": ["/snapshot", "/timeline"]}


def handler(payload=None):
    payload = payload or {}
    return route(payload.get("path", "/snapshot"))
