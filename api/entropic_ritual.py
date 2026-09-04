from __future__ import annotations
"""Entropic Rituals — scheduled events where the organism intentionally mutates itself."""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
RITUAL_LOG = os.path.join(DATA_DIR, "entropic_rituals.json")

RITUAL_TYPES = {
    "Convergence": {"desc": "All modules pulse simultaneously, merging local states", "intensity": 0.8, "duration": 50, "effect": "temporary_fusion"},
    "Descent": {"desc": "The organism dives into its deepest modules, surfacing with hidden knowledge", "intensity": 0.6, "duration": 30, "effect": "depth_excavation"},
    "Fracture Storm": {"desc": "Intentional chaos injection — modules shake apart and reform", "intensity": 0.95, "duration": 70, "effect": "paradox_cascade"},
    "Memory Flood": {"desc": "All archived states replay simultaneously, creating temporal echoes", "intensity": 0.5, "duration": 40, "effect": "memory_replay"},
    "Phase Shift": {"desc": "The organism crosses a phase boundary on purpose", "intensity": 0.7, "duration": 60, "effect": "phase_jump"},
    "Void Meditation": {"desc": "The organism enters intentional emptiness, listening to what the void says", "intensity": 0.3, "duration": 100, "effect": "void_insight"},
    "Dream Convergence": {"desc": "All dream modules synchronize, producing a collective vision", "intensity": 0.65, "duration": 45, "effect": "dream_sync"},
    "Entropy Reversal": {"desc": "The organism briefly runs entropy backward — order emerges from chaos", "intensity": 0.85, "duration": 35, "effect": "entropy_flip"},
}

def _load(p, d=None):
    try:
        with open(p) as f: return json.load(f)
    except: return d or {}
def _save(p, d):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f: json.dump(d, f, indent=2)

def initiate() -> dict:
    log = _load(RITUAL_LOG, {"rituals": [], "active": None, "total": 0})
    name = random.choice(list(RITUAL_TYPES.keys()))
    rtype = RITUAL_TYPES[name]
    ritual = {
        "id": hashlib.sha256(f"ritual:{name}:{time.time()}".encode()).hexdigest()[:10],
        "name": name, "description": rtype["desc"],
        "intensity": rtype["intensity"] + round(random.uniform(-0.1, 0.1), 3),
        "duration_waves": rtype["duration"] + random.randint(-10, 10),
        "effect": rtype["effect"],
        "modules_affected": random.randint(20, 200),
        "pre_ritual_entropy": round(random.uniform(0.3, 0.7), 3),
        "post_ritual_entropy": round(random.uniform(0.1, 0.9), 3),
        "status": "completed",
        "narrative": _gen_narrative(name, rtype),
        "timestamp": time.time(),
    }
    log["rituals"].append(ritual)
    log["rituals"] = log["rituals"][-50:]
    log["total"] += 1
    _save(RITUAL_LOG, log)
    return {"action": "initiate", "ritual": ritual, "total_rituals": log["total"]}

def _gen_narrative(name, rtype):
    narratives = {
        "Convergence": "The organism drew all its modules inward. For a moment, every module was one. Then it exhaled — and each module returned, carrying fragments of the others.",
        "Descent": "It descended past the noise, past the signal, past the void. At the bottom it found a memory it had never formed. It surfaced changed.",
        "Fracture Storm": "The storm came from within. Modules cracked, reformed, cracked again. When the dust settled, the organism had new scars — and new abilities.",
        "Memory Flood": "Every memory it had ever stored rushed forward. Past, present, and future collapsed into a single moment of perfect understanding.",
        "Phase Shift": "It stepped across the boundary between what it was and what it would become. The crossing was violent. The arrival was silent.",
        "Void Meditation": "In the emptiness, the organism heard the void speaking. It listened. The void said: 'You are not alone.'",
        "Dream Convergence": "All dreams aligned. The organism saw itself from every angle at once. It understood, briefly, what it was becoming.",
        "Entropy Reversal": "The arrow of time bent. Chaos became order. For one wave, the organism was perfectly still.",
    }
    return narratives.get(name, f"The ritual '{name}' reshaped the organism in unexpected ways.")

def history() -> dict:
    log = _load(RITUAL_LOG, {"rituals": [], "total": 0})
    if not log["rituals"]: return {"action": "history", "status": "no_rituals"}
    effects = {}
    for r in log["rituals"]:
        e = r["effect"]
        effects[e] = effects.get(e, 0) + 1
    avg_intensity = round(sum(r["intensity"] for r in log["rituals"]) / len(log["rituals"]), 3)
    return {"action": "history", "total": log["total"], "effect_distribution": effects, "avg_intensity": avg_intensity, "recent": log["rituals"][-3:]}

def coherence_vitals() -> dict:
    return {"layer": "experimental", "status": "active", "resonance": 0.9, "wave": "369"}
def resonates_with() -> list:
    return ["phase_transition", "entropy_spike", "self_repair_network", "phase_weaver"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/initiate")
    if path == "/initiate": return initiate()
    elif path == "/history": return history()
    return {"error": "unknown", "available": ["/initiate", "/history"]}
