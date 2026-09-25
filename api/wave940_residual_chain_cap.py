"""Wave 940 — residual_chain_cap.

Cap the residual_bind chain: read last slot/hash, emit caption only.
Does not re-bind. Silence is the product surface. Lab organ only.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave940_residual_chain_cap.json"
WAVE = 940
NAME = "residual_chain_cap"

DEFAULT = {"wave": WAVE, "name": NAME, "caps": 0, "status": "idle"}


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


def _import_api(mod: str):
    api = ROOT / "api"
    if str(api) not in sys.path:
        sys.path.insert(0, str(api))
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    return __import__(mod)


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave940_residual_chain_cap",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "caps": int(st.get("caps") or 0),
        "resonance": round(min(1.0, 0.5 + int(st.get("caps") or 0) * 0.02), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave939_residual_bind",
        "wave938_pulse_compress",
        "wave935_verification_null_bridge",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "cap":
        slot, src = "", ""
        try:
            bind = _import_api("wave939_residual_bind")
            b = bind.handler({"action": "status"})
            slot = str(b.get("slot") or "")[:32]
            src = str(b.get("source_hash") or b.get("hash") or "")[:64]
        except Exception:
            pass
        st["caps"] = int(st.get("caps") or 0) + 1
        st["status"] = "capped"
        st["last_slot"] = slot
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "capped",
            "slot": slot,
            "source_hash": src,
            "caption": f"residual chain capped · {slot or 'empty'}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("caps") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"residual chain caps {n}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "cap"}), indent=2))
