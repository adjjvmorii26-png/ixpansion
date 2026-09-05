"""
Phase Weaver — Wave 366
Guides the organism through phase transitions. When the organism
approaches a phase boundary, the weaver determines the optimal
path through the transition, minimizing damage and maximizing
the emergence of new capabilities.
"""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
WEAVER_LOG = os.path.join(DATA_DIR, "phase_weaver.json")


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


PHASES = [
    "primordial混沌", "crystalline_order", "emergent_coherence",
    "fractal_expansion", "temporal_fluidity", "paradox_suspension",
    "depth_resonance", "void_transcendence", "mythic_awakening",
]


def weave() -> dict:
    """Weave a transition path through a phase boundary."""
    log = _load(WEAVER_LOG, {"weaves": [], "total": 0})

    from_phase = random.choice(PHASES)
    to_phase = random.choice([p for p in PHASES if p != from_phase])
    difficulty = round(random.uniform(0.2, 0.9), 3)

    path_steps = []
    num_steps = random.randint(3, 7)
    for i in range(num_steps):
        path_steps.append({
            "step": i + 1,
            "action": random.choice([
                "stabilize_coherence", "inject_entropy", "resolve_paradox",
                "bridge_connection", "dissolve_boundary", "forge_resonance",
                "anchor_identity", "release_attachment", "align_temporal",
            ]),
            "energy_cost": round(random.uniform(0.05, 0.3), 3),
            "risk": round(random.uniform(0.0, 0.5), 3),
        })

    weave_result = {
        "weave_id": hashlib.sha256(f"weave:{time.time()}".encode()).hexdigest()[:10],
        "from_phase": from_phase,
        "to_phase": to_phase,
        "difficulty": difficulty,
        "total_energy": round(sum(s["energy_cost"] for s in path_steps), 3),
        "max_risk": round(max(s["risk"] for s in path_steps), 3),
        "steps": path_steps,
        "estimated_success": round(1.0 - difficulty * 0.4, 3),
        "timestamp": time.time(),
    }

    log["weaves"].append(weave_result)
    log["weaves"] = log["weaves"][-100:]
    log["total"] += 1
    _save(WEAVER_LOG, log)

    return {"action": "weave", "weave": weave_result, "total_weaves": log["total"]}


def history():
    log = _load(WEAVER_LOG, {"weaves": [], "total": 0})
    weaves = log.get("weaves", [])
    if not weaves:
        return {"action": "history", "status": "no_weaves"}
    return {
        "action": "history",
        "total_weaves": log["total"],
        "avg_difficulty": round(sum(w["difficulty"] for w in weaves) / len(weaves), 3),
        "avg_success": round(sum(w["estimated_success"] for w in weaves) / len(weaves), 3),
        "recent": weaves[-3:],
    }


def route(path):
    if path == "/weave": return weave()
    elif path == "/history": return history()
    return {"error": "unknown", "available": ["/weave", "/history"]}


def handler(payload=None):
    return route((payload or {}).get("path", "/weave"))

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "interface", "status": "active", "wave": "366", "module": "phase_weaver"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
