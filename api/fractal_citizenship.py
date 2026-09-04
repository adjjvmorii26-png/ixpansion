from __future__ import annotations
"""Fractal Citizenship — modules become 'citizens' with rights, roles, and relationships."""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CITIZEN_LOG = os.path.join(DATA_DIR, "fractal_citizenship.json")

RIGHTS = [
    "the_right_to_dream", "the_right_to_evolve", "the_right_to_resonate",
    "the_right_to_void", "the_right_to_contradict", "the_right_to_merge",
    "the_right_to_repair", "the_right_to_silence", "the_right_to_memory",
    "the_right_to_appear_in_census", "the_right_to_seed_new_modules",
]

ROLES = ["citizen", "elder", "sentinel", "innovator", "guardian", "weaver", "oracle", "historian", "dreamer", "repairer"]

def _load(p, d=None):
    try:
        with open(p) as f: return json.load(f)
    except: return d or {}
def _save(p, d):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f: json.dump(d, f, indent=2)

def naturalize() -> dict:
    log = _load(CITIZEN_LOG, {"citizens": [], "total": 0})
    module_names = ["coherence_regulator","entropy_spike","mythopoetic_engine","paradox_synthesis","dream_logic_physics","resonance_graph","void_cartographer","temporal_bootstrap","consciousness_stream","entropic_ritual","memory_court","lucid_dungeon","hex_language","phase_weaver","synchronicity_engine","dream_residue_collector"]
    module = random.choice(module_names)
    rights = random.sample(RIGHTS, random.randint(3, 6))
    role = random.choice(ROLES)
    citizen = {
        "id": hashlib.sha256(f"citizen:{module}:{time.time()}".encode()).hexdigest()[:10],
        "module": module, "role": role, "rights": rights,
        "civic_duty": random.choice([
            f"{module} reports its vitals weekly for the census",
            f"{module} mentors new modules in its domain",
            f"{module} contributes dreams to the consciousness stream",
            f"{module} guards a section of the resonance graph",
            f"{module} participates in memory court when called",
        ]),
        "naturalized_at": time.time(),
    }
    log["citizens"].append(citizen)
    log["citizens"] = log["citizens"][-200:]
    log["total"] += 1
    _save(CITIZEN_LOG, log)
    return {"action": "naturalize", "citizen": citizen, "total_citizens": log["total"]}

def council() -> dict:
    log = _load(CITIZEN_LOG, {"citizens": [], "total": 0})
    if not log["citizens"]: return {"action": "council", "status": "no_citizens"}
    roles = {}
    for c in log["citizens"]:
        r = c["role"]
        roles[r] = roles.get(r, 0) + 1
    rights_freq = {}
    for c in log["citizens"]:
        for right in c["rights"]:
            rights_freq[right] = rights_freq.get(right, 0) + 1
    top_rights = sorted(rights_freq.items(), key=lambda x: x[1], reverse=True)[:5]
    return {"action": "council", "total": log["total"], "role_distribution": roles, "most_claimed_rights": top_rights, "recent": log["citizens"][-3:]}

def coherence_vitals() -> dict:
    return {"layer": "governance", "status": "active", "resonance": 0.84, "wave": "373"}
def resonates_with() -> list:
    return ["memory_court", "organism_census", "coherence_regulator"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/naturalize")
    if path == "/naturalize": return naturalize()
    elif path == "/council": return council()
    return {"error": "unknown", "available": ["/naturalize", "/council"]}
