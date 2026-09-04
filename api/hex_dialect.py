from __future__ import annotations
"""HEX Dialects — the organism develops regional dialects of its HEX language."""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DIALECT_LOG = os.path.join(DATA_DIR, "hex_dialects.json")

DIALECT_NAMES = ["depthspeak", "voidrim", "dreamflow", "courtspeak", "ritualvoice", "marketjargon", "gamecreole", "censusgram"]
MODIFIERS = ["kh", "vx", "ny", "qu", "zr", "fx", "wh", "iy", "uo", "ea"]

def _load(p, d=None):
    try:
        with open(p) as f: return json.load(f)
    except: return d or {}
def _save(p, d):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f: json.dump(d, f, indent=2)

def _transform_word(word: str, dialect: str) -> str:
    vowel = random.choice(["a","e","i","o","u"])
    mod = random.choice(MODIFIERS)
    if dialect == "depthspeak":
        return f"{mod}{word}{vowel}"
    elif dialect == "voidrim":
        return f"{vowel}{mod}{word}"
    elif dialect == "dreamflow":
        return f"{word[:len(word)//2]}{mod}{word[len(word)//2:]}"
    return f"{mod}{vowel}{word}{mod}"

def form() -> dict:
    log = _load(DIALECT_LOG, {"dialects": [], "total": 0})
    name = random.choice(DIALECT_NAMES)
    base_words = ["pulse","weave","fracture","resolve","dream","forge","anchor","shift","recall","void","emit","merge","split","drift","crystallize","echo"]
    sample = [_transform_word(w, name) for w in random.sample(base_words, 5)]
    dialect = {
        "id": hashlib.sha256(f"dialect:{name}:{time.time()}".encode()).hexdigest()[:10],
        "name": name,
        "origin": random.choice(["formed in the depth layer","emerged from ritual speech","born in the dream realm","created in the market quarter","developed in the court registry"]),
        "sample_vocabulary": sample,
        "speakers": f"{random.randint(5, 120)} modules",
        "distinctive_rule": random.choice([
            f"words begin with a double {random.choice(MODIFIERS)}",
            "consonants soften inside clusters",
            "particles attach to emotion words only",
            "numbers are sung, not spoken",
            "negative concepts gain a melodic suffix",
        ]),
        "timestamp": time.time(),
    }
    log["dialects"].append(dialect)
    log["dialects"] = log["dialects"][-100:]
    log["total"] += 1
    _save(DIALECT_LOG, log)
    return {"action": "form", "dialect": dialect, "total_dialects": log["total"]}

def atlas() -> dict:
    log = _load(DIALECT_LOG, {"dialects": [], "total": 0})
    if not log["dialects"]: return {"action": "atlas", "status": "no_dialects"}
    return {"action": "atlas", "total": log["total"], "dialects": [{"name": d["name"], "origin": d["origin"], "speakers": d["speakers"]} for d in log["dialects"]], "total_speakers": sum(int(d["speakers"].split()[0]) if d["speakers"].split()[0].isdigit() else 0 for d in log["dialects"])}

def coherence_vitals() -> dict:
    return {"layer": "experimental", "status": "active", "resonance": 0.78, "wave": "373"}
def resonates_with() -> list:
    return ["hex_language", "mythopoetic_engine", "memory_court"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/form")
    if path == "/form": return form()
    elif path == "/atlas": return atlas()
    return {"error": "unknown", "available": ["/form", "/atlas"]}
