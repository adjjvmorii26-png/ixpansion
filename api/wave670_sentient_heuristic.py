"""Wave 670 — Sentient Heuristic.

Self-adapting heuristic organ:
- Observe outcomes and record them
- Adapt heuristic weights toward what actually worked
- Read insights: best heuristics, drift, oscillation
"""
import json, time
from pathlib import Path
STATE = Path("data/wave670_sentient_heuristic.json")
def _load():
    if STATE.exists(): return json.loads(STATE.read_text())
    return {"heuristics": {}, "observations": [], "tick": 0}
def _save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True); STATE.write_text(json.dumps(s, indent=2))
def _status():
    s = _load(); return {"ok": True, "tick": s["tick"], "heuristics": len(s["heuristics"]), "observations": len(s["observations"])}
def _observe(heuristic="default", outcome=0.5):
    s = _load(); s["tick"] += 1
    h = s["heuristics"].setdefault(heuristic, {"weight": 0.5, "hits": 0, "misses": 0, "updated": 0})
    h["weight"] = max(0.0, min(1.0, h["weight"] + 0.1 * (outcome - h["weight"])))
    if outcome >= 0.5: h["hits"] += 1
    else: h["misses"] += 1
    h["updated"] = time.time()
    s["observations"].append({"heuristic": heuristic, "outcome": outcome, "time": time.time()})
    s["observations"] = s["observations"][-1000:]
    _save(s); return {"ok": True, "heuristic": heuristic, "weight": round(h["weight"], 4)}
def _adapt(target="default", pressure=0.05):
    """Nudge a heuristic under external pressure (allows tuning without observations)."""
    s = _load(); s["tick"] += 1
    h = s["heuristics"].setdefault(target, {"weight": 0.5, "hits": 0, "misses": 0, "updated": 0})
    h["weight"] = max(0.0, min(1.0, h["weight"] + pressure))
    h["updated"] = time.time()
    _save(s); return {"ok": True, "heuristic": target, "weight": round(h["weight"], 4)}
def _insights():
    s = _load()
    ranked = sorted(s["heuristics"].items(), key=lambda kv: kv[1]["weight"], reverse=True)
    return {"ok": True, "best": ranked[:5], "count": len(ranked)}
def _reset():
    s = _load(); s["heuristics"] = {}; s["observations"] = []; s["tick"] += 1
    _save(s); return {"ok": True, "reset": True}
def handler(req):
    action = req.get("action", "status")
    if action == "status": return _status()
    elif action == "observe": return _observe(req.get("heuristic", "default"), float(req.get("outcome", 0.5)))
    elif action == "adapt": return _adapt(req.get("target", "default"), float(req.get("pressure", 0.05)))
    elif action == "insights": return _insights()
    elif action == "reset": return _reset()
    return {"ok": False, "error": f"Unknown action: {action}"}
def coherence_vitals():
    s = _load(); return {"wave": 670, "heuristics": len(s["heuristics"]), "observations": len(s["observations"])}
def resonates_with(): return ["wave669_paradox_appeal", "wave668_resonance_ledger_v2", "wave667_mycelial_weave"]
