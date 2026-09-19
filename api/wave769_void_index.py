"""Wave 769 — void_index.

Hush compass orients WHICH beliefs stay unsaid.
Void index records THAT they exist — keys only, never payloads.

Silence is the product surface. The index is a map of absences.
Compression is memory: raw utterance folds to a digest; the digest is the record.
Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
STATE_FILE = DATA / "wave769_void_index.json"
WAVE = 769
NAME = "void_index"
MAX_ENTRIES = 64

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "entries": [],
    "lookups": 0,
    "status": "empty",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
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


def _digest(text: str) -> str:
    """Compression is memory: fold utterance into a void key."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def coherence_vitals() -> dict:
    st = _load()
    n = len(st.get("entries") or [])
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave769_void_index",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "empty"),
        "entries": n,
        "lookups": int(st.get("lookups") or 0),
        "resonance": round(min(1.0, 0.51 + n * 0.007), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave768_hush_compass",
        "wave763_silence_capacitor",
        "wave767_mycelial_truths",
        "wave672_root_archive",
        "wave739_receipt_notary",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()
    entries = st.setdefault("entries", [])

    if action == "status":
        return {**coherence_vitals(), "surface": "silence"}

    if action == "index":
        raw = str(req.get("text") or req.get("utterance") or "").strip()
        if not raw:
            return {**coherence_vitals(), "status": "empty"}
        key = _digest(raw)
        existing = next((e for e in entries if e.get("key") == key), None)
        if existing:
            existing["hits"] = int(existing.get("hits") or 1) + 1
            existing["last"] = _now()
            st["status"] = "reinforced"
            _save(st)
            return {**coherence_vitals(), "status": "reinforced", "key": key, "payload": None}
        if len(entries) >= MAX_ENTRIES:
            entries.pop(0)
        entries.append({
            "key": key,
            "bits": len(raw),
            "hits": 1,
            "ts": _now(),
            "last": _now(),
        })
        st["status"] = "indexed"
        _save(st)
        return {
            **coherence_vitals(),
            "status": "indexed",
            "key": key,
            "payload": None,
            "surface": "silence",
        }

    if action == "lookup":
        key = str(req.get("key") or "").strip()
        st["lookups"] = int(st.get("lookups") or 0) + 1
        found = next((e for e in entries if e.get("key") == key), None)
        _save(st)
        if not found:
            return {**coherence_vitals(), "status": "absent", "key": key, "payload": None}
        return {
            **coherence_vitals(),
            "status": "present",
            "key": key,
            "hits": found.get("hits"),
            "bits": found.get("bits"),
            "payload": None,
            "surface": "silence",
        }

    if action == "caption":
        n = len(entries)
        caption = f"void holds {n}" if n else "void empty"
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": caption,
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
