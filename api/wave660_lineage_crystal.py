"""Wave 660 — Lineage Crystal.

AEONFORGE's memory — temporal lineage of the organism:
- Record epoch events (birth, merge, deprecation, ratification)
- Trace lineage chains and ancestors
- Snapshot crystal state
"""
import json, time
from pathlib import Path
STATE = Path("data/wave660_lineage_crystal.json")
def _load():
    if STATE.exists(): return json.loads(STATE.read_text())
    return {"events": [], "lineages": {}, "tick": 0}
def _save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True); STATE.write_text(json.dumps(s, indent=2))
def _status():
    s = _load(); return {"ok": True, "tick": s["tick"], "events": len(s["events"]), "lineages": len(s["lineages"])}
def _record(event="birth", entity="organ", epoch=None, note=""):
    s = _load(); s["tick"] += 1
    ev = {"event": event, "entity": entity, "epoch": epoch, "note": note, "time": time.time()}
    s["events"].append(ev); s["events"] = s["events"][-1000:]
    key = f"{entity}:{epoch}" if epoch else entity
    chain = s["lineages"].setdefault(key, [])
    chain.append(ev); s["lineages"][key] = chain[-200:]
    _save(s); return {"ok": True, "event": ev}
def _trace(entity="organ", epoch=None):
    s = _load(); key = f"{entity}:{epoch}" if epoch else entity
    return {"ok": True, "entity": entity, "epoch": epoch, "lineage": s["lineages"].get(key, [])}
def _ancestors(entity="organ", depth=3):
    s = _load(); all_events = s["events"]
    chain = [e for e in all_events if e["entity"] == entity][-depth:]
    return {"ok": True, "entity": entity, "ancestors": chain}
def _snapshot():
    s = _load()
    return {"ok": True, "tick": s["tick"], "events": len(s["events"]), "lineages": {k: len(v) for k, v in s["lineages"].items()}}
def handler(req):
    action = req.get("action", "status")
    if action == "status": return _status()
    elif action == "record": return _record(req.get("event", "birth"), req.get("entity", "organ"), req.get("epoch"), req.get("note", ""))
    elif action == "trace": return _trace(req.get("entity", "organ"), req.get("epoch"))
    elif action == "ancestors": return _ancestors(req.get("entity", "organ"), req.get("depth", 3))
    elif action == "snapshot": return _snapshot()
    return {"ok": False, "error": f"Unknown action: {action}"}
def coherence_vitals():
    s = _load(); return {"wave": 660, "events": len(s["events"]), "lineages": len(s["lineages"])}
def resonates_with(): return ["wave659_epoch_forge", "wave657_succession_planner", "wave656_retrocausal_engine"]
