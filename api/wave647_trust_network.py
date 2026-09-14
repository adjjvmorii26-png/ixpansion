"""Wave 647 — Trust Network.

Reputation, reliability, and social capital:
- Trust scores between entities
- Betrayal detection
- Trust propagation (transitive trust)
- Trust decay over time
"""
import json, time
from pathlib import Path
STATE = Path("data/wave647_trust_network.json")
def _load():
    if STATE.exists(): return json.loads(STATE.read_text())
    return {"trust_edges": [], "betrayals": [], "tick": 0}
def _save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True); STATE.write_text(json.dumps(s, indent=2))
def _establish(a, b, score=0.7):
    s = _load(); edge = {"from": a, "to": b, "score": score, "established": time.time(), "interactions": 1}
    s["trust_edges"].append(edge); s["trust_edges"] = s["trust_edges"][-500:]; _save(s)
    return {"ok": True, "edge": edge}
def _interact(a, b, positive=True):
    s = _load()
    for e in s["trust_edges"]:
        if e["from"] == a and e["to"] == b:
            delta = 0.05 if positive else -0.15
            e["score"] = max(0.0, min(1.0, e["score"] + delta))
            e["interactions"] += 1
            if not positive and e["score"] < 0.3: s["betrayals"].append({"from": a, "to": b, "time": time.time(), "score": e["score"]})
            _save(s); return {"ok": True, "edge": e}
    return _establish(a, b, 0.8 if positive else 0.2)
def _trust_graph():
    s = _load(); nodes = set(); edges = []
    for e in s["trust_edges"]:
        nodes.add(e["from"]); nodes.add(e["to"]); edges.append({"from": e["from"], "to": e["to"], "score": e["score"]})
    return {"ok": True, "nodes": len(nodes), "edges": len(edges), "betrayals": len(s["betrayals"])}
def _status():
    s = _load(); return {"ok": True, "tick": s["tick"], "edges": len(s["trust_edges"]), "betrayals": len(s["betrayals"])}
def handler(req):
    action = req.get("action", "status")
    if action == "status": return _status()
    elif action == "establish": return _establish(req.get("a", "?"), req.get("b", "?"), req.get("score", 0.7))
    elif action == "interact": return _interact(req.get("a", "?"), req.get("b", "?"), req.get("positive", True))
    elif action == "graph": return _trust_graph()
    return {"ok": False, "error": f"Unknown action: {action}"}
def coherence_vitals():
    s = _load(); return {"wave": 647, "edges": len(s["trust_edges"]), "betrayals": len(s["betrayals"])}
def resonates_with(): return ["wave646_negotiation", "wave638_symbiosis_protocol", "wave622_resilience_mesh"]
