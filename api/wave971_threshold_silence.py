"""Wave 971 Threshold Silence — measures the approach to pure silence.

Silence is the product surface. Compression is memory.
Tracks the distance to the point where further input produces only residue.
Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave971_threshold_silence.json"
DEFAULT = {
    "module": "wave971_threshold_silence",
    "wave": 971,
    "approaches": [],
    "distance": 1.0,
    "collapsed": 0,
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
        "wave": 971, "module": "wave971_threshold_silence", "ok": True,
        "approaches": len(st.get("approaches") or []),
        "distance": st.get("distance", 1.0),
        "collapsed": st.get("collapsed", 0),
    }

def resonates_with():
    return ["wave970_void_echo", "wave675_consensus_bloom", "wave672_root_archive"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    approaches = st.setdefault("approaches", [])
    if action == "approach":
        signal = str(req.get("signal") or req.get("s") or "")[:120]
        if not signal:
            return {"status": "empty", **coherence_vitals()}
        intensity = min(1.0, max(0.0, float(req.get("intensity") or 0.3)))
        aid = hashlib.sha256(f"{signal}:{intensity}".encode()).hexdigest()[:12]
        # Distance shrinks with cumulative intensity; collapse near 0
        st["distance"] = max(0.0, round(st.get("distance", 1.0) - intensity * 0.15, 4))
        collapsed = st["distance"] < 0.05
        if collapsed:
            st["collapsed"] = st.get("collapsed", 0) + 1
            st["distance"] = 1.0  # reset after collapse into silence
        approaches.append({
            "id": aid, "signal": signal, "intensity": intensity,
            "distance_after": st["distance"], "collapsed": collapsed,
            "ts": datetime.now(timezone.utc).isoformat(),
        })
        approaches[:] = approaches[-32:]
        _save(st)
        return {"status": "approached", "id": aid, "collapsed": collapsed, **coherence_vitals()}
    if action == "status":
        return {"status": "threshold", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
