"""Wave 664 — Paradox Court.

Judicial organ resolving paradox debt:
- File cases against paradoxes
- Deliberate toward a verdict
- Record precedent
"""
import json, time
from pathlib import Path
STATE = Path("data/wave664_paradox_court.json")
def _load():
    if STATE.exists(): return json.loads(STATE.read_text())
    return {"cases": [], "precedents": [], "tick": 0}
def _save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True); STATE.write_text(json.dumps(s, indent=2))
def _status():
    s = _load(); return {"ok": True, "tick": s["tick"], "cases": len(s["cases"]), "precedents": len(s["precedents"])}
def _file(name="unnamed_paradox", charge="self_reference"):
    s = _load(); s["tick"] += 1
    case = {"name": name, "charge": charge, "status": "filed", "time": time.time()}
    s["cases"].append(case); s["cases"] = s["cases"][-200:]
    _save(s); return {"ok": True, "case": case}
def _deliberate(case_id=0, verdict="resolve"):
    s = _load()
    if case_id >= len(s["cases"]): return {"ok": False, "error": "no such case"}
    case = s["cases"][case_id]
    case["verdict"] = verdict; case["status"] = "adjudicated"; case["adjudicated_at"] = time.time()
    s["precedents"].append({"name": case["name"], "verdict": verdict, "time": time.time()})
    s["precedents"] = s["precedents"][-200:]
    _save(s); return {"ok": True, "case": case}
def _verdict():
    s = _load()
    pending = [c for c in s["cases"] if c["status"] == "filed"]
    return {"ok": True, "pending": len(pending), "adjudicated": len(s["cases"]) - len(pending)}
def _precedents():
    s = _load(); return {"ok": True, "precedents": s["precedents"][-20:]}
def handler(req):
    action = req.get("action", "status")
    if action == "status": return _status()
    elif action == "file": return _file(req.get("name", "unnamed_paradox"), req.get("charge", "self_reference"))
    elif action == "deliberate": return _deliberate(req.get("case_id", 0), req.get("verdict", "resolve"))
    elif action == "verdict": return _verdict()
    elif action == "precedents": return _precedents()
    return {"ok": False, "error": f"Unknown action: {action}"}
def coherence_vitals():
    s = _load(); return {"wave": 664, "cases": len(s["cases"]), "precedents": len(s["precedents"])}
def resonates_with(): return ["wave665_mycelial_network", "wave663_resonance_ledger", "wave656_retrocausal_engine"]
