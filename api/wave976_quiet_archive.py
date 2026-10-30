"""Wave 976 — Quiet Archive.

Compresses non-events and silence intervals into durable memory tokens.
Silence is the product surface. Compression is memory.
Lab organ only. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave976_quiet_archive.json"
WAVE = 976
NAME = "quiet_archive"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "archives": 0,
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


def _compress(silence_ms: int, note: str = "") -> str:
    """Compression is memory: turn absence into a short token."""
    raw = f"quiet:{silence_ms}:{note or 'void'}"
    return hashlib.sha256(raw.encode()).hexdigest()[:10]


def coherence_vitals() -> dict:
    st = _load()
    n = int(st.get("archives") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave976_quiet_archive",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "archives": n,
        "tokens": len(st.get("tokens") or []),
        "resonance": round(min(1.0, 0.48 + n * 0.008), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave950_hush_margin",
        "wave941_hush_fold",
        "wave681_hush_membrane",
        "wave700_still_interval",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "archive":
        silence_ms = int(req.get("silence_ms") or 0)
        note = str(req.get("note") or "")[:80]
        token = _compress(silence_ms, note)
        tokens = st.setdefault("tokens", [])
        tokens.append({
            "token": token,
            "silence_ms": silence_ms,
            "note": note,
            "ts": _now(),
        })
        tokens[:] = tokens[-32:]
        st["archives"] = int(st.get("archives") or 0) + 1
        st["status"] = "archived"
        st["last_token"] = token
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "archived",
            "token": token,
            "caption": f"quiet archived · {token}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        last = st.get("last_token") or "empty"
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"silence compressed · {last}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "archive", "silence_ms": 1200, "note": "pulse gap"}), indent=2))
