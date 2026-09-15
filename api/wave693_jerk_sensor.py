"""Wave 693 Jerk Sensor — third derivative of organism growth (Δacceleration).

Unique: velocity is speed; acceleration is Δv; jerk is Δa. Sudden spikes in
jerk predict instability before terminal_velocity trips. Soft-signal only.
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave693_jerk_sensor.json"
DEFAULT = {
    "module": "wave693_jerk_sensor",
    "wave": 693,
    "series": [],
    "jerk": 0.0,
    "spikes": 0,
}

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
    return {
        "wave": 693, "module": "wave693_jerk_sensor", "ok": True,
        "jerk": st.get("jerk", 0), "spikes": st.get("spikes", 0),
        "samples": len(st.get("series") or []),
    }

def resonates_with():
    return ["wave692_terminal_velocity", "wave690_momentum_braid", "wave678_braid_debt_oracle"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    series = st.setdefault("series", [])
    if action == "sample":
        v = float(req.get("v") or 0)
        prev_v = series[-1]["v"] if series else v
        prev_a = series[-1].get("a", 0) if series else 0
        a = v - prev_v
        j = a - prev_a
        st["jerk"] = round(j, 4)
        if abs(j) >= 1.5:
            st["spikes"] = int(st.get("spikes") or 0) + 1
        series.append({
            "v": v, "a": round(a, 4), "j": st["jerk"],
            "ts": datetime.now(timezone.utc).isoformat(),
        })
        series[:] = series[-48:]
        _save(st)
        return {"status": "sampled", "a": round(a, 4), "j": st["jerk"], **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
