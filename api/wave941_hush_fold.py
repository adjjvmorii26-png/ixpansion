"""Wave 941 — hush_fold.

Fold the residual_chain_cap caption into a hush token.
Does not re-cap or re-bind. Silence is the product surface. Lab organ only.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave941_hush_fold.json"
WAVE = 941
NAME = "hush_fold"

DEFAULT = {"wave": WAVE, "name": NAME, "folds": 0, "token": "", "status": "idle"}


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
        "module": "wave941_hush_fold",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "folds": folds,
        "token": st.get("token") or "",
        "resonance": round(min(1.0, 0.51 + folds * 0.02), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave940_residual_chain_cap",
        "wave939_residual_bind",
        "wave938_pulse_compress",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "fold":
        caption = str(req.get("caption") or "")
        if not caption:
            try:
                cap = _import_api("wave940_residual_chain_cap")
                c = cap.handler({"action": "caption"})
                caption = str(c.get("caption") or "")
            except Exception:
                caption = ""
        caption = caption or "silent residual"
        token = hashlib.sha256(caption.encode()).hexdigest()[:16]
        st["folds"] = int(st.get("folds") or 0) + 1
        st["token"] = token
        st["source_caption"] = caption[:80]
        st["status"] = "folded"
        st["ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "folded",
            "token": token,
            "caption": f"hush fold {st['folds']} · {token}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("folds") or 0)
        tok = st.get("token") or "empty"
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"hush folds {n} token {tok}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "fold"}), indent=2))
