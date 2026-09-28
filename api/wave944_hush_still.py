"""Wave 944 — hush_still.

Compress the last hush ledger token (or a provided seal) into a still residue.
Does not re-record the ledger. Silence is the product surface. Lab organ only.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave944_hush_still.json"
WAVE = 944
NAME = "hush_still"
STILL_LEN = 8

DEFAULT = {"wave": WAVE, "name": NAME, "still": "", "source": "", "status": "idle"}


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


def _still_of(source: str) -> str:
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    return digest[:STILL_LEN]


def coherence_vitals() -> dict:
    st = _load()
    still = str(st.get("still") or "")
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave944_hush_still",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "still": still,
        "source": str(st.get("source") or ""),
        "resonance": round(0.54 + (0.08 if still else 0.0), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave942_hush_ledger",
        "wave941_hush_fold",
        "wave938_pulse_compress",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "still":
        source = str(req.get("seal") or req.get("token") or "")
        if not source:
            try:
                ledger = _import_api("wave942_hush_ledger")
                vitals = ledger.coherence_vitals()
                source = str(vitals.get("last_token") or "")
            except Exception:
                source = ""
        source = source or "empty-hush"
        still = _still_of(source)
        st["source"] = source[:16]
        st["still"] = still
        st["status"] = "stilled"
        st["ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "stilled",
            "still": still,
            "source": source[:16],
            "caption": f"hush still {still}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        still = str(st.get("still") or "empty")
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"hush still {still}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "still"}), indent=2))
