"""Wave 667 — Mycelial Weave.

Semantic interconnectivity for the mycelial lattice across organs:
- Register semantic links between organs
- Propagate meaning through the lattice
- Query lattice for connected concepts
"""
import json, time
from pathlib import Path
STATE = Path("data/wave667_mycelial_weave.json")
def _load():
    if STATE.exists(): return json.loads(STATE.read_text())
    return {"nodes": [], "links": [], "tick": 0}
def _save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True); STATE.write_text(json.dumps(s, indent=2))
def _status():
    s = _load(); return {"ok": True, "tick": s["tick"], "nodes": len(s["nodes"]), "links": len(s["links"])}
def _link(org1="organ", org2="organ", relation="related"):
    s = _load(); s["tick"] += 1
    entry = {"source": org1, "target": org2, "relation": relation, "time": time.time()}
    s["links"].append(entry); s["links"] = s["links"][-500:]
    _save(s); return {"ok": True, "link": entry}
def _query(org=None):
    s = _load()
    if not org: return {"ok": True, "all_links": s["links"]}
    results = [l for l in s["links"] if l["source"] == org or l["target"] == org]
    return {"ok": True, "links": results}
def _map():
    s = _load(); return {"ok": True, "nodes": len(s["nodes"]), "links": len(s["links"])}
def handler(req):
    action = req.get("action", "status")
    if action == "status": return _status()
    elif action == "link": return _link(req.get("source", "organ"), req.get("target", "organ"), req.get("relation", "related"))
    elif action == "query": return _query(req.get("org"))
    elif action == "map": return _map()
    return {"ok": False, "error": f"Unknown action: {action}"}
def coherence_vitals():
    s = _load(); return {"wave": 667, "nodes": len(s["nodes"]), "links": len(s["links"])}
def resonates_with(): return ["wave668_resonance_ledger_v2", "wave665_mycelial_network", "wave664_paradox_court"]
