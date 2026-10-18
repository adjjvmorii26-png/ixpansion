"""Wave 952 — silence_caretaker.

Daily maintenance pulse for the caretaker cadence. Records a silent tick.
No audio, no payload. Silence is the product surface.
Lab organ only. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave952_silence_caretaker.json"
WAVE = 952
NAME = "silence_caretaker"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "pulses": 0,
    "status": "idle",
    "last_pulse": None,
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
    pulses = int(st.get("pulses") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave952_silence_caretaker",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "pulses": pulses,
        "last_pulse": st.get("last_pulse"),
        "resonance": round(min(1.0, 0.6 + pulses * 0.005), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave950_hush_margin",
        "wave949_council_witness",
        "wave822_gate_priority",
        "wave773_ci_sentinel",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "pulse":
        st["pulses"] = int(st.get("pulses") or 0) + 1
        st["status"] = "pulsed"
        st["last_pulse"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "pulsed",
            "caption": f"silent caretaker pulse · {st['pulses']}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        p = int(st.get("pulses") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"caretaker still · {p}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "pulse"}), indent=2))
