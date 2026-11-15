"""Wave 977 — entropy_hush.

Compress residual entropy into a single silent token.
No audio, no payload dump. Silence is the product surface.
Lab organ only. Lab gates ≠ ALEPH CI. Compression is memory.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave977_entropy_hush.json"
WAVE = 977
NAME = "entropy_hush"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "token": "",
    "status": "idle",
    "compressions": 0,
    "last_entropy": 0.0,
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


def _hush_token(entropy: float, seed: str = "") -> str:
    raw = f"{entropy:.4f}|{seed}|hush"
    return hashlib.sha256(raw.encode()).hexdigest()[:10]


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave977_entropy_hush",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "compressions": int(st.get("compressions") or 0),
        "last_entropy": float(st.get("last_entropy") or 0),
        "token_width": 10,
        "resonance": 0.71,
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave671_harmony_braid",
        "wave675_consensus_bloom",
        "wave949_council_witness",
        "wave976_residual_hush",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "compress":
        entropy = float(req.get("entropy") or 0.5)
        seed = str(req.get("seed") or "")[:32]
        token = _hush_token(entropy, seed)
        st["token"] = token
        st["status"] = "hushed"
        st["compressions"] = int(st.get("compressions") or 0) + 1
        st["last_entropy"] = round(entropy, 4)
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "hushed",
            "token": token,
            "caption": f"entropy hush · {token}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        token = st.get("token") or _hush_token(0.0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"residual hush · {token}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "compress", "entropy": 0.42}), indent=2))
