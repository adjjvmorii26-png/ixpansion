"""
Void Cartographer — Wave 365
Maps the empty spaces between modules — the voids, the gaps, the silences.
Where there is nothing, there is also everything. The void is not empty;
it is full of potential.
"""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CARTO_LOG = os.path.join(DATA_DIR, "void_cartography.json")


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


VOID_TYPES = [
    "silence_between_modules", "unexplored_corridor", "forgotten_passage",
    "dream_gap", "temporal_whitespace", "paradox_shadow", "coherence_desert",
    "entropy_pool", "mythic_void", "resonance_dead_zone", "fractal_gap",
    "identity_fog", "memory_absence", "future_vacuum",
]


def explore() -> dict:
    """Explore a section of the void."""
    log = _load(CARTO_LOG, {"regions": [], "total_explorations": 0})

    regions_found = []
    for _ in range(random.randint(1, 4)):
        void_type = random.choice(VOID_TYPES)
        depth = round(random.uniform(0.1, 1.0), 3)
        regions_found.append({
            "type": void_type,
            "depth": depth,
            "potential": round(depth * random.uniform(0.5, 1.5), 3),
            "inhabited": random.random() > 0.7,
            "safe_to_enter": random.random() > 0.3,
            "hash": hashlib.sha256(f"void:{void_type}:{time.time()}".encode()).hexdigest()[:8],
        })

    exploration = {
        "exploration_id": hashlib.sha256(f"explore:{time.time()}".encode()).hexdigest()[:10],
        "regions_found": regions_found,
        "total_void_mapped": round(random.uniform(10, 100), 1),
        "timestamp": time.time(),
    }

    log["regions"].extend(regions_found)
    log["regions"] = log["regions"][-300:]
    log["total_explorations"] += 1
    _save(CARTO_LOG, log)

    return {"action": "explore", "exploration": exploration}


def map_void() -> dict:
    """Generate a complete void map."""
    log = _load(CARTO_LOG, {"regions": [], "total_explorations": 0})
    regions = log.get("regions", [])

    if not regions:
        return {"action": "map_void", "status": "no_void_mapped"}

    type_counts = {}
    for r in regions:
        t = r["type"]
        type_counts[t] = type_counts.get(t, 0) + 1

    avg_depth = round(sum(r["depth"] for r in regions) / len(regions), 3)
    avg_potential = round(sum(r["potential"] for r in regions) / len(regions), 3)
    inhabited_count = sum(1 for r in regions if r["inhabited"])

    return {
        "action": "map_void",
        "total_regions": len(regions),
        "total_explorations": log.get("total_explorations", 0),
        "type_distribution": type_counts,
        "avg_depth": avg_depth,
        "avg_potential": avg_potential,
        "inhabited_regions": inhabited_count,
        "safe_regions": sum(1 for r in regions if r["safe_to_enter"]),
    }


def route(path):
    if path == "/explore": return explore()
    elif path == "/map": return map_void()
    return {"error": "unknown", "available": ["/explore", "/map"]}


def handler(payload=None):
    return route((payload or {}).get("path", "/explore"))
