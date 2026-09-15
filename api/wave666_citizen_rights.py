"""Wave 666 — Citizen Rights.

Modules become citizens with rights and roles:
- Register modules as citizens with roles
- Grant and revoke rights
- Census of all citizens and their rights
"""
import json, time
from pathlib import Path
STATE = Path("data/wave666_citizen_rights.json")
ROLE_RIGHTS = {"worker": ["sense", "signal", "evolve"], "steward": ["sense", "evolve", "govern", "seal"], "observer": ["sense", "report"], "citizen": ["sense", "signal"]}
def _load():
    if STATE.exists(): return json.loads(STATE.read_text())
    return {"citizens": {}, "grants": [], "tick": 0}
def _save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True); STATE.write_text(json.dumps(s, indent=2))
def _status():
    s = _load(); return {"ok": True, "tick": s["tick"], "citizens": len(s["citizens"]), "grants": len(s["grants"])}
def _register(citizen="module", role="citizen", rights=None):
    s = _load(); s["tick"] += 1
    base = ROLE_RIGHTS.get(role, ROLE_RIGHTS["citizen"])
    rights = list(dict.fromkeys(base + (rights or [])))
    s["citizens"][citizen] = {"role": role, "rights": rights, "registered": time.time(), "active": True}
    _save(s); return {"ok": True, "citizen": s["citizens"][citizen]}
def _grant(citizen="module", right="evolve", by="steward"):
    s = _load(); s["tick"] += 1
    c = s["citizens"].setdefault(citizen, {"role": "citizen", "rights": list(ROLE_RIGHTS["citizen"]), "registered": time.time(), "active": True})
    if right not in c["rights"]: c["rights"].append(right)
    s["grants"].append({"citizen": citizen, "right": right, "by": by, "time": time.time()})
    s["grants"] = s["grants"][-500:]
    _save(s); return {"ok": True, "citizen": citizen, "rights": c["rights"]}
def _revoke(citizen="module", right="evolve", by="steward"):
    s = _load(); s["tick"] += 1
    c = s["citizens"].get(citizen)
    if not c: return {"ok": False, "error": "no such citizen"}
    if right in c["rights"]: c["rights"].remove(right)
    s["grants"].append({"citizen": citizen, "right": f"-{right}", "by": by, "time": time.time()})
    _save(s); return {"ok": True, "citizen": citizen, "rights": c["rights"]}
def _can(citizen="module", right="sense"):
    s = _load(); c = s["citizens"].get(citizen)
    if not c: return {"ok": True, "citizen": citizen, "right": right, "permitted": False, "reason": "not registered"}
    return {"ok": True, "citizen": citizen, "right": right, "permitted": right in c["rights"]}
def _census():
    s = _load(); return {"ok": True, "count": len(s["citizens"]), "citizens": {k: {"role": v["role"], "rights": v["rights"]} for k, v in s["citizens"].items()}}
def handler(req):
    action = req.get("action", "status")
    if action == "status": return _status()
    elif action == "register": return _register(req.get("citizen", "module"), req.get("role", "citizen"), req.get("rights"))
    elif action == "grant": return _grant(req.get("citizen", "module"), req.get("right", "evolve"), req.get("by", "steward"))
    elif action == "revoke": return _revoke(req.get("citizen", "module"), req.get("right", "evolve"), req.get("by", "steward"))
    elif action == "can": return _can(req.get("citizen", "module"), req.get("right", "sense"))
    elif action == "census": return _census()
    return {"ok": False, "error": f"Unknown action: {action}"}
def coherence_vitals():
    s = _load(); return {"wave": 666, "citizens": len(s["citizens"]), "grants": len(s["grants"])}
def resonates_with(): return ["wave665_mycelial_network", "wave664_paradox_court", "wave647_trust_network", "wave648_ambient_sensor"]
