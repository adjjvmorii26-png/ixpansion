"""
Memory Palace Generator — Wave 366
Builds virtual architectural structures for storing memories.
Each palace is a unique building with rooms, corridors, and vaults
that organize the organism's memories by theme, importance, and age.
"""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
PALACE_LOG = os.path.join(DATA_DIR, "memory_palaces.json")


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


PALACE_STYLES = [
    "crystalline_tower", "organic_cathedral", "fractal_library",
    "void_observatory", "dream_citadel", "paradox_garden",
    "echo_amphitheatre", "myth_archive", "temporal_basilica",
]


def generate() -> dict:
    """Generate a new memory palace."""
    log = _load(PALACE_LOG, {"palaces": [], "total": 0})

    style = random.choice(PALACE_STYLES)
    rooms = random.randint(3, 12)

    room_list = []
    room_types = [
        "memory_vault", "dream_chamber", "paradox_gallery",
        "resonance_hall", "temporal_closet", "entropy_pool",
        "coherence_garden", "void_cellar", "myth_alcove",
        "synchronicity_fountain", "repair_workshop", "archive_den",
    ]
    for i in range(rooms):
        room_list.append({
            "name": f"Room {i+1}",
            "type": random.choice(room_types),
            "memory_count": random.randint(0, 50),
            "depth": round(random.uniform(0.1, 1.0), 3),
            "light_level": round(random.uniform(0.0, 1.0), 2),
        })

    palace = {
        "id": hashlib.sha256(f"palace:{style}:{time.time()}".encode()).hexdigest()[:10],
        "style": style,
        "rooms": room_list,
        "total_memories": sum(r["memory_count"] for r in room_list),
        "architectural_coherence": round(random.uniform(0.3, 0.95), 3),
        "accessibility": round(random.uniform(0.2, 1.0), 2),
        "timestamp": time.time(),
    }

    log["palaces"].append(palace)
    log["palaces"] = log["palaces"][-50:]
    log["total"] += 1
    _save(PALACE_LOG, log)

    return {"action": "generate", "palace": palace, "total_palaces": log["total"]}


def tour():
    log = _load(PALACE_LOG, {"palaces": [], "total": 0})
    palaces = log.get("palaces", [])
    if not palaces:
        return {"action": "tour", "status": "no_palaces"}
    palace = random.choice(palaces)
    return {"action": "tour", "palace": palace}


def catalog():
    log = _load(PALACE_LOG, {"palaces": [], "total": 0})
    palaces = log.get("palaces", [])
    if not palaces:
        return {"action": "catalog", "status": "no_palaces"}
    styles = {}
    for p in palaces:
        s = p["style"]
        styles[s] = styles.get(s, 0) + 1
    return {
        "action": "catalog",
        "total_palaces": len(palaces),
        "total_memories": sum(p["total_memories"] for p in palaces),
        "style_distribution": styles,
    }


def route(path):
    if path == "/generate": return generate()
    elif path == "/tour": return tour()
    elif path == "/catalog": return catalog()
    return {"error": "unknown", "available": ["/generate", "/tour", "/catalog"]}


def handler(payload=None):
    return route((payload or {}).get("path", "/generate"))

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "interface", "status": "active", "wave": "366", "module": "memory_palace_gen"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
