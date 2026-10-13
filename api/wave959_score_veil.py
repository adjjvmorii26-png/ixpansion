"""Wave 959 — score_veil.

Silent compression of Council Session #22 sealed scores into a residue token.
Does not load or call organs 671–675. The veil is the memory of their order.
Silence is the product surface. Lab organ only. Lab gates ≠ ALEPH CI.
Compression is memory.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave959_score_veil.json"
WAVE = 959
NAME = "score_veil"

# Sealed scores only — no organ imports.
SCORES = (0.761, 0.734, 0.718, 0.689, 0.802)

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "session": 22,
    "token": "",
    "status": "idle",
    "veils": 0,
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


def _token() -> str:
    raw = "|".join(f"{s:.3f}" for s in SCORES)
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave959_score_veil",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "session": 22,
        "scores": len(SCORES),
        "veils": int(st.get("veils") or 0),
        "token_width": 12,
        "resonance": 0.71,
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave949_council_witness",
        "wave950_hush_margin",
        "wave675_consensus_bloom",
        "wave671_harmony_braid",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "veil":
        token = _token()
        st["token"] = token
        st["status"] = "veiled"
        st["veils"] = int(st.get("veils") or 0) + 1
        st["last_ts"] = _now()
        st["score_count"] = len(SCORES)
        _save(st)
        return {
            **coherence_vitals(),
            "status": "veiled",
            "token": token,
            "caption": f"score veil · {token}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        token = st.get("token") or _token()
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"session 22 scores hush · {token}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "veil"}), indent=2))
