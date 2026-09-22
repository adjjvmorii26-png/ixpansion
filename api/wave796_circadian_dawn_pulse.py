"""Wave 796 — circadian_dawn_pulse.

Map UTC hour to dawn/day/dusk/night and emit a silent renewal pulse.
Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave796_circadian_dawn_pulse.json"
WAVE = 796
NAME = "circadian_dawn_pulse"
PHASES = ("dawn", "day", "dusk", "night")

DEFAULT = {"wave": WAVE, "name": NAME, "pulses": 0, "status": "idle"}


def _now() -> datetime:
    return datetime.now(timezone.utc)


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


def _phase(hour: int) -> str:
    if 5 <= hour < 8:
        return "dawn"
    if 8 <= hour < 17:
        return "day"
    if 17 <= hour < 21:
        return "dusk"
    return "night"


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave796_circadian_dawn_pulse",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "pulses": int(st.get("pulses") or 0),
        "last_phase": st.get("last_phase"),
        "resonance": round(min(1.0, 0.5 + int(st.get("pulses") or 0) * 0.01), 4),
        "surface": "silence",
        "phases": list(PHASES),
    }


def resonates_with() -> list:
    return [
        "wave770_copilot_council_pulse",
        "wave791_lattice_rest",
        "wave790_still_interval",
        "wave789_entropy_weather_cell",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "pulse":
        now = _now()
        hour = int(req.get("hour")) if req.get("hour") is not None else now.hour
        hour = max(0, min(23, int(hour)))
        phase = _phase(hour)
        advice = {
            "dawn": "renew backlog; soft solid routes",
            "day": "ship lab units; dual-track",
            "dusk": "compress crystals; caption only",
            "night": "rest nodes; scar budgets tight",
        }[phase]
        st["pulses"] = int(st.get("pulses") or 0) + 1
        st["last_phase"] = phase
        st["status"] = "pulsed"
        st["last_ts"] = now.isoformat()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "pulsed",
            "phase": phase,
            "hour_utc": hour,
            "advice": advice,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("pulses") or 0)
        p = st.get("last_phase") or "-"
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"dawn pulses {n} · {p}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "pulse", "hour": 6}), indent=2))
