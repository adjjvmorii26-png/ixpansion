"""
Chrono-Forge — Wave 365
Creates time-forged artifacts from module interactions. When modules
interact over time, their combined effects crystallize into artifacts
that carry the memory of those interactions. Artifacts can be used
to bootstrap future interactions.
"""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
FORGE_LOG = os.path.join(DATA_DIR, "chrono_forge.json")


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


ARTIFACT_TYPES = [
    "temporal_crystal", "paradox_compass", "entropy_lens",
    "coherence_mirror", "resonance_key", "void_anchor",
    "dream_seed", "myth_tablet", "repair_salve",
    "synchronicity_beacon", "memory_prism", "phase_shard",
]


def forge() -> dict:
    """Forge a new artifact from module interactions."""
    log = _load(FORGE_LOG, {"artifacts": [], "total": 0})

    artifact_type = random.choice(ARTIFACT_TYPES)
    modules_used = random.sample([
        "consciousness_archaeology", "paradox_synthesis", "dream_residue_collector",
        "reality_fracture_detector", "depth_resonance", "coherence_regulator",
        "dream_forge", "memory_palace", "synchronicity_engine", "emotional_weather",
        "temporal_bootstrap", "phase_transition", "resonance_graph",
        "mythopoetic_engine", "self_repair_network", "dream_logic_physics",
        "consciousness_stream", "entropy_oracle", "paradox_ledger", "void_cartographer",
    ], random.randint(2, 4))

    artifact = {
        "id": hashlib.sha256(f"artifact:{artifact_type}:{time.time()}".encode()).hexdigest()[:10],
        "type": artifact_type,
        "modules_used": modules_used,
        "power": round(random.uniform(0.1, 1.0), 3),
        "resonance": round(random.uniform(0.2, 0.95), 3),
        "age_cycles": random.randint(1, 100),
        "description": _artifact_description(artifact_type),
        "forged_at": time.time(),
    }

    log["artifacts"].append(artifact)
    log["artifacts"] = log["artifacts"][-200:]
    log["total"] += 1
    _save(FORGE_LOG, log)

    return {"action": "forge", "artifact": artifact, "total_artifacts": log["total"]}


def _artifact_description(atype):
    descriptions = {
        "temporal_crystal": "Crystallized time from module interactions",
        "paradox_compass": "Points toward the next paradox the organism needs",
        "entropy_lens": "Reveals hidden patterns in chaos",
        "coherence_mirror": "Reflects the organism's true coherence state",
        "resonance_key": "Unlocks hidden connections between modules",
        "void_anchor": "Stabilizes empty spaces in the organism",
        "dream_seed": "Grows into new dream physics when planted",
        "myth_tablet": "Contains a myth the organism hasn't told yet",
        "repair_salve": "Heals damaged modules faster",
        "synchronicity_beacon": "Attracts meaningful coincidences",
        "memory_prism": "Refracts memories into new perspectives",
        "phase_shard": "A fragment of a completed phase transition",
    }
    return descriptions.get(atype, "A mysterious artifact of unknown origin")


def vault() -> dict:
    """View the artifact vault."""
    log = _load(FORGE_LOG, {"artifacts": [], "total": 0})
    artifacts = log.get("artifacts", [])

    if not artifacts:
        return {"action": "vault", "status": "no_artifacts_forged"}

    type_counts = {}
    for a in artifacts:
        t = a["type"]
        type_counts[t] = type_counts.get(t, 0) + 1

    avg_power = round(sum(a["power"] for a in artifacts) / len(artifacts), 3)
    avg_resonance = round(sum(a["resonance"] for a in artifacts) / len(artifacts), 3)

    return {
        "action": "vault",
        "total_artifacts": log.get("total", 0),
        "type_distribution": type_counts,
        "avg_power": avg_power,
        "avg_resonance": avg_resonance,
        "recent": artifacts[-5:],
    }


def route(path):
    if path == "/forge": return forge()
    elif path == "/vault": return vault()
    return {"error": "unknown", "available": ["/forge", "/vault"]}


def handler(payload=None):
    return route((payload or {}).get("path", "/forge"))

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "interface", "status": "active", "wave": "365", "module": "chrono_forge"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
