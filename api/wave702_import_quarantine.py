"""Wave 702 Import Quarantine — isolates in-memory organ state between tests/runs.

Addresses cross-import pollution (e.g. coherence_regulator retaining state):
registers module names that must be purged from sys.modules before a clean pulse.
Soft-fail: never crashes the host process.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave702_import_quarantine.json"
DEFAULT = {
    "module": "wave702_import_quarantine",
    "wave": 702,
    "watchlist": [
        "coherence_regulator",
        "wave190", "wave191", "wave192", "wave193",
        "wave194", "wave195", "wave196", "wave197",
    ],
    "purges": 0,
    "last_purged": [],
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
        "wave": 702, "module": "wave702_import_quarantine", "ok": True,
        "watchlist": len(st.get("watchlist") or []),
        "purges": st.get("purges", 0),
    }

def resonates_with():
    return ["wave460_pulse_engine_bridge", "wave680_dual_track_sentinel", "wave693_jerk_sensor"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    watch = st.setdefault("watchlist", list(DEFAULT["watchlist"]))
    if action == "watch":
        name = str(req.get("name") or "")[:64]
        if name and name not in watch:
            watch.append(name)
            _save(st)
        return {"status": "watching", "watchlist": watch, **coherence_vitals()}
    if action == "purge":
        purged = []
        keys = list(sys.modules.keys())
        for k in keys:
            for w in watch:
                if w in k:
                    try:
                        del sys.modules[k]
                        purged.append(k)
                    except KeyError:
                        pass
                    break
        st["purges"] = int(st.get("purges") or 0) + 1
        st["last_purged"] = purged[:32]
        st["last_ts"] = datetime.now(timezone.utc).isoformat()
        _save(st)
        return {"status": "purged", "count": len(purged), "purged": purged[:16], **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
