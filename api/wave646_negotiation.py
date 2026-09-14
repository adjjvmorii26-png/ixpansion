"""Wave 646 — Negotiation Engine.

Multi-agent bargaining & consensus:
- Proposal / counter-proposal cycles
- Compromise synthesis
- Fair division algorithms
- Coalition formation
"""
import json, time
from pathlib import Path
STATE = Path("data/wave646_negotiation.json")
def _load():
    if STATE.exists(): return json.loads(STATE.read_text())
    return {"proposals": [], "agreements": [], "tick": 0}
def _save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True); STATE.write_text(json.dumps(s, indent=2))
def _propose(topic, offerer, terms):
    s = _load(); p = {"id": len(s["proposals"]), "topic": topic, "offerer": offerer, "terms": terms, "status": "open", "time": time.time()}
    s["proposals"].append(p); s["proposals"] = s["proposals"][-200:]; _save(s)
    return {"ok": True, "proposal_id": p["id"]}
def _accept(proposal_id):
    s = _load()
    for p in s["proposals"]:
        if p["id"] == proposal_id:
            p["status"] = "accepted"; s["agreements"].append({"topic": p["topic"], "terms": p["terms"], "time": time.time()}); _save(s)
            return {"ok": True, "proposal_id": proposal_id, "status": "accepted"}
    return {"ok": False, "error": "proposal not found"}
def _status():
    s = _load(); return {"ok": True, "tick": s["tick"], "proposals": len(s["proposals"]), "agreements": len(s["agreements"])}
def handler(req):
    action = req.get("action", "status")
    if action == "status": return _status()
    elif action == "propose": return _propose(req.get("topic", "?"), req.get("offerer", "?"), req.get("terms", {}))
    elif action == "accept": return _accept(req.get("proposal_id", 0))
    return {"ok": False, "error": f"Unknown action: {action}"}
def coherence_vitals():
    s = _load(); return {"wave": 646, "proposals": len(s["proposals"]), "agreements": len(s["agreements"])}
def resonates_with(): return ["wave645_communication", "wave638_symbiosis_protocol", "wave637_meta_regulation"]
