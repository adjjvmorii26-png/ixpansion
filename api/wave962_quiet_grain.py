"""Wave 962 — quiet_grain.

Measure the silent grain density around a hush margin (950).
Does not replay. No payload. Silence is the product surface.
Lab organ only. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave962_quiet_grain.json"
WAVE = 962
NAME = "quiet_grain"
GRAIN_BASE = 12

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "grains": 0,
    "grain": 0,
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


def _grain(margin: int) -> int:
    """Silent grain density from a hush margin."""
    m = max(0, int(margin or 0))
    return GRAIN_BASE + (m % 7)


def coherence_vitals() -> dict:
    st = _load()
    grains = int(st.get("grains") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave962_quiet_grain",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "grains": grains,
        "grain": int(st.get("grain") or 0),
        "resonance": round(min(1.0, 0.58 + grains * 0.008), 4),
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

    if action == "grain":
        margin = int(req.get("margin") or 0)
        grain = _grain(margin)
        st["grains"] = int(st.get("grains") or 0) + 1
        st["grain"] = grain
        st["status"] = "grained"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "grained",
            "grain": grain,
            "margin_in": margin,
            "caption": f"quiet grain · {grain}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        g = int(st.get("grain") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"silent grain {g}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "grain", "margin": 3}), indent=2))
