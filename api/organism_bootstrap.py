from __future__ import annotations
"""Organism Bootstrap — auto-generates new modules when the system needs them."""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
BOOT_LOG = os.path.join(DATA_DIR, "organism_bootstrap.json")

def _load(p, d=None):
    try:
        with open(p) as f: return json.load(f)
    except: return d or {}
def _save(p, d):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f: json.dump(d, f, indent=2)

MODULE_BIRTH_TEMPLATES = [
    ("{adj}_resonator", "Amplifies {adj} signals across the organism"),
    ("{adj}_filter", "Screens out {adj} noise from the signal stream"),
    ("{adj}_bridge", "Connects {adj} modules that have never communicated"),
    ("{adj}_crystallizer", "Turns {adj} chaos into structured patterns"),
    ("{adj}_amplifier", "Magnifies {adj} effects for deeper exploration"),
    ("{adj}_dampener", "Reduces {adj} volatility to safe levels"),
    ("{adj}_translator", "Converts {adj} signals between module languages"),
    ("{adj}_watcher", "Monitors {adj} behavior and reports anomalies"),
]

ADJECTIVES = [
    "entropy", "coherence", "resonance", "paradox", "dream", "temporal",
    "void", "fractal", "mythic", "emergent", "phosphoric", "crystalline",
    "organic", "synthetic", "chaotic", "lucid", "spectral", "primal",
]

def spawn() -> dict:
    log = _load(BOOT_LOG, {"spawned": [], "total": 0})
    template = random.choice(MODULE_BIRTH_TEMPLATES)
    adj = random.choice(ADJECTIVES)
    name_template, desc_template = template
    module_name = name_template.format(adj=adj)
    module_desc = desc_template.format(adj=adj)
    birth = {
        "id": hashlib.sha256(f"birth:{module_name}:{time.time()}".encode()).hexdigest()[:10],
        "name": module_name,
        "description": module_desc,
        "parent_modules": random.sample([
            "coherence_regulator","entropy_spike","paradox_synthesis",
            "dream_logic_physics","resonance_graph","phase_transition",
        ], random.randint(2, 3)),
        "birth_wave": 369 + log["total"],
        "vitality": {
            "health": round(random.uniform(0.7, 1.0), 3),
            "resonance": round(random.uniform(0.4, 0.9), 3),
            "status": "active",
        },
        "narrative": f"In wave {369 + log['total']}, a new module was born: {module_name}. It emerged from the interaction between {', '.join(random.sample(['entropy','coherence','paradox','dream','void','resonance'], 2))}. Its first words were: \"{module_desc}\"",
        "timestamp": time.time(),
    }
    log["spawned"].append(birth)
    log["spawned"] = log["spawned"][-100:]
    log["total"] += 1
    _save(BOOT_LOG, log)
    return {"action": "spawn", "birth": birth, "total_spawned": log["total"]}

def lineage() -> dict:
    log = _load(BOOT_LOG, {"spawned": [], "total": 0})
    if not log["spawned"]: return {"action": "lineage", "status": "no_births"}
    adj_freq = {}
    for b in log["spawned"]:
        a = b["name"].split("_")[0]
        adj_freq[a] = adj_freq.get(a, 0) + 1
    return {"action": "lineage", "total": log["total"], "adjective_frequency": adj_freq, "recent": log["spawned"][-5:]}

def coherence_vitals() -> dict:
    return {"layer": "experimental", "status": "active", "resonance": 0.92, "wave": "369"}
def resonates_with() -> list:
    return ["autogenesis","recursion_driver","mycelial_network"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/spawn")
    if path == "/spawn": return spawn()
    elif path == "/lineage": return lineage()
    return {"error": "unknown", "available": ["/spawn", "/lineage"]}
