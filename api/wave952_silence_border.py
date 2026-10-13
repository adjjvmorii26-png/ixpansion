"""Wave 952 — silence_border.

Measure the quiet edge after a hush margin (950). No replay of session organs.
Payload stays empty. Silence is the product surface.
Lab organ only. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave952_silence_border.json"
WAVE = 952
NAME = "silence_border"
BORDER = 1

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "borders": 0,
    "border": 0,
    "status": "idle",
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


def coherence_vitals() -> dict:
    st = _load()
    borders = int(st.get("borders") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave952_silence_border",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "borders": borders,
        "border": int(st.get("border") or 0),
        "resonance": round(min(1.0, 0.56 + borders * 0.01), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave950_hush_margin",
        "wave949_council_witness",
        "wave941_hush_fold",
        "wave681_hush_membrane",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "border":
        width = int(req.get("width") or BORDER)
        border = max(0, width)
        st["borders"] = int(st.get("borders") or 0) + 1
        st["border"] = border
        st["status"] = "bordered"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "bordered",
            "border": border,
            "caption": f"silence border · {border}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        b = int(st.get("border") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"quiet edge {b}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "border"}), indent=2))
