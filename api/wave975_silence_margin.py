"""Wave 975 — silence_margin.

Measures residual silence left after council_witness (949) compresses Session #22.
Does not re-braid, re-archive, re-name, re-dawn, or re-bloom. Silence is the product surface.
Lab organ only. Lab gates ≠ ALEPH CI. Compression is memory.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave975_silence_margin.json"
WAVE = 975
NAME = "silence_margin"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "margin": 0.0,
    "status": "idle",
    "measures": 0,
    "last_token": "",
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


def _margin(token: str = "") -> float:
    raw = token or "session22"
    h = hashlib.sha256(raw.encode()).hexdigest()
    # residual fraction of unused hash entropy as silent margin
    return round(int(h[:8], 16) / 0xFFFFFFFF, 4)


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave975_silence_margin",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "margin": float(st.get("margin") or 0.0),
        "measures": int(st.get("measures") or 0),
        "token_width": 12,
        "resonance": 0.68,
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave949_council_witness",
        "wave671_harmony_braid",
        "wave675_consensus_bloom",
        "wave974_gap_compress",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "measure":
        token = str(req.get("token") or st.get("last_token") or "")
        margin = _margin(token)
        st["margin"] = margin
        st["status"] = "measured"
        st["measures"] = int(st.get("measures") or 0) + 1
        st["last_token"] = token[:12]
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "measured",
            "margin": margin,
            "caption": f"silence margin · {margin}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        m = st.get("margin") or _margin()
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"residual hush · {m}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "measure"}), indent=2))
