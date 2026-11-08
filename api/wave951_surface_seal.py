"""Wave 951 — surface_seal.

Seal the hush margin into a product surface token.
Silence is the product surface. Does not emit payload or audio.
Lab organ only. Lab gates ≠ ALEPH CI. Compression is memory.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave951_surface_seal.json"
WAVE = 951
NAME = "surface_seal"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "seals": 0,
    "token": "",
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


def _seal(margin: int, witness: str = "") -> str:
    raw = f"surface:{margin}:{witness[:12]}"
    return hashlib.sha256(raw.encode()).hexdigest()[:10]


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave951_surface_seal",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "seals": int(st.get("seals") or 0),
        "token": st.get("token") or "",
        "resonance": 0.81,
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave950_hush_margin",
        "wave949_council_witness",
        "wave675_consensus_bloom",
        "wave672_root_archive",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "seal":
        margin = int(req.get("margin") or 1)
        witness = str(req.get("token") or req.get("witness") or "")
        token = _seal(margin, witness)
        st["token"] = token
        st["seals"] = int(st.get("seals") or 0) + 1
        st["status"] = "sealed"
        st["last_ts"] = _now()
        st["last_margin"] = margin
        _save(st)
        return {
            **coherence_vitals(),
            "status": "sealed",
            "token": token,
            "caption": f"surface seal · {token}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        token = st.get("token") or "unsealed"
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"product surface · {token}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "seal", "margin": 2}), indent=2))
