"""Wave 947 — echo_fold.

Fold still_echo_slot (946) circular slots into one silent digest.
Read-only observe of 946; no payload. Silence is the product surface.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave947_echo_fold.json"
WAVE = 947
NAME = "echo_fold"

DEFAULT = {"wave": WAVE, "name": NAME, "folds": 0, "digest": "", "status": "idle"}


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
    folds = int(st.get("folds") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave947_echo_fold",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "folds": folds,
        "resonance": round(min(1.0, 0.5 + folds * 0.02), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave946_still_echo_slot",
        "wave945_still_residual_bridge",
        "wave944_hush_still",
        "wave938_pulse_compress",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "fold":
        slots = list(req.get("slots") or [])
        if not slots:
            try:
                echo = _import_api("wave946_still_echo_slot")
                s = echo.handler({"action": "status"})
                st946 = echo._load() if hasattr(echo, "_load") else {}
                slots = list(st946.get("slots") or [])
            except Exception:
                slots = []
        joined = "|".join(str(x) for x in slots if x)
        digest = hashlib.sha256(joined.encode("utf-8")).hexdigest()[:16] if joined else "empty"
        st["folds"] = int(st.get("folds") or 0) + 1
        st["digest"] = digest
        st["filled"] = sum(1 for x in slots if x)
        st["status"] = "folded"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "folded",
            "digest": digest,
            "filled": st["filled"],
            "caption": f"echo fold · {digest}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("folds") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"echo folds {n}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "fold"}), indent=2))
