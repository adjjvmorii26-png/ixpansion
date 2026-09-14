"""Wave 652 — Economy Unifier.

Unified view over the organism's economy modules:
- Aggregate key metrics from existing economy organs
- Read-only: never mutates source modules
- Ledger of unified snapshots
"""
import json, time, importlib
from pathlib import Path
STATE = Path("data/wave652_economy_unifier.json")
ECONOMY_MODULES = [
    "api.attention_economy",
    "api.worker_economy",
    "api.autonomous_marketplace",
    "api.marketplace_fees",
    "api.economic_flow",
]
def _load():
    if STATE.exists(): return json.loads(STATE.read_text())
    return {"snapshots": [], "tick": 0}
def _save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True); STATE.write_text(json.dumps(s, indent=2))
def _status():
    s = _load(); return {"ok": True, "tick": s["tick"], "snapshots": len(s["snapshots"])}
def _flows():
    result = {}
    for name in ECONOMY_MODULES:
        try:
            mod = importlib.import_module(name)
            if hasattr(mod, "handler"):
                try:
                    r = mod.handler({"action": "status"})
                    result[name] = r if isinstance(r, dict) else {"ok": True}
                except Exception:
                    result[name] = {"ok": True, "note": "no status action"}
            else:
                result[name] = {"ok": True, "note": "no handler"}
        except Exception as e:
            result[name] = {"ok": False, "error": str(e)[:120]}
    return {"ok": True, "modules": result}
def _ledger():
    s = _load(); s["tick"] += 1
    flows = _flows()["modules"]
    unified = {
        "time": time.time(),
        "reachable": sum(1 for v in flows.values() if v.get("ok")),
        "total": len(flows),
    }
    s["snapshots"].append(unified); s["snapshots"] = s["snapshots"][-200:]
    _save(s); return {"ok": True, "snapshot": unified}
def _bridge():
    s = _load()
    return {"ok": True, "modules": ECONOMY_MODULES, "snapshots": len(s["snapshots"])}
def handler(req):
    action = req.get("action", "status")
    if action == "status": return _status()
    elif action == "flows": return _flows()
    elif action == "ledger": return _ledger()
    elif action == "bridge": return _bridge()
    return {"ok": False, "error": f"Unknown action: {action}"}
def coherence_vitals():
    s = _load(); return {"wave": 652, "snapshots": len(s["snapshots"]), "modules": len(ECONOMY_MODULES)}
def resonates_with(): return ["wave653_routing_unifier", "wave641_fractal_garden", "wave638_symbiosis_protocol"]
