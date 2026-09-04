from __future__ import annotations
"""Lucid Dungeon — procedural level generation from organism modules."""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DUNGEON_LOG = os.path.join(DATA_DIR, "lucid_dungeons.json")

REALMS = {
    "entropy_desert": {"biome": "sand_and_probability", "hazard": "entropy_storm", "loot": "probability_lens", "difficulty": 3},
    "dream_gravity_zone": {"biome": "surreal_float", "hazard": "gravity_inversion", "loot": "dream_seed", "difficulty": 5},
    "paradox_garden": {"biome": "impossible_bloom", "hazard": "logic_collapse", "loot": "paradox_compass", "difficulty": 4},
    "coherence_cathedral": {"biome": "crystalline_hall", "hazard": "resonance_feedback", "loot": "coherence_mirror", "difficulty": 6},
    "void_abyss": {"biome": "absolute_dark", "hazard": "identity_dissolution", "loot": "void_anchor", "difficulty": 7},
    "temporal_rift": {"biome": "time_fragments", "hazard": "chronological_loop", "loot": "temporal_crystal", "difficulty": 5},
    "mythic_realm": {"biome": "living_stories", "hazard": "narrative_overflow", "loot": "myth_tablet", "difficulty": 8},
    "resonance_depths": {"biome": "harmonic_caves", "hazard": "frequency_shatter", "loot": "resonance_key", "difficulty": 4},
    "fracture_field": {"biome": "broken_ground", "hazard": "reality_gap", "loot": "repair_salve", "difficulty": 3},
    "synchronicity_meadow": {"biome": "coincidence_flowers", "hazard": "meaning_flood", "loot": "synchronicity_beacon", "difficulty": 2},
}

def _load(path, default=None):
    for _p in (path, os.path.join("/tmp", os.path.basename(path))):
        try:
            with open(_p) as f: return json.load(f)
        except Exception: pass
    return default or {}

def _save(p, d):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f: json.dump(d, f, indent=2)
    except OSError:
        with open(os.path.join("/tmp", os.path.basename(p)), "w") as f:
            json.dump(d, f, indent=2)

def _gen_rooms(realm_name: str, realm: dict) -> list:
    rooms = []
    num = random.randint(4, 8)
    room_types = ["entrance", "corridor", "hazard", "treasure", "puzzle", "boss", "shrine", "void_gate"]
    for i in range(num):
        rtype = room_types[min(i, len(room_types)-1)]
        if i == 0: rtype = "entrance"
        if i == num - 1: rtype = "boss"
        rooms.append({
            "id": f"room_{i}", "type": rtype,
            "realm": realm_name, "biome": realm["biome"],
            "hazard": realm["hazard"] if rtype in ("hazard","boss") else None,
            "loot": realm["loot"] if rtype == "treasure" else None,
            "enemies": random.randint(0, 3) if rtype in ("hazard","boss") else 0,
            "hp_required": realm["difficulty"] * (2 if rtype == "boss" else 1),
        })
    return rooms

def generate(realm: str = None) -> dict:
    log = _load(DUNGEON_LOG, {"dungeons": [], "total": 0})
    if realm and realm in REALMS:
        realm_name, realm_data = realm, REALMS[realm]
    else:
        realm_name = random.choice(list(REALMS.keys()))
        realm_data = REALMS[realm_name]

    rooms = _gen_rooms(realm_name, realm_data)
    dungeon = {
        "id": hashlib.sha256(f"dungeon:{realm_name}:{time.time()}".encode()).hexdigest()[:10],
        "realm": realm_name,
        "biome": realm_data["biome"],
        "difficulty": realm_data["difficulty"],
        "rooms": rooms,
        "total_rooms": len(rooms),
        "boss_room": rooms[-1]["id"] if rooms else None,
        "estimated_waves": realm_data["difficulty"] * 2,
        "timestamp": time.time(),
    }
    log["dungeons"].append(dungeon)
    log["dungeons"] = log["dungeons"][-100:]
    log["total"] += 1
    _save(DUNGEON_LOG, log)
    return {"action": "generate", "dungeon": dungeon, "total_dungeons": log["total"]}

def list_realms() -> dict:
    return {"action": "list_realms", "realms": {k: {"biome": v["biome"], "difficulty": v["difficulty"], "hazard": v["hazard"], "loot": v["loot"]} for k, v in REALMS.items()}, "count": len(REALMS)}

def coherence_vitals() -> dict:
    return {"layer": "game", "status": "active", "resonance": 0.85, "wave": "368"}
def resonates_with() -> list:
    return ["lucid_npc", "lucid_physics_rules", "lucid_lore", "lucid_session", "lucid_combat"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/generate")
    if path == "/generate": return generate()
    elif path == "/generate/entropy_desert": return generate("entropy_desert")
    elif path == "/generate/dream_gravity_zone": return generate("dream_gravity_zone")
    elif path == "/generate/paradox_garden": return generate("paradox_garden")
    elif path == "/generate/void_abyss": return generate("void_abyss")
    elif path == "/generate/mythic_realm": return generate("mythic_realm")
    elif path == "/realms": return list_realms()
    return {"error": "unknown", "available": ["/generate", "/generate/{realm}", "/realms"]}
