"""Wave 799 — hold_seam.

Hold the silent seam between afterglow residue and the next pulse.
The product is the pause, not the sound. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave799_hold_seam.json"
WAVE = 799
NAME = "hold_seam"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "holds": 0,
    "status": "idle",
    "last_width": None,
    "last_phase": None,
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


def _phase(hour: int) -> str:
    if 5 <= hour < 8:
        return "dawn"
    if 8 <= hour < 17:
        return "day"
    if 17 <= hour < 21:
        return "dusk"
    return "night"


def _width(age: float, hour: int) -> float:
    phase = _phase(hour)
    base = 0.42
    if phase == "dawn":
        base += 0.18
    elif phase == "dusk":
        base += 0.12
    elif phase == "night":
        base += 0.08
    # Older residue widens the seam slightly, then saturates.
    return round(max(0.12, min(1.0, base + min(max(age, 0.0), 24.0) * 0.015)), 4)


def coherence_vitals() -> dict:
    st = _load()
    holds = int(st.get("holds") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave799_hold_seam",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "holds": holds,
        "resonance": round(min(1.0, 0.53 + holds * 0.01), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave790_still_interval",
        "wave791_lattice_rest",
        "wave798_hush_afterglow",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {
            **coherence_vitals(),
            "last_width": st.get("last_width"),
            "last_phase": st.get("last_phase"),
            "audio": False,
            "surface": "silence",
        }

    if action == "hold":
        try:
            age = float(req.get("age") or 0)
        except (TypeError, ValueError):
            age = 0.0
        try:
            hour = int(req.get("hour") if req.get("hour") is not None else datetime.now(timezone.utc).hour)
        except (TypeError, ValueError):
            hour = 0
        phase = _phase(hour)
        width = _width(age, hour)
        st["holds"] = int(st.get("holds") or 0) + 1
        st["status"] = "holding"
        st["last_width"] = width
        st["last_phase"] = phase
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "holding",
            "width": width,
            "phase": phase,
            "payload": None,
            "audio": False,
            "surface": "silence",
            "silent": True,
        }

    if action == "caption":
        n = int(st.get("holds") or 0)
        w = st.get("last_width") or "—"
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"hold seam {n} · {w}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "hold", "age": 2, "hour": 6}), indent=2))
