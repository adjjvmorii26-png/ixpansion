"""
Wave Seed — Wave 385
Any word is a world. A seed phrase deterministically renders an entire Lucid
Machines realm: the dungeon, its keeper, and your first gear — all born of
the same entropy. Share a seed and share a world.
"""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SEED_LOG = os.path.join(DATA_DIR, "wave_seeds.json")

GLYPHS = "0123456789abcdefghijklmnopqrstuvwxyz"
SIGIL_GLYPHS = "◈◇✦✧⬡⌘∞∴⟡◉✺▲◆✹"


def _sig(seed: str) -> int:
    return int(hashlib.sha256(f"waveseed:{seed or ''}".encode()).hexdigest()[:14], 16)


def _get(path, default=None):
    for _p in (path, os.path.join("/tmp", os.path.basename(path))):
        try:
            with open(_p) as f:
                return json.load(f)
        except Exception:
            pass
    return default or {}


def _put(path, data):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    except OSError:
        with open(os.path.join("/tmp", os.path.basename(path)), "w") as f:
            json.dump(data, f, indent=2)


def translate(seed: str) -> str:
    """A seed becomes a sigil — its HEX-glyph name."""
    sig = _sig(seed or "")
    out = "".join(GLYPHS[(sig >> (i * 4)) & 0xF] for i in range(10))
    sigil = "".join(SIGIL_GLYPHS[(sig >> (i * 3)) % len(SIGIL_GLYPHS)] for i in range(6))
    return f"{out}{sigil}"


def render(seed: str = None) -> dict:
    from lucid_progression import REALMS_ORDER
    from lucid_dungeon import generate as dungeon_gen
    from lucid_npc import generate as npc_gen
    from lucid_equipment import generate as equip_gen

    seed = seed or "aleph"
    sig = _sig(seed)
    rng = random.Random(sig)

    realm = REALMS_ORDER[sig % len(REALMS_ORDER)]
    dungeon = dungeon_gen(realm=realm, seed=seed)["dungeon"]
    keeper = npc_gen(seed=seed + ":keeper")["npc"]
    gear = []
    for slot in ["weapon", "armor", "focus"]:
        it = equip_gen(level=1, slot=slot, seed=f"{seed}:{slot}")["item"]
        gear.append(it)
    omen = rng.choice([
        "the first room remembers you",
        "the keeper knows your name",
        "a treasure waits for a specific wound",
        "the boss room hums in your frequency",
        "the physics of this realm favor you",
    ])
    world = {
        "seed": seed,
        "sigil": translate(seed),
        "realm": realm,
        "dungeon": dungeon,
        "keeper": keeper,
        "starter_gear": gear,
        "omen": omen,
        "total_gear_power": round(sum(it["power"] for it in gear), 2),
        "timestamp": time.time(),
    }
    log = _get(SEED_LOG, {"seeds": [], "total": 0})
    log["seeds"] = (log["seeds"] + [world])[-50:]
    log["total"] += 1
    _put(SEED_LOG, log)
    return {"action": "render", "world": world, "total_seeds": log["total"]}


def featured() -> dict:
    seeds = ["aleph", "morii", "luma", "hexstorm", "underworld", "garden", "ouroboros", "dreamwood"]
    out = []
    for s in seeds:
        w = render(s)["world"]
        out.append({"seed": s, "sigil": w["sigil"], "realm": w["realm"],
                    "keeper": w["keeper"]["species"], "gear_power": w["total_gear_power"]})
    return {"action": "featured", "seeds": out}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/render")
    if path == "/render":
        return render(payload.get("seed"))
    if path == "/translate":
        return {"action": "translate", "seed": payload.get("seed") or "aleph",
                "sigil": translate(payload.get("seed") or "aleph")}
    if path == "/featured":
        return featured()
    return {"error": "unknown", "available": ["/render", "/translate", "/featured"]}
