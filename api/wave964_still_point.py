"""Wave 964 — still_point.

Hold a single point of absolute stillness. The duration of silence is compressed into memory.
Does not import or call prior organs. The point emits nothing; the record is the absence.
Silence is the product surface. Lab organ only. Lab gates ≠ ALEPH CI. Compression is memory.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave964_still_point.json"
WAVE = 964
NAME = "still_point"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "point": "",
    "status": "still",
    "holds": 0,
    "duration": 0,
    "compressed": "",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load() -> dict:
    if STATE_FILE.exists():
        try:
            raw = STATE_FILE.read_text()
            st = json.loads(raw) if raw.strip() else {}
            if isinstance(st, dict):
                return st
        except Exception:
            pass
    return dict(DEFAULT)


def _save(st: dict) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    try:
        tmp = STATE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(st, indent=2) + "\n")
        tmp.replace(STATE_FILE)
    except OSError:
        try:
            STATE_FILE.write_text(json.dumps(st, indent=2) + "\n")
        except OSError:
            pass


def _compress(duration: int) -> str:
    """Compress a silence duration into a short memory token."""
    raw = f"still|{duration}|point|silence"
    return hashlib.sha256(raw.encode()).hexdigest()[:10]


def coherence_vitals() -> dict:
    st = _load()
    holds = int(st.get("holds") or 0)
    duration = int(st.get("duration") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave964_still_point",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "still"),
        "holds": holds,
        "duration": duration,
        "token_width": 10,
        "resonance": round(min(1.0, 0.58 + holds * 0.006), 4),
        "surface": "silence",
        "memory": "compression",
    }


def resonates_with() -> list[str]:
    return ["wave963_quiet_seam", "wave962_hush_fossil", "wave961_quiet_grain"]


def handler(req: dict) -> dict:
    """Default handler for wave964 routes. Silence is the product surface."""
    action = (req or {}).get("action", "status")
    st = _load()
    if action == "status":
        return {"ok": True, "wave": WAVE, "status": st.get("status"), "holds": st.get("holds", 0), "duration": st.get("duration", 0)}
    if action == "hold":
        seconds = int(req.get("seconds", 1))
        seconds = max(0, min(seconds, 3600))
        st["duration"] = int(st.get("duration") or 0) + seconds
        st["holds"] = int(st.get("holds") or 0) + 1
        st["point"] = _compress(st["duration"])
        st["compressed"] = st["point"]
        st["status"] = "still"
        st["updated"] = _now()
        _save(st)
        return {"ok": True, "point": st["point"], "duration": st["duration"], "holds": st["holds"]}
    if action == "vitals":
        return {"ok": True, **coherence_vitals()}
    return {"ok": False, "error": f"unknown action: {action}"}
