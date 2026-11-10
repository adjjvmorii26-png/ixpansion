"""Wave 976 — residual_hush.

Accumulates residual silence after silence_margin (975) measures.
Residue is compressed memory. No audio emission. Silence is the product surface.
Lab organ only. Lab gates ≠ ALEPH CI. Compression is memory.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave976_residual_hush.json"
WAVE = 976
NAME = "residual_hush"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "residue": 0.0,
    "tokens": [],
    "status": "idle",
    "deposits": 0,
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


def _compress(margin: float, token: str = "") -> float:
    raw = f"{margin}:{token or 'hush'}"
    h = hashlib.sha256(raw.encode()).hexdigest()
    # residue is the fractional unused entropy after compression
    return round((int(h[:6], 16) / 0xFFFFFF) * max(0.0, 1.0 - margin), 4)


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave976_residual_hush",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "residue": float(st.get("residue") or 0.0),
        "tokens": len(st.get("tokens") or []),
        "deposits": int(st.get("deposits") or 0),
        "resonance": 0.71,
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave975_silence_margin",
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

    if action == "deposit":
        margin = float(req.get("margin") or 0.0)
        token = str(req.get("token") or "")[:12]
        residue = _compress(margin, token)
        st["residue"] = round(float(st.get("residue") or 0.0) + residue, 4)
        tokens = st.setdefault("tokens", [])
        tokens.append({"token": token, "residue": residue, "ts": _now()})
        tokens[:] = tokens[-32:]
        st["status"] = "deposited"
        st["deposits"] = int(st.get("deposits") or 0) + 1
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "deposited",
            "added": residue,
            "caption": f"residue hush · {residue}",
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        r = st.get("residue") or 0.0
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"compressed residue · {r}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "deposit", "margin": 0.42, "token": "session22"}), indent=2))
