"""Wave 653 — Routing Unifier.

Canonical route registry across routing modules:
- Aggregate routing organs into a unified map
- Resolve route names to their backing modules
- Read-only: never mutates source modules
"""
import json, time, importlib
from pathlib import Path
STATE = Path("data/wave653_routing_unifier.json")
ROUTING_MODULES = [
    "api.api_gateway",
    "api.coherence_regulator",
    "api.attention_reservoir",
    "api.live_telemetry",
    "api.health",
]
def _load():
    if STATE.exists(): return json.loads(STATE.read_text())
    return {"maps": [], "tick": 0}
def _save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True); STATE.write_text(json.dumps(s, indent=2))
def _status():
    s = _load(); return {"ok": True, "tick": s["tick"], "maps": len(s["maps"])}
def _map():
    result = {}
    for name in ROUTING_MODULES:
        try:
            mod = importlib.import_module(name)
            if hasattr(mod, "handler"):
                result[name] = {"ok": True, "handler": True}
            else:
                result[name] = {"ok": True, "handler": False}
        except Exception as e:
            result[name] = {"ok": False, "error": str(e)[:120]}
    return {"ok": True, "routes": result}
def _resolve(route=None):
    m = _map()["routes"]; name = route or "api.health"
    return {"ok": True, "route": name, "found": name in m, "entry": m.get(name)}
def _registry():
    s = _load(); s["tick"] += 1
    routes = _map()["routes"]
    reccord = {"time": time.time(), "total": len(routes), "reachable": sum(1 for v in routes.values() if v.get("ok"))}
    s["maps"].append(reccord); s["maps"] = s["maps"][-200:]
    _save(s); return {"ok": True, "registry": reccord}
def handler(req):
    action = req.get("action", "status")
    if action == "status": return _status()
    elif action == "map": return _map()
    elif action == "resolve": return _resolve(req.get("route"))
    elif action == "registry": return _registry()
    return {"ok": False, "error": f"Unknown action: {action}"}
def coherence_vitals():
    s = _load(); return {"wave": 653, "maps": len(s["maps"]), "modules": len(ROUTING_MODULES)}
def resonates_with(): return ["wave652_economy_unifier", "wave654_orchestration_engine", "wave647_trust_network"]
