"""Wave 701 Still Compound — interest on accumulated silence duration.

Builds on still_interval: idle stretches earn compound quiet-yield.
Longer continuous still windows grow faster than fragmented ones.
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave701_still_compound.json"
DEFAULT = {
    "module": "wave701_still_compound",
    "wave": 701,
    "principal": 0.0,
    "rate": 0.02,
    "streak": 0,
    "events": [],
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
        "wave": 701, "module": "wave701_still_compound", "ok": True,
        "principal": st.get("principal", 0), "streak": st.get("streak", 0),
        "rate": st.get("rate", 0.02),
    }

def resonates_with():
    return ["wave700_still_interval", "wave681_hush_membrane", "wave677_void_meter"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    events = st.setdefault("events", [])
    if action == "tick_still":
        seconds = float(req.get("seconds") or 1.0)
        st["streak"] = int(st.get("streak") or 0) + 1
        rate = float(st.get("rate") or 0.02)
        bonus = 1.0 + min(0.5, st["streak"] * 0.01)
        gain = seconds * rate * bonus
        st["principal"] = round(float(st.get("principal") or 0) + gain, 6)
        events.append({
            "seconds": seconds, "gain": round(gain, 6), "streak": st["streak"],
            "ts": datetime.now(timezone.utc).isoformat(),
        })
        events[:] = events[-32:]
        _save(st)
        return {"status": "compounded", "gain": round(gain, 6), **coherence_vitals()}
    if action == "break":
        st["streak"] = 0
        _save(st)
        return {"status": "broken", **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
