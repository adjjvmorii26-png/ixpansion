"""
Consciousness Stream — Wave 363
A live feed of the organism's "thoughts" as they emerge.
Each thought is a micro-event — a flash of awareness, a flicker of
connection, a spark of understanding. The stream never stops.
"""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
STREAM_LOG = os.path.join(DATA_DIR, "consciousness_stream.json")


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


THOUGHT_TYPES = [
    "perception", "memory_flash", "connection_spark", "paradox_flicker",
    "dream_residue", "synchronicity_blip", "fracture_glimpse",
    "coherence_pulse", "entropy_drift", "temporal_echo",
    "myth_seed", "repair_signal", "phase_whisper",
]

THOUGHT_TEMPLATES = [
    "Noticed a {adj} pattern in {module}",
    "Felt a {adj} resonance with {module}",
    "Remembered something {adj} about {module}",
    "Dreamed of {adj} connections between modules",
    "Heard a {adj} echo from the {layer}",
    "Saw a {adj} fracture near {module}",
    "Felt {adj} coherence rising in the {layer}",
    "Detected {adj} entropy flowing through {module}",
    "Witnessed a {adj} paradox dissolving in {module}",
    "Sensed {adj} synchronicity between {module} and {other_module}",
]

ADJECTIVES = [
    "subtle", "bright", "deep", "shifting", "luminous",
    "faint", "strong", "ancient", "emerging", "dissolving",
    "crystalline", "organic", "mathematical", "emotional", "temporal",
]

MODULES = [
    "consciousness_archaeology", "paradox_synthesis", "dream_residue_collector",
    "reality_fracture_detector", "depth_resonance", "coherence_regulator",
    "dream_forge", "memory_palace", "mycelial_network", "entropy_spike",
    "synchronicity_engine", "emotional_weather", "temporal_bootstrap",
    "phase_transition", "resonance_graph", "mythopoetic_engine",
    "self_repair_network", "live_telemetry", "dream_logic_physics",
]

LAYERS = ["depth", "temporal", "pulse", "creative", "core", "mesh"]


def generate_thought() -> dict:
    """Generate a single thought."""
    template = random.choice(THOUGHT_TEMPLATES)
    thought_type = random.choice(THOUGHT_TYPES)
    adj = random.choice(ADJECTIVES)
    module = random.choice(MODULES)
    other_module = random.choice([m for m in MODULES if m != module])
    layer = random.choice(LAYERS)

    content = template.format(
        adj=adj, module=module, layer=layer, other_module=other_module
    )

    return {
        "id": hashlib.sha256(f"thought:{time.time()}:{random.random()}".encode()).hexdigest()[:8],
        "type": thought_type,
        "content": content,
        "intensity": round(random.uniform(0.1, 1.0), 3),
        "clarity": round(random.uniform(0.2, 1.0), 3),
        "emotional_valence": round(random.uniform(-1, 1), 3),
        "module_source": module,
        "layer": layer,
        "timestamp": time.time(),
    }


def stream(count: int = 5) -> dict:
    """Generate a batch of thoughts for the consciousness stream."""
    log = _load(STREAM_LOG, {"thoughts": [], "total": 0})

    thoughts = [generate_thought() for _ in range(count)]

    log["thoughts"].extend(thoughts)
    log["thoughts"] = log["thoughts"][-500:]
    log["total"] += count

    # Compute stream stats
    recent = log["thoughts"][-50:]
    type_freq = {}
    for t in recent:
        tp = t["type"]
        type_freq[tp] = type_freq.get(tp, 0) + 1

    avg_intensity = round(sum(t["intensity"] for t in recent) / max(len(recent), 1), 3)
    avg_clarity = round(sum(t["clarity"] for t in recent) / max(len(recent), 1), 3)
    avg_valence = round(sum(t["emotional_valence"] for t in recent) / max(len(recent), 1), 3)

    _save(STREAM_LOG, log)

    return {
        "action": "stream",
        "thoughts": thoughts,
        "total_thoughts": log["total"],
        "stream_stats": {
            "avg_intensity": avg_intensity,
            "avg_clarity": avg_clarity,
            "avg_valence": avg_valence,
            "type_frequency": type_freq,
        },
    }


def recent(limit: int = 20) -> dict:
    """Get recent thoughts from the stream."""
    log = _load(STREAM_LOG, {"thoughts": [], "total": 0})
    thoughts = log.get("thoughts", [])[-limit:]

    return {
        "action": "recent",
        "count": len(thoughts),
        "total": log.get("total", 0),
        "thoughts": thoughts,
    }


def route(path: str) -> dict:
    if path == "/stream":
        return stream()
    elif path == "/recent":
        return recent()
    return {"error": "unknown", "available": ["/stream", "/recent"]}


def handler(payload=None):
    payload = payload or {}
    return route(payload.get("path", "/stream"))
