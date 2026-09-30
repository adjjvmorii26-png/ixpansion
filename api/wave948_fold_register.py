"""Wave 948 — fold_register.

Persist echo_fold (947) digests into a bounded silent register.
Does not replay audio. Silence is the product surface. Lab organ only.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave948_fold_register.json"
WAVE = 948
NAME = "fold_register"
CAP = 8

DEFAULT = {"wave": WAVE, "name": NAME, "entries": [], "status": "idle"}


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
    n = len(st.get("entries") or [])
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave948_fold_register",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "entries": n,
        "cap": CAP,
        "resonance": round(min(1.0, 0.52 + n * 0.03), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave947_echo_fold",
        "wave946_still_echo_slot",
        "wave945_still_residual_bridge",
        "wave938_pulse_compress",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "register":
        digest = str(req.get("digest") or "").strip()
        if not digest:
            try:
                fold = _import_api("wave947_echo_fold")
                st947 = fold._load() if hasattr(fold, "_load") else {}
                digest = str(st947.get("digest") or "")
            except Exception:
                digest = ""
        digest = digest[:16]
        entries = list(st.get("entries") or [])
        if digest and digest not in entries:
            entries.append(digest)
            entries = entries[-CAP:]
        st["entries"] = entries
        st["status"] = "registered"
        st["last_ts"] = _now()
        st["last_digest"] = digest
        _save(st)
        return {
            **coherence_vitals(),
            "status": "registered",
            "digest": digest,
            "entries": entries,
            "caption": f"fold register · n={len(entries)}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = len(st.get("entries") or [])
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"fold register {n}/{CAP}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "register"}), indent=2))
