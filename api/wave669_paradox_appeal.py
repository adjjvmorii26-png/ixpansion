"""Wave 669 — Paradox Appeal.

Review layer for the paradox court:
- File appeals against adjudicated cases
- Review appeals and issue rulings
- Track reversal / sustain outcomes as new precedent
"""
import json, time
from pathlib import Path
STATE = Path("data/wave669_paradox_appeal.json")
def _load():
    if STATE.exists(): return json.loads(STATE.read_text())
    return {"cases": [], "appeals": [], "rulings": [], "tick": 0}
def _save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True); STATE.write_text(json.dumps(s, indent=2))
def _status():
    s = _load(); return {"ok": True, "tick": s["tick"], "cases": len(s["cases"]), "appeals": len(s["appeals"]), "rulings": len(s["rulings"])}
def _file(name="unnamed_paradox", verdict="resolve"):
    s = _load(); s["tick"] += 1
    case = {"name": name, "verdict": verdict, "status": "adjudicated", "time": time.time()}
    s["cases"].append(case); s["cases"] = s["cases"][-200:]
    _save(s); return {"ok": True, "case": case}
def _appeal(case_id=0, grounds="new_evidence"):
    s = _load()
    if case_id >= len(s["cases"]): return {"ok": False, "error": "no such case"}
    appeal = {"case_id": case_id, "case_name": s["cases"][case_id]["name"], "grounds": grounds, "status": "pending", "time": time.time()}
    s["appeals"].append(appeal); s["appeals"] = s["appeals"][-200:]
    _save(s); return {"ok": True, "appeal": appeal}
def _review(appeal_id=0, ruling="sustain"):
    s = _load()
    if appeal_id >= len(s["appeals"]): return {"ok": False, "error": "no such appeal"}
    ap = s["appeals"][appeal_id]
    if ap["status"] != "pending": return {"ok": False, "error": "appeal already ruled"}
    ap["status"] = "ruled"; ap["ruling"] = ruling; ap["ruled_at"] = time.time()
    s["rulings"].append({"case_id": ap["case_id"], "grounds": ap["grounds"], "ruling": ruling, "time": time.time()})
    s["rulings"] = s["rulings"][-200:]
    _save(s); return {"ok": True, "appeal": ap}
def _docket():
    s = _load()
    pending = [a for a in s["appeals"] if a["status"] == "pending"]
    return {"ok": True, "pending": len(pending), "appeals": s["appeals"][-20:]}
def _rulings():
    s = _load(); return {"ok": True, "rulings": s["rulings"][-20:]}
def handler(req):
    action = req.get("action", "status")
    if action == "status": return _status()
    elif action == "file": return _file(req.get("name", "unnamed_paradox"), req.get("verdict", "resolve"))
    elif action == "appeal": return _appeal(req.get("case_id", 0), req.get("grounds", "new_evidence"))
    elif action == "review": return _review(req.get("appeal_id", 0), req.get("ruling", "sustain"))
    elif action == "docket": return _docket()
    elif action == "rulings": return _rulings()
    return {"ok": False, "error": f"Unknown action: {action}"}
def coherence_vitals():
    s = _load(); return {"wave": 669, "appeals": len(s["appeals"]), "rulings": len(s["rulings"])}
def resonates_with(): return ["wave664_paradox_court", "wave668_resonance_ledger_v2", "wave670_sentient_heuristic"]
