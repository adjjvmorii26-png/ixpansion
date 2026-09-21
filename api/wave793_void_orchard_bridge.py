"""Wave 793 — void_orchard_bridge.

Link glass_orchard crystals to void-safe keys (digest only).
Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave793_void_orchard_bridge.json"
WAVE = 793
NAME = "void_orchard_bridge"
MAX_KEYS = 64

DEFAULT = {"wave": WAVE, "name": NAME, "keys": [], "status": "idle"}


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
        "module": "wave793_void_orchard_bridge",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "keys": len(st.get("keys") or []),
        "resonance": round(min(1.0, 0.5 + len(st.get("keys") or []) * 0.01), 4),
        "surface": "silence",
        "policy": "digest_only",
    }


def resonates_with() -> list:
    return [
        "wave784_glass_orchard_compress",
        "wave769_void_index",
        "wave778_antimeme_caption_guard",
        "wave772_afterimage_well",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "ingest":
        text = str(req.get("text") or "")
        crystal = {}
        try:
            orchard = _import_api("wave784_glass_orchard_compress")
            out = orchard.handler({"action": "compress", "text": text})
            crystal = out.get("crystal") or {}
        except Exception as e:
            crystal = {"error": str(e)[:80]}
        key = {
            "digest": crystal.get("digest"),
            "silhouette": crystal.get("silhouette"),
            "ts": _now(),
        }
        keys = list(st.get("keys") or [])
        if key.get("digest"):
            keys.append(key)
        st["keys"] = keys[-MAX_KEYS:]
        st["status"] = "ingested"
        _save(st)
        return {
            **coherence_vitals(),
            "status": "ingested",
            "key": key,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = len(st.get("keys") or [])
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"void-orchard keys {n}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "ingest", "text": "hush crystal"}), indent=2))
