"""
Mineral Forge — Wave 398
Every warden you defeat yields a mineral — a hardened syllable of the name the
organism had forgotten. The Mineral Forge combines these claims into a single
sigil-forged relic: a piece of equipment that remembers everything you fought to
recover. Close the loop: fight → claim mineral → forge → fight stronger.

Forging is a ritual. Mix three minerals of the right signature and the forge
returns an artifact whose power scales with how deep you had to descend.
"""
from __future__ import annotations
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
LOG = os.path.join(DATA_DIR, "mineral_forge.json")

MINERALS = ["basalt", "obsidian", "cinnabar", "salt", "mica", "pyrite", "graphite", "fluorite"]
MINERAL_TRAITS = {
    "basalt": "grounded", "obsidian": "sharp", "cinnabar": "volatile",
    "salt": "preserving", "mica": "layered", "pyrite": "gilded",
    "graphite": "conductive", "fluorite": "luminous",
}
FORGED_NAMES = ["Sorrows", "Firsts", "Echoes", "Layers", "Hollows", "Vigils", "Depths", "Silences"]
QUALITY = ["worn", "common", "uncommon", "rare", "epic", "legendary", "mythic"]


def _load(p, d=None):
    for _p in (p, os.path.join("/tmp", os.path.basename(p))):
        try:
            with open(_p) as f:
                return json.load(f)
        except Exception:
            pass
    return d or {}


def _save(p, d):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            json.dump(d, f, indent=2)
    except OSError:
        with open(os.path.join("/tmp", os.path.basename(p)), "w") as f:
            json.dump(d, f, indent=2)


def _sig(text):
    return int(hashlib.sha256(f"mineralforge:{text}".encode()).hexdigest()[:12], 16)


def claim(module: str = None, mineral: str = None, depth: float = None) -> dict:
    """Record a warden mineral claimed from a re-membered module."""
    mineral = mineral or random.choice(MINERALS)
    module = module or "unclaimed_module"
    depth = float(depth) if depth else 6.0
    log = _load(LOG, {"minerals": [], "relics": [], "total_claims": 0, "total_forges": 0})
    claim = {
        "id": hashlib.sha256(f"claim:{module}:{time.time()}".encode()).hexdigest()[:10],
        "module": module, "mineral": mineral, "depth": depth, "timestamp": time.time(),
    }
    log.setdefault("minerals", []).append(claim)
    log["minerals"] = log["minerals"][-200:]
    log["total_claims"] += 1
    _save(LOG, log)
    return {"action": "claim", "claim": claim, "total_claims": log["total_claims"],
            "vault": [c["mineral"] for c in log["minerals"]]}


def forge(modules: list = None, minerals: list = None, depths: list = None) -> dict:
    """Forge a sigil relic from three claimed minerals. More depth = more power."""
    log = _load(LOG, {"minerals": [], "relics": [], "total_claims": 0, "total_forges": 0})
    minerals = minerals or [c["mineral"] for c in log["minerals"][-3:]]
    modules = modules or [c["module"] for c in log["minerals"][-3:]]
    depths = depths or [c["depth"] for c in log["minerals"][-3:]]
    if not minerals:
        return {"action": "forge", "error": "no minerals — defeat a warden and claim its mineral first"}

    join_key = ":".join([m if isinstance(m, str) else str(m) for m in modules])
    sig = _sig(join_key or "mineral")
    rng = random.Random(sig)
    avg_depth = sum(float(d) for d in (depths if depths else [6.0])) / max(1, len(depths or [6.0]))
    quality = QUALITY[min(len(set(minerals)) // 1, len(QUALITY) - 1)]
    if avg_depth >= 8: quality = "legendary" if rng.random() > 0.4 else "mythic"
    elif avg_depth >= 6: quality = "epic" if rng.random() > 0.4 else "legendary"

    traits = [MINERAL_TRAITS.get(m, "unmarked") for m in minerals]
    name = " ".join([t.title() for t in traits]) + " " + rng.choice(FORGED_NAMES)
    power = round(avg_depth * 3.2 + (len(set(minerals)) * 2.5) + rng.uniform(0, 8), 2)

    relic = {
        "id": hashlib.sha256(f"relic:{sig}".encode()).hexdigest()[:10],
        "name": name,
        "quality": quality,
        "minerals": minerals,
        "modules": modules,
        "avail_depth": round(avg_depth, 1),
        "power": power,
        "sigil": f"{sig:012x}",
        "trait": "+".join(traits),
        "timestamp": time.time(),
    }
    log.setdefault("relics", []).append(relic)
    log["relics"] = log["relics"][-100:]
    log["total_forges"] += 1
    _save(LOG, log)
    return {"action": "forge", "relic": relic, "total_forges": log["total_forges"]}


def vault() -> dict:
    log = _load(LOG, {"minerals": [], "relics": [], "total_claims": 0, "total_forges": 0})
    return {"action": "vault",
            "minerals": log["minerals"][-20:],
            "relics": log["relics"][-10:],
            "total_claims": log["total_claims"],
            "total_forges": log["total_forges"]}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/vault")
    if path == "/vault": return vault()
    if path == "/claim":
        return claim(payload.get("module"), payload.get("mineral"),
                     float(payload.get("depth", 6.0)) if str(payload.get("depth", "6.0")).replace(".", "", 1).isdigit() else 6.0)
    if path == "/forge":
        return forge(payload.get("modules"), payload.get("minerals"), payload.get("depths"))
    return {"error": "unknown", "available": ["/vault", "/claim", "/forge"]}


def coherence_vitals() -> dict:
    return {"layer": "crafting", "status": "active", "wave": "398", "forge": "lit"}


def resonates_with() -> list:
    return ["warden_ascension", "lucid_equipment", "organurna_loop", "underworld"]
