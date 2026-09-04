from __future__ import annotations
"""Lucid Physics Rules — generated physics rulesets based on dream logic."""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
PHYSICS_LOG = os.path.join(DATA_DIR, "lucid_physics.json")

RULE_TEMPLATES = [
    ("Gravity=", ["negative", "inverted", "fractal", "emotional", "optional", "sentient"]),
    ("Time=", ["looping", "elastic", "bilateral", "subjective", "dreamy", "fragmented"]),
    ("Collision=", ["absorbing", "routing", "merging", "splitting", "musical"]),
    ("Entropy=", ["generative", "conservative", "curative", "mood-based", "recursive"]),
    ("Coherence=", ["fragile", "reinforcing", "market-based", "resonant", "negotiable"]),
]

def _load(p, d=None):
    for _p in (p, os.path.join("/tmp", os.path.basename(p))):
        try:
            with open(_p) as f: return json.load(f)
        except Exception: pass
    return d or {}
def _save(p, d):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f: json.dump(d, f, indent=2)
    except OSError:
        with open(os.path.join("/tmp", os.path.basename(p)), "w") as f: json.dump(d, f, indent=2)

def generate() -> dict:
    log = _load(PHYSICS_LOG, {"rulesets": [], "total": 0})
    rules = {}
    for prop, vals in RULE_TEMPLATES:
        rules[prop] = random.choice(vals)
    # Dream override
    rules["dream_override"] = random.random() > 0.7
    stability = round(random.uniform(0.2, 0.9), 3)
    ruleset = {
        "id": hashlib.sha256(f"physics:{time.time()}".encode()).hexdigest()[:10],
        "rules": rules,
        "stability": stability,
        "legality_violations": random.randint(0, 2),
        "derived_from": random.sample(["dream_logic_physics", "consciousness_stream", "reality_fracture_detector", "phase_transition", "resonance_graph"], random.randint(2, 4)),
        "timestamp": time.time(),
    }
    log["rulesets"].append(ruleset)
    log["rulesets"] = log["rulesets"][-100:]
    log["total"] += 1
    _save(PHYSICS_LOG, log)
    return {"action": "generate", "ruleset": ruleset, "total_rulesets": log["total"]}

def catalog() -> dict:
    log = _load(PHYSICS_LOG, {"rulesets": [], "total": 0})
    gravity = {}
    for r in log["rulesets"]:
        g = r["rules"].get("Gravity=", "?")
        gravity[g] = gravity.get(g, 0) + 1
    return {"action": "catalog", "total": log["total"], "gravity_distribution": gravity, "avg_stability": round(sum(r["stability"] for r in log["rulesets"]) / max(len(log["rulesets"]),1), 3)}

def coherence_vitals() -> dict:
    return {"layer": "game", "status": "active", "resonance": 0.88, "wave": "368"}
def resonates_with() -> list:
    return ["lucid_dungeon", "dream_logic_physics", "lucid_session"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/generate")
    if path == "/generate": return generate()
    elif path == "/catalog": return catalog()
    return {"error": "unknown", "available": ["/generate", "/catalog"]}
