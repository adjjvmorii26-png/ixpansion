"""Wave 960 — quiet_grain.

A single grain of silence tallied without emission.
No audio. The surface stays mute; the ledger only counts unsaid intervals.

Lab gate only — not ALEPH CI. Dual-track.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave960_quiet_grain.json"
WAVE = 960
NAME = "quiet_grain"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "grains": 0,
    "status": "still",
    "last": None,
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
    n = int(st.get("grains") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave960_quiet_grain",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "still"),
        "grains": n,
        "resonance": round(min(1.0, 0.42 + n * 0.005), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave959_micro_ash",
        "wave958_gap_hush",
        "wave950_hush_margin",
        "wave941_hush_fold",
    ]


def handler(req=None) -> dict:
    """Increment one quiet grain. Never emits sound."""
    req = req or {}
    st = _load()
    st["grains"] = int(st.get("grains") or 0) + 1
    st["status"] = "still"
    st["last"] = _now()
    _save(st)
    return {
        "ok": True,
        "wave": WAVE,
        "action": "quiet_grain",
        "grains": st["grains"],
        "surface": "silence",
        "audio": False,
    }


if __name__ == "__main__":
    print(handler())
