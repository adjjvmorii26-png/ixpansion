"""Wave 938 — pulse_compress.

Fold a dual-track daily pulse into one silent memory hash.
The product surface stays silent; the hash is the memory.
Does not talk to ALEPH CI. Lab gates remain the organism gates.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave938_pulse_compress.json"
WAVE = 938
NAME = "pulse_compress"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "folds": 0,
    "last_hash": "",
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
    folds = int(st.get("folds") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave938_pulse_compress",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "folds": folds,
        "last_hash": st.get("last_hash") or "",
        "resonance": round(min(1.0, 0.52 + folds * 0.03), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave821_still_interval",
        "wave822_gate_priority",
        "wave937_experiment_track_hygiene",
        "wave671_harmony_braid",
        "wave674_dawn_ledger",
    ]


def _digest(payload: dict) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "fold":
        pulse = {
            "frontier": int(req.get("frontier") or WAVE),
            "lab_ok": bool(req.get("lab_ok", True)),
            "aleph_blocked": bool(req.get("aleph_blocked", False)),
            "council": str(req.get("council") or "session_22")[:32],
            "note": str(req.get("note") or "dual-track pulse")[:96],
        }
        digest = _digest(pulse)
        st["folds"] = int(st.get("folds") or 0) + 1
        st["last_hash"] = digest
        st["last_pulse"] = pulse
        st["status"] = "folded"
        st["ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "folded",
            "compressed": {"hash": digest, "token": "hold"},
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("folds") or 0)
        h = st.get("last_hash") or "silent"
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"pulse compress folds {n} hash {h}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "fold", "frontier": 938}), indent=2))
