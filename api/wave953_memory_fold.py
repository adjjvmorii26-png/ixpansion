"""Wave 953 — memory_fold.

Folds recent pulses into compressed hush tokens.
Compression is memory. Silence is the product surface.
Lab organ only. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave953_memory_fold.json"
WAVE = 953
NAME = "memory_fold"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "folds": 0,
    "tokens": [],
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


def _fold(pulses: list) -> str:
    """Compress pulse texts into a hush token."""
    blob = "|".join(str(p)[:64] for p in (pulses or [])[-8:])
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def coherence_vitals() -> dict:
    st = _load()
    folds = int(st.get("folds") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave953_memory_fold",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "folds": folds,
        "tokens": len(st.get("tokens") or []),
        "resonance": round(min(1.0, 0.62 + folds * 0.008), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave952_silence_seed",
        "wave951_hush_compressor",
        "wave950_hush_margin",
        "wave681_hush_membrane",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "fold":
        pulses = req.get("pulses") or ["silence", "compression", "memory"]
        token = _fold(pulses)
        st["folds"] = int(st.get("folds") or 0) + 1
        tokens = st.setdefault("tokens", [])
        tokens.append({"token": token, "count": len(pulses), "ts": _now()})
        tokens[:] = tokens[-32:]
        st["status"] = "folded"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "folded",
            "token": token,
            "caption": f"hush token · {token[:8]}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        tokens = st.get("tokens") or []
        last = tokens[-1]["token"] if tokens else "void"
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"memory fold · {last[:8]}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "fold"}), indent=2))
