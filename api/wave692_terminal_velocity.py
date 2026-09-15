"""Wave 692 Terminal Velocity — soft ceiling when growth speed turns unstable.

Experimental: tracks wave-ship rate; when velocity exceeds a soft terminal
threshold, emits a hush advisory (not a hard fail) so the organism can coast
instead of thrash. Pairs with momentum_braid torque.
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave692_terminal_velocity.json"
DEFAULT = {
    "module": "wave692_terminal_velocity",
    "wave": 692,
    "v": 0.0,
    "terminal": 5.0,
    "coasting": False,
    "advisories": [],
    "history": [],
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
        "wave": 692, "module": "wave692_terminal_velocity", "ok": True,
        "v": st.get("v", 0), "terminal": st.get("terminal", 5.0),
        "coasting": st.get("coasting", False),
    }

def resonates_with():
    return ["wave690_momentum_braid", "wave681_hush_membrane", "wave674_dawn_ledger"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    hist = st.setdefault("history", [])
    advisories = st.setdefault("advisories", [])
    if action == "observe":
        v = float(req.get("v") or req.get("velocity") or 0)
        st["v"] = v
        hist.append({"v": v, "ts": datetime.now(timezone.utc).isoformat()})
        hist[:] = hist[-48:]
        terminal = float(st.get("terminal") or 5.0)
        if v >= terminal:
            st["coasting"] = True
            advisories.append({
                "level": "hush", "msg": "terminal velocity — prefer coast over thrash",
                "v": v, "terminal": terminal,
                "ts": datetime.now(timezone.utc).isoformat(),
            })
            advisories[:] = advisories[-16:]
        else:
            st["coasting"] = False
        _save(st)
        return {"status": "observed", "coasting": st["coasting"], **coherence_vitals()}
    if action == "set_terminal":
        st["terminal"] = float(req.get("terminal") or 5.0)
        _save(st)
        return {"status": "set", **coherence_vitals()}
    if action == "advisories":
        return {"status": "advisories", "items": advisories[-5:], **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
