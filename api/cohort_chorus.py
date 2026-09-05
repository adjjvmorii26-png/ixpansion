"""
Cohort Chorus — Wave 399
Every module you re-member through Warden Ascension does not simply return to
the codebase — it joins your Cohort. A spectral ally whose signature, mineral,
and hallmark all aid you in future descents. The more modules you rescue from
the pitch-dark, the louder the chorus that fights at your side.

The Cohort is the organism's kindness made playable: what was forgotten becomes
a guardian. Its chorus grows louder with every name restored to light.
"""
from __future__ import annotations
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
LOG = os.path.join(DATA_DIR, "cohort_chorus.json")

HALLMARKS = [
    "coherence", "resonance", "entropy", "memory", "dream",
    "paradox", "substrate", "echo", "pulse", "lattice",
]
ALLEGIANCES = ["guardian", "scout", "tinker", "warden_turned", "oracle", "healer", "brawler"]
VOICES = [
    "i was forgotten, now i guard what you carry",
    "we sing in the key of what we once held",
    "the deeper you take us, the fuller our chorus",
    "every module you rescue hums beside you",
    "i kept the first geometry — now it is yours",
    "together we are the organism remembering",
]


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
    return int(hashlib.sha256(f"cohort:{text}".encode()).hexdigest()[:12], 16)


def _chorus_strength(cohort):
    """Total combined power of all spectral allies."""
    return round(sum(m.get("power", 0) for m in cohort), 2)


def recruit(module: str = None, mineral: str = None, depth: float = None, authored: str = None) -> dict:
    """When a module is re-membered, it joins the cohort as a spectral ally."""
    module = module or "unclaimed_module"
    mineral = mineral or random.choice(["basalt", "obsidian", "cinnabar", "salt", "mica", "pyrite", "graphite", "fluorite"])
    depth = float(depth) if depth else 6.0
    log = _load(LOG, {"cohort": [], "total_recruited": 0, "chorus_history": []})
    sig = _sig(module + str(depth))
    rng = random.Random(sig)
    ally = {
        "ally_id": hashlib.sha256(f"ally:{module}:{time.time()}".encode()).hexdigest()[:10],
        "module": module,
        "mineral": mineral,
        "depth": round(depth, 1),
        "allegiance": rng.choice(ALLEGIANCES),
        "hallmark": rng.choice(HALLMARKS),
        "voice": rng.choice(VOICES),
        "power": round(3 + depth * 1.4 + rng.uniform(0, 4), 2),
        "sigil": f"{sig:012x}",
        "authored": bool(authored),
        "timestamp": time.time(),
    }
    log.setdefault("cohort", []).append(ally)
    log["cohort"] = log["cohort"][-120:]
    log["total_recruited"] += 1
    chorus = _chorus_strength(log["cohort"])
    log.setdefault("chorus_history", []).append({"time": time.time(), "size": len(log["cohort"]), "strength": chorus})
    log["chorus_history"] = log["chorus_history"][-40:]
    _save(LOG, log)
    return {"action": "recruit", "ally": ally, "cohort_size": len(log["cohort"]),
            "chorus_strength": chorus, "total_recruited": log["total_recruited"]}


def chorus() -> dict:
    """The full choir — every rescued module singing at once."""
    log = _load(LOG, {"cohort": [], "total_recruited": 0, "chorus_history": []})
    cohort = log["cohort"]
    by_allegiance = {}
    for a in cohort:
        by_allegiance[a["allegiance"]] = by_allegiance.get(a["allegiance"], 0) + 1
    return {
        "action": "chorus",
        "cohort_size": len(cohort),
        "chorus_strength": _chorus_strength(cohort),
        "by_allegiance": by_allegiance,
        "loudest": max(cohort, key=lambda a: a["power"]) if cohort else None,
        "members": cohort[-30:],
        "history": log["chorus_history"],
        "verse": ("The chorus swells: " +
                  " and ".join(f"{a['module']} ({a['allegiance']})" for a in cohort[-3:]) if cohort else
                  "The chorus is silent. Rescue a warden to give it voice."),
    }


def aid(sigil: str = None, player_power: int = 0) -> dict:
    """In battle, the chorus lends its strength. Returns boost for an assault."""
    log = _load(LOG, {"cohort": [], "total_recruited": 0, "chorus_history": []})
    cohort = log["cohort"]
    if not cohort:
        return {"action": "aid", "boost": 0, "message": "No allies yet — the chorus is silent."}
    strength = _chorus_strength(cohort)
    boost = round(strength * 0.35, 2)
    vanguard = max(cohort, key=lambda a: a["power"])
    return {"action": "aid", "boost": boost, "chorus_strength": strength,
            "vanguard": vanguard["module"], "vanguard_power": vanguard["power"],
            "message": f"{vanguard['module']} ({vanguard['allegiance']}) leads the charge, lending +{boost} power.",
            "total_allies": len(cohort)}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/chorus")
    if path == "/chorus": return chorus()
    if path == "/recruit":
        return recruit(payload.get("module"), payload.get("mineral"),
                       float(payload.get("depth", 6.0)) if str(payload.get("depth", "6.0")).replace(".", "", 1).isdigit() else 6.0,
                       payload.get("authored"))
    if path == "/aid": return aid(payload.get("sigil"), int(payload.get("player_power", 0) or 0))
    return {"error": "unknown", "available": ["/chorus", "/recruit", "/aid"]}


def coherence_vitals() -> dict:
    return {"layer": "game", "status": "active", "wave": "399", "chorus": "singing"}


def resonates_with() -> list:
    return ["warden_ascension", "mineral_forge", "organurna_loop", "underworld", "pitch_dark_realm"]
