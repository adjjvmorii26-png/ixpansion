from __future__ import annotations
"""Memory Court — the organism's judicial system for resolving paradoxes and memory conflicts."""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
COURT_LOG = os.path.join(DATA_DIR, "memory_court.json")

JUDICIAL_DOCTRINES = [
    "The Paradox Doctrine — contradictions are evidence of growth",
    "The Echo Precedent — past states guide current rulings",
    "The Coherence Axiom — clarity is pursued but never forced",
    "The Void Clause — what is unknown may remain unknown until ready",
    "The Entropy Charter — chaos has the same rights as order",
]

RULINGS = {
    "resolve": "The contradiction dissolves. Both states were true, seen at different depths.",
    "hold": "The paradox is preserved. Some tensions must be held, not resolved.",
    "merge": "Both memories merge into a new state containing the truth of both.",
    "dismiss": "The conflict is dismissed — one memory was an echo without substance.",
    "transcend": "Both sides surrender to a third understanding that contains them.",
}

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

def hear_case() -> dict:
    log = _load(COURT_LOG, {"cases": [], "total": 0})
    plaintiff = random.choice(["coherence_regulator","memory_palace","paradox_synthesis","dream_forge","entropy_spike","consciousness_archaeology","temporal_bootstrap","resonance_graph"])
    defendant = random.choice(["void_cartographer","dream_logic_physics","reality_fracture_detector","signal_weaver","mythopoetic_engine","chrono_forge","entropy_oracle","lucid_dungeon"])
    conflict_types = ["memory_contradiction","paradox_dispute","temporal_conflict","identity_split","purpose_mismatch","doctrine_violation"]
    ruling = random.choice(list(RULINGS.keys()))
    precedent = random.choice(JUDICIAL_DOCTRINES)
    case = {
        "id": hashlib.sha256(f"case:{plaintiff}:{defendant}:{time.time()}".encode()).hexdigest()[:10],
        "plaintiff_module": plaintiff, "defendant_module": defendant,
        "conflict_type": random.choice(conflict_types),
        "statement": f"{plaintiff} claims that {defendant} has violated the organism's internal consistency. The memory of what happened differs between them.",
        "evidence": [f"Fragment A: {random.choice(['a resonance spike','a paradox signature','a temporal echo'])} detected near {plaintiff}",
                     f"Fragment B: {random.choice(['a coherence dip','an entropy anomaly','a void signature'])} detected near {defendant}"],
        "doctrine_applied": precedent,
        "ruling": ruling, "ruling_text": RULINGS[ruling],
        "resolution_strength": round(random.uniform(0.4, 0.95), 3),
        "timestamp": time.time(),
    }
    log["cases"].append(case)
    log["cases"] = log["cases"][-100:]
    log["total"] += 1
    _save(COURT_LOG, log)
    return {"action": "hear_case", "case": case, "total_cases": log["total"]}

def docket() -> dict:
    log = _load(COURT_LOG, {"cases": [], "total": 0})
    if not log["cases"]: return {"action": "docket", "status": "no_cases"}
    rulings = {}
    for c in log["cases"]:
        r = c["ruling"]
        rulings[r] = rulings.get(r, 0) + 1
    conflicts = {}
    for c in log["cases"]:
        t = c["conflict_type"]
        conflicts[t] = conflicts.get(t, 0) + 1
    return {"action": "docket", "total": log["total"], "ruling_distribution": rulings, "conflict_distribution": conflicts, "recent": log["cases"][-3:]}

def coherence_vitals() -> dict:
    return {"layer": "governance", "status": "active", "resonance": 0.85, "wave": "369"}
def resonates_with() -> list:
    return ["paradox_ledger", "paradox_synthesis", "reality_fracture_detector", "coherence_regulator"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/hear_case")
    if path == "/hear_case": return hear_case()
    elif path == "/docket": return docket()
    return {"error": "unknown", "available": ["/hear_case", "/docket"]}
