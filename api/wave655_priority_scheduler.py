"""Wave 655 — Priority Scheduler.

CPU allocation when resources are scarce:
- Priority queue of tasks (lower priority number = higher priority)
- Run-highest, drain, stats
"""
import json, time
from pathlib import Path
STATE = Path("data/wave655_priority_scheduler.json")
def _load():
    if STATE.exists(): return json.loads(STATE.read_text())
    return {"queue": [], "run_log": [], "tick": 0}
def _save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True); STATE.write_text(json.dumps(s, indent=2))
def _status():
    s = _load(); return {"ok": True, "tick": s["tick"], "queued": len(s["queue"]), "run": len(s["run_log"])}
def _queue(name="task", priority=5, resource="cpu"):
    s = _load(); s["tick"] += 1
    entry = {"name": name, "priority": priority, "resource": resource, "queued_at": time.time()}
    s["queue"].append(entry); s["queue"].sort(key=lambda x: x["priority"])
    _save(s); return {"ok": True, "position": s["queue"].index(entry), "task": entry}
def _run():
    s = _load()
    if not s["queue"]: return {"ok": False, "error": "empty queue"}
    task = s["queue"].pop(0)
    task["ran_at"] = time.time(); task["status"] = "executed"
    s["run_log"].append(task); s["run_log"] = s["run_log"][-200:]
    _save(s); return {"ok": True, "task": task}
def _drain():
    s = _load(); drained = []
    while s["queue"]:
        t = s["queue"].pop(0); t["status"] = "drained"; drained.append(t)
    s["run_log"].extend(drained); _save(s)
    return {"ok": True, "drained": len(drained)}
def _stats():
    s = _load(); return {"ok": True, "queue_depth": len(s["queue"]), "run_count": len(s["run_log"]), "avg_priority": round(sum(x["priority"] for x in s["queue"]) / len(s["queue"]), 4) if s["queue"] else 0.0}
def handler(req):
    action = req.get("action", "status")
    if action == "status": return _status()
    elif action == "queue": return _queue(req.get("name", "task"), req.get("priority", 5), req.get("resource", "cpu"))
    elif action == "run": return _run()
    elif action == "drain": return _drain()
    elif action == "stats": return _stats()
    return {"ok": False, "error": f"Unknown action: {action}"}
def coherence_vitals():
    s = _load(); return {"wave": 655, "queued": len(s["queue"]), "run": len(s["run_log"])}
def resonates_with(): return ["wave654_orchestration_engine", "wave650_auto_optimizer", "wave653_routing_unifier"]
