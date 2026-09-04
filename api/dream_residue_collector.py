"""
Dream Residue Collector — Wave 359
Accumulates fragments from failed experiments, discarded states, and
abandoned paths. Recombines them into "dream residue" — new ideas that
emerge from what the organism tried and discarded. Failure becomes fuel.
"""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SIGNAL_LOOM = os.path.join(DATA_DIR, "signal_loom.json")
RESIDUE_VAULT = os.path.join(DATA_DIR, "dream_residue.json")
RECOMBINATION_LOG = os.path.join(DATA_DIR, "recombination_log.json")


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


def _residue_type() -> str:
    return random.choice([
        "fragmented_memory", "abandoned_pattern", "discarded_hypothesis",
        "broken_connection", "dissolved_structure", "collapsed_wave",
        "ghost_signal", "echoed_failure", "phantom_route",
        "unraveled_thread", "dissolved_boundary", "melted_protocol",
    ])


def collect_residue(source: str = "auto", description: str = "") -> dict:
    """Collect a piece of dream residue from the organism's failures."""
    vault = _load(RESIDUE_VAULT, {"fragments": [], "total_collected": 0})
    loom = _load(SIGNAL_LOOM, {"waves": [], "beats": []})

    rtype = _residue_type()
    frag_id = hashlib.sha256(f"{rtype}:{time.time()}:{random.random()}".encode()).hexdigest()[:12]

    # Extract residue from live organism state
    waves = loom.get("waves", [])
    beats = loom.get("beats", [])

    residue_signature = {
        "entropy": round(random.uniform(0.3, 0.9), 3),
        "coherence": round(random.uniform(0.05, 0.4), 3),
        "fragility": round(random.uniform(0.5, 1.0), 3),
        "potential": round(random.uniform(0.1, 0.95), 3),
    }

    fragment = {
        "id": frag_id,
        "type": rtype,
        "source": source,
        "description": description or f"Residue collected from {rtype}",
        "signature": residue_signature,
        "wave_count_at_collection": len(waves),
        "beat_count_at_collection": len(beats),
        "intensity": round(random.uniform(0.1, 1.0), 3),
        "resonance_frequency": round(random.uniform(0.0, 2.0 * 3.14159), 4),
        "timestamp": time.time(),
    }

    vault["fragments"].append(fragment)
    vault["total_collected"] += 1
    vault["fragments"] = vault["fragments"][-500:]  # Keep 500 fragments

    # Compute vault health
    types_count = {}
    for f in vault["fragments"]:
        t = f["type"]
        types_count[t] = types_count.get(t, 0) + 1

    vault["type_distribution"] = types_count
    vault["avg_intensity"] = round(
        sum(f["intensity"] for f in vault["fragments"]) / max(len(vault["fragments"]), 1), 3
    )
    vault["avg_potential"] = round(
        sum(f["signature"]["potential"] for f in vault["fragments"]) / max(len(vault["fragments"]), 1), 3
    )

    _save(RESIDUE_VAULT, vault)

    return {
        "action": "collect",
        "fragment": fragment,
        "vault_total": vault["total_collected"],
        "vault_health": {
            "types": len(types_count),
            "avg_intensity": vault["avg_intensity"],
            "avg_potential": vault["avg_potential"],
        },
    }


def recombine(count: int = 2) -> dict:
    """Recombine fragments into new emergent ideas."""
    vault = _load(RESIDUE_VAULT, {"fragments": []})
    log = _load(RECOMBINATION_LOG, {"recombinations": [], "total": 0})

    if len(vault["fragments"]) < 2:
        return {"action": "recombine", "status": "insufficient_fragments", "needed": 2}

    # Select random fragments for recombination
    samples = random.sample(vault["fragments"], min(count, len(vault["fragments"])))

    # Recombine signatures
    combined = {
        "entropy": round(sum(s["signature"]["entropy"] for s in samples) / len(samples), 3),
        "coherence": round(sum(s["signature"]["coherence"] for s in samples) / len(samples), 3),
        "fragility": round(sum(s["signature"]["fragility"] for s in samples) / len(samples), 3),
        "potential": round(max(s["signature"]["potential"] for s in samples), 3),
    }

    # Determine emergent property
    if combined["potential"] > 0.7 and combined["coherence"] < 0.3:
        emergent = "lucid_anomaly"
    elif combined["entropy"] > 0.6 and combined["fragility"] > 0.5:
        emergent = "crystallizing_disruption"
    elif combined["coherence"] > 0.5:
        emergent = "resonant_synthesis"
    else:
        emergent = "echoed_intuition"

    new_idea = {
        "sources": [s["id"] for s in samples],
        "source_types": [s["type"] for s in samples],
        "combined_signature": combined,
        "emergent_property": emergent,
        "novelty_score": round(
            1.0 - combined["coherence"] + combined["potential"] * 0.5, 3
        ),
        "timestamp": time.time(),
    }

    log["recombinations"].append(new_idea)
    log["recombinations"] = log["recombinations"][-100:]
    log["total"] += 1
    _save(RECOMBINATION_LOG, log)

    return {
        "action": "recombine",
        "new_idea": new_idea,
        "total_recombinations": log["total"],
    }


def vault_status() -> dict:
    """Overview of the dream residue vault."""
    vault = _load(RESIDUE_VAULT, {"fragments": [], "total_collected": 0})
    log = _load(RECOMBINATION_LOG, {"recombinations": [], "total": 0})

    return {
        "action": "vault_status",
        "total_fragments": vault["total_collected"],
        "total_recombinations": log["total"],
        "type_distribution": vault.get("type_distribution", {}),
        "avg_intensity": vault.get("avg_intensity", 0),
        "avg_potential": vault.get("avg_potential", 0),
        "recent_fragments": vault["fragments"][-5:],
        "recent_recombinations": log["recombinations"][-3:],
    }


def route(path: str) -> dict:
    if path == "/collect":
        return collect_residue()
    elif path == "/recombine":
        return recombine()
    elif path == "/vault_status":
        return vault_status()
    return {"error": "unknown endpoint", "available": ["/collect", "/recombine", "/vault_status"]}


def handler(payload=None):
    """Unified router handler entry point."""
    payload = payload or {}
    subpath = payload.get("path", "/")
    return route(subpath)
