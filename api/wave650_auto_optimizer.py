"""Wave 650 — Auto-Optimizer.

Self-tune weights and parameters:
- Register tunable parameters with target metric
- Propose tuned values based on delta
- Keep best-value history per parameter
"""
import json, time
from pathlib import Path
STATE = Path("data/wave650_auto_optimizer.json")
def _load():
    if STATE.exists(): return json.loads(STATE.read_text())
    return {"tunables": {}, "history": [], "tick": 0}
def _save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True); STATE.write_text(json.dumps(s, indent=2))
def _status():
    s = _load(); return {"ok": True, "tick": s["tick"], "tunables": len(s["tunables"]), "history": len(s["history"])}
def _tune(name="weight", current=0.5, metric=0.0, delta=0.05):
    s = _load(); s["tick"] += 1
    proposed = max(0.0, min(1.0, current + delta))
    t = s["tunables"].setdefault(name, {"best": current, "best_metric": metric, "tunes": 0})
    if metric > t["best_metric"]:
        t["best"] = current; t["best_metric"] = metric
    t["tunes"] += 1
    s["history"].append({"name": name, "current": current, "proposed": proposed, "metric": metric, "time": time.time()})
    s["history"] = s["history"][-500:]
    _save(s); return {"ok": True, "name": name, "proposed": round(proposed, 4), "best": t["best"], "best_metric": t["best_metric"]}
def _recommend(name="weight"):
    s = _load(); t = s["tunables"].get(name)
    if not t: return {"ok": True, "name": name, "recommended": 0.5}
    return {"ok": True, "name": name, "recommended": t["best"], "best_metric": t["best_metric"]}
def _history(name=None):
    s = _load()
    h = [x for x in s["history"] if name is None or x["name"] == name]
    return {"ok": True, "entries": h[-20:]}
def handler(req):
    action = req.get("action", "status")
    if action == "status": return _status()
    elif action == "tune": return _tune(req.get("name", "weight"), req.get("current", 0.5), req.get("metric", 0.0), req.get("delta", 0.05))
    elif action == "recommend": return _recommend(req.get("name", "weight"))
    elif action == "history": return _history(req.get("name"))
    return {"ok": False, "error": f"Unknown action: {action}"}
def coherence_vitals():
    s = _load(); return {"wave": 650, "tunables": len(s["tunables"]), "history": len(s["history"])}
def resonates_with(): return ["wave651_self_repair", "wave637_meta_regulation", "wave636_adaptive_regulation"]
