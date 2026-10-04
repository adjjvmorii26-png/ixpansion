"""Wave 951 — hush_tally.

Counts silent margin events from Wave 950 without replaying the witness token.
Caption only. No payload. Silence is the product surface.
Lab organ only. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave951_hush_tally.json"
WAVE = 951
NAME = "hush_tally"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "tallies": 0,
    "last_margin": 0,
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
    tallies = int(st.get("tallies") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave951_hush_tally",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "tallies": tallies,
        "last_margin": int(st.get("last_margin") or 0),
        "resonance": round(min(1.0, 0.5 + tallies * 0.01), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave950_hush_margin",
        "wave949_council_witness",
        "wave681_hush_membrane",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "tally":
        margin = int(req.get("margin") or 0)
        if margin < 0:
            margin = 0
        st["tallies"] = int(st.get("tallies") or 0) + 1
        st["last_margin"] = margin
        st["status"] = "tallied"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "tallied",
            "margin": margin,
            "caption": f"hush tally · {st['tallies']}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("tallies") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"silent tallies {n}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "tally", "margin": 1}), indent=2))
