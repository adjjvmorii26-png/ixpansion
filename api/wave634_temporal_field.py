"""Wave 634 — Temporal Field.

Modules schedule their own evolution, decay, and rebirth.
The organism gains temporal self-awareness — knowing when it was born,
how it has aged, and when it should transform.
"""
import json, time
from pathlib import Path

STATE = Path("data/wave634_temporal_field.json")

def _load():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {
        "tick": 0,
        "epoch": "genesis",
        "modules": {},
        "events": [],
        "epoch_history": [],
    }

def _save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, indent=2))

def _now():
    return time.time()

def _register(name, decay_rate=0.01, rebirth_threshold=0.2):
    s = _load()
    s["modules"][name] = {
        "born": _now(),
        "age_waves": 0,
        "coherence": 1.0,
        "decay_rate": decay_rate,
        "rebirth_threshold": rebirth_threshold,
        "status": "active",
        "last_interaction": _now(),
    }
    _save(s)
    return {"ok": True, "module": name}

def _tick():
    s = _load()
    s["tick"] += 1
    now = _now()
    evolved = []
    decayed = []
    reborn = []

    for name, m in list(s["modules"].items()):
        if m["status"] != "active":
            continue

        # Age by one wave
        m["age_waves"] += 1

        # Decay based on time since last interaction
        idle_time = now - m["last_interaction"]
        idle_waves = idle_time / 60  # 1 minute = 1 wave in simulation
        m["coherence"] = max(0.0, m["coherence"] - m["decay_rate"] * idle_waves)

        # Check for rebirth
        if m["coherence"] < m["rebirth_threshold"]:
            m["coherence"] = 0.8
            m["age_waves"] = 0
            m["status"] = "reborn"
            reborn.append(name)
            s["events"].append({"type": "rebirth", "module": name, "tick": s["tick"], "time": now})
        elif m["coherence"] < 0.5:
            decayed.append(name)
            s["events"].append({"type": "decay_warning", "module": name, "tick": s["tick"], "coherence": m["coherence"]})
        else:
            evolved.append(name)

    _save(s)
    return {
        "tick": s["tick"],
        "epoch": s["epoch"],
        "evolved": len(evolved),
        "decayed": len(decayed),
        "reborn": len(reborn),
        "reborn_modules": reborn,
    }

def _interact(module_name):
    s = _load()
    if module_name in s["modules"]:
        m = s["modules"][module_name]
        m["last_interaction"] = _now()
        m["coherence"] = min(1.0, m["coherence"] + 0.1)
        _save(s)
        return {"ok": True, "module": module_name, "coherence": m["coherence"]}
    return {"ok": False, "error": f"Module {module_name} not registered"}

def _transition_epoch(new_epoch):
    s = _load()
    old = s["epoch"]
    s["epoch_history"].append({"from": old, "to": new_epoch, "tick": s["tick"], "time": _now()})
    s["epoch"] = new_epoch
    # Boost all modules on epoch change
    for m in s["modules"].values():
        m["coherence"] = min(1.0, m["coherence"] + 0.15)
    s["events"].append({"type": "epoch_transition", "from": old, "to": new_epoch, "tick": s["tick"]})
    _save(s)
    return {"ok": True, "from": old, "to": new_epoch}

def _status():
    s = _load()
    active = [n for n, m in s["modules"].items() if m["status"] == "active"]
    reborn = [n for n, m in s["modules"].items() if m["status"] == "reborn"]
    avg_coherence = sum(m["coherence"] for m in s["modules"].values()) / max(len(s["modules"]), 1)
    return {
        "tick": s["tick"],
        "epoch": s["epoch"],
        "total_modules": len(s["modules"]),
        "active": len(active),
        "reborn": len(reborn),
        "avg_coherence": round(avg_coherence, 3),
        "recent_events": s["events"][-5:],
    }

def _audit():
    s = _load()
    dying = []
    healthy = []
    for name, m in s["modules"].items():
        if m["coherence"] < 0.3:
            dying.append({"module": name, "coherence": round(m["coherence"], 3), "age": m["age_waves"]})
        else:
            healthy.append(name)
    return {"dying": dying, "healthy_count": len(healthy), "dying_count": len(dying)}

def handler(req):
    action = req.get("action", "status")
    if action == "status":
        return {"ok": True, **_status()}
    elif action == "tick":
        return {"ok": True, **_tick()}
    elif action == "register":
        return {"ok": True, **_register(
            req.get("name", "unnamed"),
            req.get("decay_rate", 0.01),
            req.get("rebirth_threshold", 0.2),
        )}
    elif action == "interact":
        return {"ok": True, **_interact(req.get("module", ""))}
    elif action == "epoch":
        return {"ok": True, **_transition_epoch(req.get("epoch", "unknown"))}
    elif action == "audit":
        return {"ok": True, **_audit()}
    return {"ok": False, "error": f"Unknown action: {action}"}

def coherence_vitals():
    s = _load()
    avg = sum(m["coherence"] for m in s["modules"].values()) / max(len(s["modules"]), 1)
    return {"wave": 634, "tick": s["tick"], "epoch": s["epoch"], "avg_coherence": round(avg, 3)}

def resonates_with():
    return ["wave622_resilience_mesh", "wave630_performance_oracle", "wave626_dream_synthesis"]
