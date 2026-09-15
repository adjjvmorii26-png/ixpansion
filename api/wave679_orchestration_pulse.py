"""Wave 679 Orchestration Pulse — lightweight heartbeat over Orchestration Engine plans.

Emits pulse events for plan/execute/cancel so Resilience Mesh and Priority
Scheduler share a common cadence.
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave679_orchestration_pulse.json"
DEFAULT = {"module": "wave679_orchestration_pulse", "wave": 679, "pulses": [], "active": 0}

def _load():
    if STATE_FILE.exists():
        try: return json.loads(STATE_FILE.read_text())
        except Exception: pass
    return dict(DEFAULT)

def _save(st):
    DATA.mkdir(parents=True, exist_ok=True)
    try:
        tmp = STATE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(st, indent=2) + "\n")
        tmp.replace(STATE_FILE)
    except OSError:
        try: STATE_FILE.write_text(json.dumps(st, indent=2) + "\n")
        except OSError: pass

def coherence_vitals():
    st = _load()
    return {"wave": 679, "module": "wave679_orchestration_pulse", "ok": True,
            "pulses": len(st.get("pulses") or []), "active": st.get("active", 0)}

def resonates_with():
    return ["wave654_orchestration_engine", "wave655_priority_scheduler", "wave622_resilience_mesh"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    pulses = st.setdefault("pulses", [])
    if action == "plan":
        name = str(req.get("name") or f"plan_{len(pulses)}")[:48]
        pulses.append({"name": name, "phase": "planned",
                       "ts": datetime.now(timezone.utc).isoformat()})
        pulses[:] = pulses[-64:]
        st["active"] = int(st.get("active") or 0) + 1
        _save(st)
        return {"status": "planned", "name": name, **coherence_vitals()}
    if action == "execute":
        name = str(req.get("name") or "")
        for p in pulses:
            if p["name"] == name:
                p["phase"] = "executing"
                p["ts"] = datetime.now(timezone.utc).isoformat()
                break
        _save(st)
        return {"status": "executing", "name": name, **coherence_vitals()}
    if action == "cancel":
        name = str(req.get("name") or "")
        for p in pulses:
            if p["name"] == name and p.get("phase") != "done":
                p["phase"] = "cancelled"
                st["active"] = max(0, int(st.get("active") or 0) - 1)
                break
        _save(st)
        return {"status": "cancelled", "name": name, **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
