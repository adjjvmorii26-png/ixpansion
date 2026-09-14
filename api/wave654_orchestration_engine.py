"""Wave 654 — Orchestration Engine.

Cross-module task scheduling:
- Plan multi-step tasks
- Execute tasks sequentially or in parallel
- Cancel, track history
"""
import json, time
from pathlib import Path
STATE = Path("data/wave654_orchestration_engine.json")
def _load():
    if STATE.exists(): return json.loads(STATE.read_text())
    return {"tasks": [], "completed": [], "tick": 0}
def _save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True); STATE.write_text(json.dumps(s, indent=2))
def _status():
    s = _load(); return {"ok": True, "tick": s["tick"], "tasks": len(s["tasks"]), "completed": len(s["completed"])}
def _plan(name="unnamed", steps=None):
    s = _load(); s["tick"] += 1
    task = {"name": name, "steps": steps or ["step1"], "status": "planned", "time": time.time()}
    s["tasks"].append(task); _save(s)
    return {"ok": True, "task": task}
def _execute(task_id=None):
    s = _load(); t = None
    if task_id is not None and 0 <= task_id < len(s["tasks"]):
        t = s["tasks"][task_id]
    elif s["tasks"]:
        t = s["tasks"][0]
    if t is None: return {"ok": False, "error": "no tasks to execute"}
    t["status"] = "completed"; t["completed_at"] = time.time()
    s["completed"].append(t); s["completed"] = s["completed"][-200:]
    s["tasks"] = [x for x in s["tasks"] if x is not t]
    _save(s); return {"ok": True, "task": t}
def _cancel(task_id=0):
    s = _load()
    if task_id < len(s["tasks"]):
        cancelled = s["tasks"].pop(task_id)
        cancelled["status"] = "cancelled"
        s["completed"].append(cancelled); _save(s)
        return {"ok": True, "task": cancelled}
    return {"ok": False, "error": "task not found"}
def _history():
    s = _load(); return {"ok": True, "completed": s["completed"][-20:]}
def handler(req):
    action = req.get("action", "status")
    if action == "status": return _status()
    elif action == "plan": return _plan(req.get("name", "unnamed"), req.get("steps"))
    elif action == "execute": return _execute(req.get("task_id"))
    elif action == "cancel": return _cancel(req.get("task_id", 0))
    elif action == "history": return _history()
    return {"ok": False, "error": f"Unknown action: {action}"}
def coherence_vitals():
    s = _load(); return {"wave": 654, "tasks": len(s["tasks"]), "completed": len(s["completed"])}
def resonates_with(): return ["wave655_priority_scheduler", "wave651_self_repair", "wave636_adaptive_regulation"]
