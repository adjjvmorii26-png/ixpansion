"""Wave 776 — hush_ledger.

Compresses silence pulses into ledger tokens. Silence is the product surface;
compression is memory. Lab-gated; does not touch ALEPH CI.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave776_hush_ledger.json"
WAVE = 776
NAME = "hush_ledger"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "pulses": 0,
    "tokens": [],
    "status": "silent",
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
        "module": "wave776_hush_ledger",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "silent"),
        "pulses": int(st.get("pulses") or 0),
        "tokens": len(st.get("tokens") or []),
        "resonance": round(min(1.0, 0.42 + int(st.get("pulses") or 0) * 0.005), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave681_hush_membrane",
        "wave763_silence_capacitor",
        "wave775_constellation_affinity",
        "wave672_root_archive",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {
            **coherence_vitals(),
            "audio": False,
            "surface": "silence",
        }

    if action == "pulse":
        intensity = float(req.get("intensity") or 0.3)
        duration = float(req.get("duration") or 1.0)
        token_raw = f"{intensity}:{duration}:{_now()}"
        token = hashlib.sha256(token_raw.encode()).hexdigest()[:16]
        entry = {
            "token": token,
            "intensity": round(intensity, 3),
            "duration": round(duration, 2),
            "ts": _now(),
        }
        tokens = st.setdefault("tokens", [])
        tokens.append(entry)
        tokens[:] = tokens[-32:]
        st["pulses"] = int(st.get("pulses") or 0) + 1
        st["status"] = "compressed"
        _save(st)
        return {
            **coherence_vitals(),
            "status": "pulsed",
            "token": token,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "ledger":
        return {
            **coherence_vitals(),
            "status": "ledger",
            "recent": (st.get("tokens") or [])[-8:],
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("pulses") or 0)
        t = len(st.get("tokens") or [])
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"hush ledger {n} pulses · {t} tokens compressed",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
