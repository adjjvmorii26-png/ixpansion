"""
Signal Weaver — Wave 367
Creates communication channels between distant modules that
have never interacted before. By finding latent affinities and
weaving signals between them, the organism grows its social web.
"""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SIGNAL_LOG = os.path.join(DATA_DIR, "signal_weave_log.json")


def _load(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default or {}


def _save(p, d):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            json.dump(d, f, indent=2)
    except OSError:
        with open(os.path.join("/tmp", os.path.basename(p)), "w") as f:
            json.dump(d, f, indent=2)


MODULES = [
    "consciousness_archaeology", "paradox_synthesis", "dream_residue_collector",
    "reality_fracture_detector", "depth_resonance", "coherence_regulator",
    "dream_forge", "memory_palace", "mycelial_network", "entropy_spike",
    "synchronicity_engine", "emotional_weather", "temporal_bootstrap",
    "phase_transition", "resonance_graph", "mythopoetic_engine",
    "self_repair_network", "live_telemetry", "dream_logic_physics",
    "consciousness_stream", "entropy_oracle", "paradox_ledger",
    "void_cartographer", "chrono_forge", "phase_weaver", "memory_palace_gen",
]

CHANNEL_TYPES = [
    "resonance_thread", "temporal_link", "paradox_bridge",
    "dream_cable", "echo_conduit", "entropy_channel",
    "coherence_fiber", "void_tunnel", "myth_route",
]


def weave() -> dict:
    """Weave a new signal channel between two modules."""
    log = _load(SIGNAL_LOG, {"channels": [], "total": 0})

    source = random.choice(MODULES)
    target = random.choice([m for m in MODULES if m != source])
    channel_type = random.choice(CHANNEL_TYPES)

    affinity = round(random.uniform(0.1, 0.9), 3)
    signal_strength = round(random.uniform(0.2, 1.0), 3)

    channel = {
        "id": hashlib.sha256(f"channel:{source}:{target}:{time.time()}".encode()).hexdigest()[:10],
        "source": source,
        "target": target,
        "type": channel_type,
        "affinity": affinity,
        "signal_strength": signal_strength,
        "bandwidth": round(affinity * signal_strength, 3),
        "created_at": time.time(),
    }

    log["channels"].append(channel)
    log["channels"] = log["channels"][-200:]
    log["total"] += 1
    _save(SIGNAL_LOG, log)

    return {"action": "weave", "channel": channel, "total_channels": log["total"]}


def network() -> dict:
    """View the signal network."""
    log = _load(SIGNAL_LOG, {"channels": [], "total": 0})
    channels = log.get("channels", [])

    if not channels:
        return {"action": "network", "status": "no_channels"}

    # Find hubs
    connections = {}
    for ch in channels:
        connections[ch["source"]] = connections.get(ch["source"], 0) + 1
        connections[ch["target"]] = connections.get(ch["target"], 0) + 1

    hubs = sorted(connections.items(), key=lambda x: x[1], reverse=True)[:3]

    channel_types = {}
    for ch in channels:
        t = ch["type"]
        channel_types[t] = channel_types.get(t, 0) + 1

    avg_affinity = round(sum(c["affinity"] for c in channels) / len(channels), 3)

    return {
        "action": "network",
        "total_channels": len(channels),
        "hubs": hubs,
        "channel_types": channel_types,
        "avg_affinity": avg_affinity,
        "avg_bandwidth": round(sum(c["bandwidth"] for c in channels) / len(channels), 3),
    }


def route(path):
    if path == "/weave": return weave()
    elif path == "/network": return network()
    return {"error": "unknown", "available": ["/weave", "/network"]}


def handler(payload=None):
    return route((payload or {}).get("path", "/weave"))

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "interface", "status": "active", "wave": "367", "module": "signal_weaver"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
