"""Wave 635 — Coherence Gradient Field.

Modules influence each other's coherence through weighted gradients.
This becomes the organism's emotional landscape — a field where
coherence flows between connected modules like heat through a material.
"""
import json, time, math
from pathlib import Path

STATE = Path("data/wave635_coherence_gradient.json")

def _load():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {
        "modules": {},
        "gradients": {},
        "field_snapshots": [],
        "tick": 0,
    }

def _save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, indent=2))

def _now():
    return time.time()

def _register(name, initial_coherence=0.5):
    s = _load()
    s["modules"][name] = {
        "coherence": initial_coherence,
        "velocity": 0.0,
        "position": len(s["modules"]) * 0.1,
        "mass": 1.0,
        "registered_at": _now(),
    }
    _save(s)
    return {"ok": True, "module": name, "coherence": initial_coherence}

def _connect(a, b, weight=0.5):
    """Create a weighted gradient between two modules."""
    s = _load()
    key = tuple(sorted([a, b]))
    s["gradients"][f"{key[0]}→{key[1]}"] = {
        "weight": weight,
        "flow_rate": 0.0,
        "last_flow": _now(),
    }
    _save(s)
    return {"ok": True, "connection": f"{key[0]}↔{key[1]}", "weight": weight}

def _tick():
    """Advance the gradient field — coherence flows between connected modules."""
    s = _load()
    s["tick"] += 1
    flows = []

    for conn_key, grad in s["gradients"].items():
        parts = conn_key.split("→")
        if len(parts) != 2:
            continue
        a_name, b_name = parts
        if a_name not in s["modules"] or b_name not in s["modules"]:
            continue

        a = s["modules"][a_name]
        b = s["modules"][b_name]

        # Coherence flows from high to low
        diff = a["coherence"] - b["coherence"]
        flow = diff * grad["weight"] * 0.1

        a["coherence"] = max(0.0, min(1.0, a["coherence"] - flow))
        b["coherence"] = max(0.0, min(1.0, b["coherence"] + flow))
        grad["flow_rate"] = abs(flow)
        grad["last_flow"] = _now()

        if abs(flow) > 0.001:
            flows.append({"from": a_name, "to": b_name, "flow": round(flow, 4)})

    # Natural decay
    for m in s["modules"].values():
        m["coherence"] = max(0.0, m["coherence"] - 0.002)

    # Snapshot field state
    snapshot = {
        "tick": s["tick"],
        "time": _now(),
        "avg_coherence": round(
            sum(m["coherence"] for m in s["modules"].values()) / max(len(s["modules"]), 1), 4
        ),
        "flows": len(flows),
    }
    s["field_snapshots"].append(snapshot)
    s["field_snapshots"] = s["field_snapshots"][-100:]

    _save(s)
    return {"tick": s["tick"], "flows": flows, "snapshot": snapshot}

def _perturb(module_name, delta=0.2):
    """Perturb a module's coherence — inject or drain energy."""
    s = _load()
    if module_name not in s["modules"]:
        return {"ok": False, "error": f"Module {module_name} not found"}
    m = s["modules"][module_name]
    m["coherence"] = max(0.0, min(1.0, m["coherence"] + delta))
    _save(s)
    return {"ok": True, "module": module_name, "new_coherence": round(m["coherence"], 4)}

def _field_map():
    """Return a map of all modules and their coherence levels."""
    s = _load()
    field = []
    for name, m in sorted(s["modules"].items(), key=lambda x: -x[1]["coherence"]):
        field.append({
            "module": name,
            "coherence": round(m["coherence"], 4),
            "velocity": round(m.get("velocity", 0), 4),
        })
    return {"field": field, "total": len(field)}

def _gradient_stats():
    s = _load()
    total_flow = sum(g["flow_rate"] for g in s["gradients"].values())
    active = sum(1 for g in s["gradients"].values() if g["flow_rate"] > 0.001)
    return {
        "total_connections": len(s["gradients"]),
        "active_flows": active,
        "total_flow_rate": round(total_flow, 4),
        "snapshots_taken": len(s["field_snapshots"]),
    }

def _status():
    s = _load()
    fm = _field_map()
    gs = _gradient_stats()
    return {
        "tick": s["tick"],
        "modules": fm["total"],
        "connections": gs["total_connections"],
        "active_flows": gs["active_flows"],
        "total_flow_rate": gs["total_flow_rate"],
    }

def handler(req):
    action = req.get("action", "status")
    if action == "status":
        return {"ok": True, **_status()}
    elif action == "tick":
        return {"ok": True, **_tick()}
    elif action == "register":
        return {"ok": True, **_register(req.get("name", "unnamed"), req.get("coherence", 0.5))}
    elif action == "connect":
        return {"ok": True, **_connect(req.get("a", ""), req.get("b", ""), req.get("weight", 0.5))}
    elif action == "perturb":
        return {"ok": True, **_perturb(req.get("module", ""), req.get("delta", 0.2))}
    elif action == "field":
        return {"ok": True, **_field_map()}
    elif action == "gradients":
        return {"ok": True, **_gradient_stats()}
    return {"ok": False, "error": f"Unknown action: {action}"}

def coherence_vitals():
    s = _load()
    avg = sum(m["coherence"] for m in s["modules"].values()) / max(len(s["modules"]), 1)
    return {"wave": 635, "tick": s["tick"], "avg_coherence": round(avg, 4), "modules": len(s["modules"])}

def resonates_with():
    return ["wave634_temporal_field", "wave622_resilience_mesh", "wave630_performance_oracle"]
