"""Wave 656 — Retrocausal Engine.

Trace effects back to causes:
- Link effect→cause pairs
- Trace causal chains
- Resolve disputes, maintain ledger
"""
import json, time
from pathlib import Path
STATE = Path("data/wave656_retrocausal_engine.json")
def _load():
    if STATE.exists(): return json.loads(STATE.read_text())
    return {"links": [], "resolved": [], "tick": 0}
def _save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True); STATE.write_text(json.dumps(s, indent=2))
def _status():
    s = _load(); return {"ok": True, "tick": s["tick"], "links": len(s["links"]), "resolved": len(s["resolved"])}
def _link(effect="unknown_effect", cause="unknown_cause", confidence=0.5):
    s = _load(); s["tick"] += 1
    pair = {"effect": effect, "cause": cause, "confidence": confidence, "time": time.time()}
    s["links"].append(pair); s["links"] = s["links"][-500:]
    _save(s); return {"ok": True, "link": pair}
def _trace(effect=None):
    s = _load()
    chain = [x for x in s["links"] if effect is None or x["effect"] == effect]
    return {"ok": True, "effect": effect, "chain": chain}
def _resolve(effect=None):
    s = _load()
    resolved = []
    remaining = []
    for x in s["links"]:
        if effect and x["effect"] != effect: remaining.append(x); continue
        x["resolved_at"] = time.time(); resolved.append(x)
    s["resolved"].extend(resolved); s["links"] = remaining
    _save(s); return {"ok": True, "resolved": len(resolved), "remaining": len(remaining)}
def _ledger():
    s = _load(); return {"ok": True, "total_links": len(s["links"]), "total_resolved": len(s["resolved"])}
def handler(req):
    action = req.get("action", "status")
    if action == "status": return _status()
    elif action == "link": return _link(req.get("effect", "unknown_effect"), req.get("cause", "unknown_cause"), req.get("confidence", 0.5))
    elif action == "trace": return _trace(req.get("effect"))
    elif action == "resolve": return _resolve(req.get("effect"))
    elif action == "ledger": return _ledger()
    return {"ok": False, "error": f"Unknown action: {action}"}
def coherence_vitals():
    s = _load(); return {"wave": 656, "links": len(s["links"]), "resolved": len(s["resolved"])}
def resonates_with(): return ["wave649_pattern_predictor", "wave657_succession_planner", "wave648_ambient_sensor"]
