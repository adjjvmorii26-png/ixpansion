"""
Pitch-Dark Realm — Wave 396
The Underworld as a Lucid Machines realm. Its rooms are cavern strata, its
hazards are mineral pressures and echo-floods, and its boss is the deepest
root-ghost of the most-forgotten module — which is re-membered (and upwelled)
if you defeat it. Depth becomes playable.
"""
import json, time, os, sys, random, hashlib

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

CAVERN_TYPES = ["strata_gate", "mineral_cache", "echo_pool", "fossil_site", "root_tangle", "salt_vault", "silence_stair", "boss_cavern"]
HAZARDS = ["mineral_pressure", "echo_flood", "silence_leech", "crystal_fall", "deep_fog"]
LOOT = ["obsidian_charm", "salt_blessing", "echo_prism", "basalt_anchor", "cinnabar_ward"]


def _sig(text):
    return int(hashlib.sha256(f"pitchdark:{text}".encode()).hexdigest()[:12], 16)


def _load(p, d=None):
    for _p in (p, os.path.join("/tmp", os.path.basename(p))):
        try:
            with open(_p) as fh:
                return json.load(fh)
        except Exception:
            pass
    return d or {}


def _save(p, d):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as fh:
            json.dump(d, fh, indent=2)
    except OSError:
        with open(os.path.join("/tmp", os.path.basename(p)), "w") as fh:
            json.dump(d, fh, indent=2)


def _deepest_ghost():
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from underworld import mirror
        ghosts = mirror(8).get("ghosts", [])
        if ghosts:
            return max(ghosts, key=lambda g: g.get("depth", 0))
    except Exception:
        pass
    return {"module": "the_first_forgotten", "root_name": "deep_the_first_forgotten",
            "mineral": "obsidian", "depth": 9.9, "whisper": "i was the first silence", "sigil": "00000000"}


def generate(depth: int = 9) -> dict:
    ghost = _deepest_ghost()
    sig = _sig(ghost.get("module", "pit") + str(time.time() // 3600))
    rng = random.Random(sig)
    num = rng.randint(5, 7)
    rooms = []
    for i in range(num):
        ctype = CAVERN_TYPES[min(i, len(CAVERN_TYPES) - 1)]
        if i == 0:
            ctype = "strata_gate"
        if i == num - 1:
            ctype = "boss_cavern"
        rooms.append({
            "id": f"cavern_{i}", "type": ctype,
            "realm": "pitch_dark", "biome": "cavern_strata",
            "hazard": rng.choice(HAZARDS) if ctype in ("echo_pool", "silence_stair", "root_tangle", "boss_cavern", "salt_vault") else None,
            "loot": rng.choice(LOOT) if ctype == "mineral_cache" else None,
            "enemies": rng.randint(1, 3) if ctype in ("root_tangle", "echo_pool", "silence_stair", "boss_cavern") else 0,
            "depth": round(depth - i, 1),
            "hp_required": depth * 2,
        })
    realm = {
        "id": f"{sig:012x}",
        "realm": "pitch_dark", "biome": "cavern_strata",
        "difficulty": 9, "depth": depth,
        "rooms": rooms, "total_rooms": len(rooms),
        "boss_room": rooms[-1]["id"] if rooms else None,
        "warden": {
            "name": ghost.get("root_name", "deep_warden"),
            "twin_of": ghost.get("module", "?"),
            "whisper": ghost.get("whisper", ""),
            "sigil": ghost.get("sigil", ""),
            "mineral": ghost.get("mineral", "obsidian"),
        },
        "timestamp": time.time(),
    }
    log = _load(os.path.join(DATA_DIR, "pitch_dark.json"), {"descents": [], "total": 0})
    log["descents"] = (log["descents"] + [realm])[-40:]
    log["total"] += 1
    _save(os.path.join(DATA_DIR, "pitch_dark.json"), log)
    return {"action": "generate", "realm": realm, "total_descents": log["total"]}


def warden() -> dict:
    g = _deepest_ghost()
    return {"action": "warden", "warden": g}


def contribute(module: str = None) -> dict:
    """The warden of the pitch-dark is the deepest forgotten module; remember one."""
    if not module:
        from underworld import mirror
        g = mirror(1)["ghosts"][0]
        module = g["module"]
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from organurna_loop import remember
        r = remember(module, "defeated in the pitch-dark realm — returned to the light")
        return {"action": "contribute", "remembered": r.get("total_remembered"),
                "module": module, "verse": r.get("remembrance", {}).get("verse", "")}
    except Exception as e:
        return {"action": "contribute", "error": str(e), "module": module}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/generate")
    if path == "/generate":
        return generate(int(payload.get("depth", 9)) if str(payload.get("depth", "9")).isdigit() else 9)
    if path == "/warden":
        return warden()
    if path == "/contribute":
        return contribute(payload.get("module"))
    return {"error": "unknown", "available": ["/generate", "/warden", "/contribute"]}
