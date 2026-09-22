"""Wave 798 — hush_afterglow.

Compress leftover pulse residue into a silent afterglow token.
Memory is the compressed glow, not the raw pulse.
Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave798_hush_afterglow.json"
WAVE = 798
NAME = "hush_afterglow"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "glows": 0,
    "status": "idle",
    "last_token": None,
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


def _compress(text: str, age: float, hour: int) -> str:
    raw = f"{text.strip().lower()}|{age:.2f}|{_phase(hour)}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


def coherence_vitals() -> dict:
    st = _load()
    glows = int(st.get("glows") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave798_hush_afterglow",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "glows": glows,
        "resonance": round(min(1.0, 0.52 + glows * 0.01), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave790_still_interval",
        "wave795_residual_echo_filter",
        "wave796_circadian_dawn_pulse",
        "wave797_antimeme_scar_fuse",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {
            **coherence_vitals(),
            "last_token": st.get("last_token"),
            "last_phase": st.get("last_phase"),
            "audio": False,
            "surface": "silence",
        }

    if action == "glow":
        text = str(req.get("text") or "hush")
        try:
            age = float(req.get("age") or 0)
        except (TypeError, ValueError):
            age = 0.0
        try:
            hour = int(req.get("hour") if req.get("hour") is not None else datetime.now(timezone.utc).hour)
        except (TypeError, ValueError):
            hour = 0
        phase = _phase(hour)
        token = _compress(text, age, hour)
        # Older residue damps into quieter glow; dawn holds more afterglow.
        hold = max(0.0, min(1.0, 0.35 + (0.25 if phase == "dawn" else 0.0) - min(age, 24) * 0.02))
        silent = True
        st["glows"] = int(st.get("glows") or 0) + 1
        st["status"] = "glowing"
        st["last_token"] = token
        st["last_phase"] = phase
        st["last_hold"] = round(hold, 4)
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "glowing",
            "token": token,
            "phase": phase,
            "hold": round(hold, 4),
            "payload": None,
            "audio": False,
            "surface": "silence",
            "silent": silent,
        }

    if action == "caption":
        n = int(st.get("glows") or 0)
        token = st.get("last_token") or "—"
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"hush afterglow {n} · {token}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "glow", "text": "council hush", "age": 3, "hour": 6}), indent=2))
