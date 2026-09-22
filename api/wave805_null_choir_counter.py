"""Wave 805 — null_choir_counter.

Count consecutive silent/empty outcomes (null choir) — antimemetic ledger.
Experimental: streak of silence as a first-class metric.

Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave805_null_choir_counter.json"
WAVE = 805
NAME = "null_choir_counter"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "streak": 0,
    "max_streak": 0,
    "events": 0,
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
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave805_null_choir_counter",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "streak": int(st.get("streak") or 0),
        "max_streak": int(st.get("max_streak") or 0),
        "events": int(st.get("events") or 0),
        "resonance": round(min(1.0, 0.5 + int(st.get("events") or 0) * 0.01), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave778_antimeme_caption_guard",
        "wave795_residual_echo_filter",
        "wave798_hush_afterglow",
        "wave802_quiet_margin_meter",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "tick":
        silent = req.get("silent")
        if silent is None:
            text = str(req.get("text") or "")
            silent = len(text.strip()) == 0
        silent = bool(silent)
        st["events"] = int(st.get("events") or 0) + 1
        if silent:
            st["streak"] = int(st.get("streak") or 0) + 1
            st["max_streak"] = max(int(st.get("max_streak") or 0), st["streak"])
            st["status"] = "singing_null"
        else:
            st["streak"] = 0
            st["status"] = "broken"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": st["status"],
            "silent": silent,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "reset":
        st["streak"] = 0
        st["status"] = "reset"
        st["last_ts"] = _now()
        _save(st)
        return {**coherence_vitals(), "status": "reset", "audio": False, "surface": "silence"}

    if action == "caption":
        s = int(st.get("streak") or 0)
        m = int(st.get("max_streak") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"null choir streak {s} · max {m}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "tick", "silent": True}), indent=2))
