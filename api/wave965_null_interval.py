"""Wave 965 — null_interval.

Record the length of an empty interval (the gap where nothing arrived).
Compress the absence into a short memory token. Do not emit content.
Silence is the product surface. Lab organ only. Lab gates ≠ ALEPH CI. Compression is memory.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave965_null_interval.json"
WAVE = 965
NAME = "null_interval"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "gaps": 0,
    "last_gap": 0,
    "token": "",
    "status": "null",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load() -> dict:
    if STATE_FILE.exists():
        try:
            raw = json.loads(STATE_FILE.read_text())
            if isinstance(raw, dict):
                return raw
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


def _compress(gap: int) -> str:
    """Compress a null gap length into a short memory token."""
    raw = f"null|{gap}|interval|absence"
    return hashlib.sha256(raw.encode()).hexdigest()[:10]


def coherence_vitals() -> dict:
    st = _load()
    gaps = int(st.get("gaps") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave965_null_interval",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "null"),
        "gaps": gaps,
        "last_gap": int(st.get("last_gap") or 0),
        "token_width": 10,
        "resonance": round(min(1.0, 0.56 + gaps * 0.008), 4),
        "surface": "silence",
        "memory": "compression",
    }


def resonates_with() -> list:
    return [
        "wave964_still_point",
        "wave963_quiet_seam",
        "wave950_hush_margin",
        "wave681_hush_membrane",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {
            **coherence_vitals(),
            "audio": False,
            "payload": None,
            "surface": "silence",
        }

    if action == "gap":
        length = int(req.get("length") or req.get("seconds") or 1)
        length = max(0, min(length, 86400))
        token = _compress(length)
        st["gaps"] = int(st.get("gaps") or 0) + 1
        st["last_gap"] = length
        st["token"] = token
        st["status"] = "null"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "gapped",
            "token": token,
            "length": length,
            "caption": f"null interval · {length}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        g = int(st.get("last_gap") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"gap {g} compressed",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "gap", "length": 7}), indent=2))
