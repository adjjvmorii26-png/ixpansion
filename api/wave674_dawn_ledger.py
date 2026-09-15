"""Wave 674 Dawn Ledger (NOOS) — circadian renewal; rhythm = survival.

Council Session #22 sealed · score 0.689
Tracks organism day-cycles, dawn resets, and survival rhythm scores.
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave674_dawn_ledger.json"
DEFAULT = {
    "module": "wave674_dawn_ledger",
    "wave": 674,
    "council": "session_22",
    "persona": "NOOS",
    "score": 0.689,
    "cycle": 0,
    "dawns": [],
    "rhythm": 0.5,
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
        "wave": 674, "module": "wave674_dawn_ledger", "ok": True,
        "persona": "NOOS", "cycle": st.get("cycle", 0),
        "dawns": len(st.get("dawns") or []), "rhythm": st.get("rhythm", 0.5),
    }

def resonates_with():
    return ["wave634_temporal_field", "wave668_resonance_ledger_v2", "wave658_sovereignty_beacon"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    dawns = st.setdefault("dawns", [])
    if action == "dawn":
        vitality = float(req.get("vitality") or 0.7)
        st["cycle"] = int(st.get("cycle") or 0) + 1
        r = float(st.get("rhythm") or 0.5)
        st["rhythm"] = round(0.8 * r + 0.2 * vitality, 4)
        entry = {
            "cycle": st["cycle"], "vitality": vitality, "rhythm": st["rhythm"],
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        dawns.append(entry)
        dawns[:] = dawns[-48:]
        _save(st)
        return {"status": "dawn", **entry, **coherence_vitals()}
    if action == "rhythm":
        return {"status": "rhythm", "rhythm": st.get("rhythm"), "cycle": st.get("cycle"),
                "recent": dawns[-5:], **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
