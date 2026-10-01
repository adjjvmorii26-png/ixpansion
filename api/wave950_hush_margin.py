"""Wave 950 — hush_margin.

Measure the silent border around a council witness token (949).
Does not replay session organs. No payload. Silence is the product surface.
Lab organ only. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave950_hush_margin.json"
WAVE = 950
NAME = "hush_margin"
TOKEN_WIDTH = 12

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "margins": 0,
    "margin": 0,
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


def _margin(token: str) -> int:
    """Silent border: unused width around a 12-char witness token."""
    width = len(token or "")
    return max(0, TOKEN_WIDTH - width) + (1 if width == TOKEN_WIDTH else 0)


def coherence_vitals() -> dict:
    st = _load()
    margins = int(st.get("margins") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave950_hush_margin",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "margins": margins,
        "margin": int(st.get("margin") or 0),
        "resonance": round(min(1.0, 0.55 + margins * 0.01), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave949_council_witness",
        "wave947_echo_fold",
        "wave941_hush_fold",
        "wave681_hush_membrane",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "margin":
        token = str(req.get("token") or "")
        if not token:
            token = "x" * TOKEN_WIDTH
        margin = _margin(token)
        st["margins"] = int(st.get("margins") or 0) + 1
        st["margin"] = margin
        st["token_width"] = len(token)
        st["status"] = "margined"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "margined",
            "margin": margin,
            "token_width": len(token),
            "caption": f"hush margin · {margin}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        m = int(st.get("margin") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"silent border {m}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "margin"}), indent=2))
