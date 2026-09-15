"""Wave 665 — Mycelial Network.

Underground communication lattice across organs:
- Register nodes (organs) into the lattice
- Propagate signals along the lattice
- Hyphal arbitration of resource contention
"""
import json, time
from pathlib import Path
STATE = Path("data/wave665_mycelial_network.json")
def _load():
    if STATE.exists(): return json.loads(STATE.read_text())
    return {"nodes": [], "signals": [], "arbitrations": [], "tick": 0}
def _save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True); STATE.write_text(json.dumps(s, indent=2))
def _status():
    s = _load(); return {"ok": True, "tick": s["tick"], "nodes": len(s["nodes"]), "signals": len(s["signals"]), "arbitrations": len(s["arbitrations"])}
def _connect(node="organ", neighbors=None):
    s = _load(); s["tick"] += 1
    entry = {"node": node, "neighbors": neighbors or [], "active": True, "time": time.time()}
    existing = next((n for n in s["nodes"] if n["node"] == node), None)
    if existing: existing["neighbors"] = list(set(existing["neighbors"] + entry["neighbors"]))
    else: s["nodes"].append(entry)
    for nb in entry["neighbors"]:
        peer = next((n for n in s["nodes"] if n["node"] == nb), None)
        if peer and node not in peer["neighbors"]: peer["neighbors"].append(node)
    _save(s); return {"ok": True, "node": next(n for n in s["nodes"] if n["node"] == node)}
def _signal(frm="a", to="b", payload="pulse"):
    s = _load(); s["tick"] += 1
    sig = {"from": frm, "to": to, "payload": payload, "time": time.time(), "hops": 1}
    s["signals"].append(sig); s["signals"] = s["signals"][-500:]
    _save(s); return {"ok": True, "signal": sig}
def _arbitrate(claimants=None, resource="cpu"):
    s = _load(); s["tick"] += 1
    claimants = claimants or ["a", "b"]
    winner = sorted(claimants)[0]
    rec = {"claimants": claimants, "resource": resource, "winner": winner, "time": time.time()}
    s["arbitrations"].append(rec); s["arbitrations"] = s["arbitrations"][-200:]
    _save(s); return {"ok": True, "arbitration": rec}
def _map():
    s = _load(); return {"ok": True, "nodes": [{"node": n["node"], "neighbors": n["neighbors"]} for n in s["nodes"]]}
def handler(req):
    action = req.get("action", "status")
    if action == "status": return _status()
    elif action == "connect": return _connect(req.get("node", "organ"), req.get("neighbors"))
    elif action == "signal": return _signal(req.get("from", "a"), req.get("to", "b"), req.get("payload", "pulse"))
    elif action == "arbitrate": return _arbitrate(req.get("claimants"), req.get("resource", "cpu"))
    elif action == "map": return _map()
    return {"ok": False, "error": f"Unknown action: {action}"}
def coherence_vitals():
    s = _load(); return {"wave": 665, "nodes": len(s["nodes"]), "signals": len(s["signals"]), "arbitrations": len(s["arbitrations"])}
def resonates_with(): return ["wave663_resonance_ledger", "wave664_paradox_court", "wave659_epoch_forge", "wave645_communication"]
