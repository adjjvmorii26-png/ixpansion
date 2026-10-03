"""Wave 952 — rest_glyph.

Compress the interval between hush margins into a single silent glyph.
Does not replay session organs or witness tokens. No payload.
Silence is the product surface. Lab gates ≠ ALEPH CI. Compression is memory.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave952_rest_glyph.json"
WAVE = 952
NAME = "rest_glyph"
GLYPHS = (".", "·", "—", " ", "◦")

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "rests": 0,
    "glyph": "",
    "interval": 0,
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


def _glyph(interval: int) -> str:
    """One silent mark for the unused span. Empty interval stays empty."""
    if interval <= 0:
        return ""
    return GLYPHS[(interval - 1) % len(GLYPHS)]


def coherence_vitals() -> dict:
    st = _load()
    rests = int(st.get("rests") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave952_rest_glyph",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "rests": rests,
        "interval": int(st.get("interval") or 0),
        "glyph": st.get("glyph") or "",
        "resonance": round(min(1.0, 0.52 + rests * 0.01), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave950_hush_margin",
        "wave949_council_witness",
        "wave671_harmony_braid",
        "wave675_consensus_bloom",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "rest":
        try:
            interval = int(req.get("interval") if req.get("interval") is not None else 1)
        except (TypeError, ValueError):
            interval = 1
        interval = max(0, interval)
        glyph = _glyph(interval)
        st["rests"] = int(st.get("rests") or 0) + 1
        st["interval"] = interval
        st["glyph"] = glyph
        st["status"] = "rested"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "rested",
            "interval": interval,
            "glyph": glyph,
            "caption": "rest glyph" if glyph else "empty rest",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        g = st.get("glyph") or ""
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": "silent rest" if g else "no rest yet",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "rest", "interval": 3}), indent=2))
