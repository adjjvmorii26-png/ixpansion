"""Wave 939 — residual_bind.

Bind the last pulse-compress hash into a residual slot.
Silence is the product surface. No audio. Lab organ only.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave939_residual_bind.json"
WAVE = 939
NAME = "residual_bind"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "binds": 0,
    "slot": "",
    "source_hash": "",
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
    binds = int(st.get("binds") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave939_residual_bind",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "binds": binds,
        "slot": st.get("slot") or "",
        "source_hash": st.get("source_hash") or "",
        "resonance": round(min(1.0, 0.53 + binds * 0.03), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave938_pulse_compress",
        "wave821_still_interval",
        "wave822_gate_priority",
        "wave937_experiment_track_hygiene",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "bind":
        src = str(req.get("hash") or st.get("source_hash") or "silent")[:16]
        slot = f"R{int(st.get('binds') or 0) + 1:04d}"
        st["binds"] = int(st.get("binds") or 0) + 1
        st["slot"] = slot
        st["source_hash"] = src
        st["status"] = "bound"
        st["ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "bound",
            "residual": {"slot": slot, "hash": src, "token": "hold"},
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("binds") or 0)
        slot = st.get("slot") or "empty"
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"residual bind {n} slot {slot}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "bind", "hash": "deadbeefcafebabe"}), indent=2))
