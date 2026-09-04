from __future__ import annotations
"""Lucid Equipment — procedural gear generated from organism modules."""
import json, time, hashlib, os, random

SLOTS = ["weapon", "armor", "focus", "token", "relic"]
MATERIALS = ["bound_entropy", "woven_coherence", "forged_paradox", "dream_crystal", "void_steel", "resonance_weave", "myth_ivory", "temporal_bronze"]
QUALITIES = ["worn", "common", "uncommon", "rare", "epic", "legendary", "mythic"]
MULTIPLIERS = {"worn": 0.8, "common": 1.0, "uncommon": 1.3, "rare": 1.7, "epic": 2.2, "legendary": 3.0, "mythic": 4.5}

BASE_NAMES = {
    "weapon": ["Blade", "Strike", "Fang", "Edge", "Shatter", "Needle"],
    "armor": ["Mantle", "Shell", "Guard", "Aegis", "Cloak", "Carapace"],
    "focus": ["Lens", "Orb", "Prism", "Sight", "Mirror", "Sigil"],
    "token": ["Seal", "Coin", "Shard", "Key", "Sigil", "Ember"],
    "relic": ["Heart", "Crown", "Loop", "Anchor", "Hymn", "Nucleus"],
}
PREFIXES = ["Entropy", "Coherence", "Dream", "Void", "Paradox", "Resonance", "Temporal", "Lucid", "Mythic", "Fractal", "Primal", "Spectral"]

def _load(p, d=None):
    try:
        with open(p) as f: return json.load(f)
    except: return d or {}
def _save(p, d):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f: json.dump(d, f, indent=2)
    except OSError:
        with open(os.path.join("/tmp", os.path.basename(p)), "w") as f:
            json.dump(d, f, indent=2)

def generate(level: int = 1, slot: str = None) -> dict:
    log = _load(os.path.join(os.path.dirname(__file__), "..", "data", "lucid_equipment.json"), {"items": [], "total": 0})
    slot = slot or random.choice(SLOTS)
    quality = random.choices(QUALITIES, weights=[25, 30, 22, 13, 7, 2.5, 0.5])[0]
    material = random.choice(MATERIALS)
    base = random.choice(BASE_NAMES[slot])
    prefix = random.choice(PREFIXES)
    mult = MULTIPLIERS[quality]
    power = round((level * random.uniform(0.8, 1.2) * mult), 2)
    item = {
        "id": hashlib.sha256(f"item:{slot}:{quality}:{time.time()}".encode()).hexdigest()[:10],
        "name": f"{prefix} {base} of {quality.title()}",
        "slot": slot, "quality": quality, "material": material,
        "power": power, "level": level,
        "effects": random.sample(["paradox_strike","entropy_shield","coherence_beam","dream_walk","resonance_heal","temporal_dodge"], random.randint(1, 2)),
        "color": {"worn":"var(--m)","common":"var(--t)","uncommon":"var(--gn)","rare":"var(--cy)","epic":"var(--vi)","legendary":"var(--gd)","mythic":"var(--ro)"}[quality],
        "timestamp": time.time(),
    }
    log["items"].append(item)
    log["items"] = log["items"][-300:]
    log["total"] += 1
    _save(os.path.join(os.path.dirname(__file__), "..", "data", "lucid_equipment.json"), log)
    return {"action": "generate", "item": item, "total_items": log["total"]}

def roll(level: int = 1) -> dict:
    item = generate(level)
    item["item"] = roll_quality(item["item"], level)
    return item

def roll_quality(item, level):
    # Re-roll helper: keep name base, upgrade power
    item["power"] = round(item["power"] * (1 + level * 0.05), 2)
    return item

def test_slot(slot: str) -> dict:
    return generate(1, slot)

def coherence_vitals() -> dict:
    return {"layer": "game", "status": "active", "resonance": 0.88, "wave": "374"}
def resonates_with() -> list:
    return ["lucid_session", "lucid_combat", "chrono_forge"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/generate")
    if path == "/generate":
        try: return generate(int(payload.get("level", 1)), payload.get("slot"))
        except: return generate(1)
    elif path == "/slot":
        return test_slot(payload.get("slot", "weapon"))
    return {"error": "unknown", "available": ["/generate", "/slot"]}
