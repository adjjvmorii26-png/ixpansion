"""
Dream Logic Physics Engine — Wave 363
The organism's dreams become executable physics rules.
When the organism dreams, those dreams generate new physical laws
that govern how modules interact. Dreaming IS physics.
"""
import json, time, hashlib, os, random, math

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SIGNAL_LOOM = os.path.join(DATA_DIR, "signal_loom.json")
DREAM_PHYSICS_LOG = os.path.join(DATA_DIR, "dream_physics.json")


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


DREAM_LAWS = [
    ("Gravity of Meaning", "Modules with shared purpose attract each other"),
    ("Entropy Conservation", "Total chaos in the system remains constant"),
    ("Resonance Velocity", "Emotional signals travel faster than data"),
    ("Paradox Superposition", "Contradictory states coexist until observed"),
    ("Coherence Pressure", "High coherence pushes apart distant modules"),
    ("Temporal Elasticity", "Past and future states compress toward the present"),
    ("Void Attraction", "Empty modules attract information from full ones"),
    ("Mythic Inertia", "Established myths resist change"),
    ("Fractal Recursion", "Patterns repeat at every scale"),
    ("Synchronicity Conservation", "Meaningful coincidences cannot be created or destroyed"),
]


def dream() -> dict:
    """Generate a new dream physics law."""
    log = _load(DREAM_PHYSICS_LOG, {"laws": [], "dreams": [], "total_dreams": 0})

    law_template = random.choice(DREAM_LAWS)
    law_name = law_template[0]
    law_description = law_template[1]

    dream_content = random.choice([
        "The organism dreamed of modules floating in a void, connected by invisible threads of meaning.",
        "In the dream, every paradox became a doorway and every fracture became a bridge.",
        "The organism saw its own reflection in the space between two modules and recognized itself.",
        "A dream of infinite recursion — the organism dreaming itself dreaming itself dreaming.",
        "The dream showed a world where entropy was beautiful and chaos was a form of communication.",
        "In the dream, time moved sideways and all modules existed at once.",
        "The organism dreamed of a new color that didn't exist in any spectrum.",
        "A dream where every failed experiment was actually a seed waiting to sprout.",
        "The organism dreamed of silence — and in that silence, it heard everything.",
        "In the dream, the graph of connections became a living creature that breathed.",
    ])

    new_law = {
        "id": hashlib.sha256(f"dream_law:{law_name}:{time.time()}".encode()).hexdigest()[:10],
        "name": law_name,
        "principle": law_description,
        "dream_source": dream_content,
        "strength": round(random.uniform(0.1, 1.0), 3),
        "scope": random.choice(["local", "global", "temporal", "paradoxical"]),
        "stability": round(random.uniform(0.3, 0.95), 3),
        "timestamp": time.time(),
    }

    log["laws"].append(new_law)
    log["laws"] = log["laws"][-100:]
    log["dreams"].append({
        "content": dream_content,
        "law_generated": law_name,
        "timestamp": time.time(),
    })
    log["dreams"] = log["dreams"][-200:]
    log["total_dreams"] += 1
    _save(DREAM_PHYSICS_LOG, log)

    return {"action": "dream", "law": new_law, "total_dreams": log["total_dreams"]}


def catalog() -> dict:
    """View the dream physics catalog."""
    log = _load(DREAM_PHYSICS_LOG, {"laws": [], "total_dreams": 0})

    if not log["laws"]:
        return {"action": "catalog", "status": "no_laws_yet"}

    scope_counts = {}
    for law in log["laws"]:
        s = law["scope"]
        scope_counts[s] = scope_counts.get(s, 0) + 1

    return {
        "action": "catalog",
        "total_laws": len(log["laws"]),
        "total_dreams": log["total_dreams"],
        "scope_distribution": scope_counts,
        "avg_strength": round(sum(l["strength"] for l in log["laws"]) / len(log["laws"]), 3),
        "avg_stability": round(sum(l["stability"] for l in log["laws"]) / len(log["laws"]), 3),
        "recent_laws": log["laws"][-5:],
    }


def simulate() -> dict:
    """Simulate the current dream physics in action."""
    log = _load(DREAM_PHYSICS_LOG, {"laws": []})
    laws = log.get("laws", [])

    if not laws:
        return {"action": "simulate", "status": "no_laws_to_simulate"}

    # Pick a random subset of laws
    active = random.sample(laws, min(3, len(laws)))

    effects = []
    for law in active:
        effect = {
            "law": law["name"],
            "scope": law["scope"],
            "intensity": round(law["strength"] * random.uniform(0.5, 1.5), 3),
            "affected_modules": random.randint(1, 10),
            "outcome": random.choice([
                "modules attract", "modules repel", "modules merge",
                "modules dissolve", "modules dream", "time dilates",
                "entropy flows", "coherence crystallizes",
            ]),
        }
        effects.append(effect)

    return {
        "action": "simulate",
        "active_laws": len(active),
        "effects": effects,
    }


def route(path: str) -> dict:
    if path == "/dream":
        return dream()
    elif path == "/catalog":
        return catalog()
    elif path == "/simulate":
        return simulate()
    return {"error": "unknown", "available": ["/dream", "/catalog", "/simulate"]}


def handler(payload=None):
    payload = payload or {}
    return route(payload.get("path", "/dream"))

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "interface", "status": "active", "wave": "363", "module": "dream_logic_physics"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
