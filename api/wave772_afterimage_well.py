"""Wave 772 — afterimage_well.

Compress a lab pulse into a short residue. Compression is memory.
Silence is the product surface. Lab gates ≠ ALEPH CI. No audio.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave772_afterimage_well.json"
WAVE = 772
NAME = "afterimage_well"
MAX_RESIDUES = 64

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "residues": [],
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


def _digest(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def coherence_vitals() -> dict:
    st = _load()
    n = len(st.get("residues") or [])
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave772_afterimage_well",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "residues": n,
        "resonance": round(min(1.0, 0.51 + n * 0.012), 4),
        "surface": "silence",
        "audio": False,
        "doctrine": "compression is memory",
    }


def resonates_with() -> list:
    return [
        "wave771_caption_pipeline_bridge",
        "wave769_void_index",
        "wave768_hush_compass",
        "wave674_dawn_ledger",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        last = (st.get("residues") or [None])[-1]
        return {
            **coherence_vitals(),
            "last": last,
            "surface": "silence",
            "audio": False,
        }

    if action in {"impress", "compress"}:
        note = str(req.get("note") or req.get("pulse") or "daily_pulse")[:240]
        frontier = str(req.get("frontier") or WAVE)
        payload = f"{frontier}|{note}|{_now()}"
        residue = {
            "hash": _digest(payload),
            "note": note,
            "frontier": frontier,
            "ts": _now(),
            "bytes_in": len(payload),
            "bytes_out": 16,
        }
        residues = list(st.get("residues") or [])
        residues.append(residue)
        st["residues"] = residues[-MAX_RESIDUES:]
        st["status"] = "impressed"
        _save(st)
        return {
            **coherence_vitals(),
            "status": "impressed",
            "residue": residue,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "recall":
        residues = list(st.get("residues") or [])
        key = str(req.get("hash") or "")
        hit = next((r for r in reversed(residues) if r.get("hash") == key), None) if key else (residues[-1] if residues else None)
        return {
            **coherence_vitals(),
            "status": "recalled" if hit else "empty",
            "residue": hit,
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
