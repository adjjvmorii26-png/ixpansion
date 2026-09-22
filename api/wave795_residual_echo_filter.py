"""Wave 795 — residual_echo_filter.

Damp afterimage/echo text so residual captions decay toward silence.
Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave795_residual_echo_filter.json"
WAVE = 795
NAME = "residual_echo_filter"
THRESHOLD = 0.12

DEFAULT = {"wave": WAVE, "name": NAME, "filters": 0, "status": "idle"}


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
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave795_residual_echo_filter",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "filters": int(st.get("filters") or 0),
        "threshold": THRESHOLD,
        "resonance": round(min(1.0, 0.5 + int(st.get("filters") or 0) * 0.01), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave772_afterimage_well",
        "wave778_antimeme_caption_guard",
        "wave771_caption_pipeline_bridge",
        "wave786_echotide_caption_pace",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "filter":
        text = str(req.get("text") or "")
        try:
            age = float(req.get("age") if req.get("age") is not None else 1.0)
        except (TypeError, ValueError):
            age = 1.0
        age = max(0.0, min(20.0, age))
        residual = (min(1.0, len(text) / 120.0)) * math.exp(-0.45 * age)
        residual = round(residual, 4)
        keep = residual >= THRESHOLD
        st["filters"] = int(st.get("filters") or 0) + 1
        st["status"] = "kept" if keep else "damped"
        st["last_residual"] = residual
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "kept" if keep else "damped",
            "residual": residual,
            "keep": keep,
            "text_out": text if keep else "",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("filters") or 0)
        r = st.get("last_residual")
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"echo filters {n}" + (f" · residual {r}" if r is not None else ""),
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "filter", "text": "echo", "age": 5}), indent=2))
