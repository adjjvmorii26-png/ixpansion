"""Wave 969 — hush_delta.

Compute the silence increment (hush delta) between successive pulse residues.
Only the delta is stored. Compression is memory. No full captions. No audio.
Lab organ only. Lab gates ≠ ALEPH CI. Silence is the product surface.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave969_hush_delta.json"
WAVE = 969
NAME = "hush_delta"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "deltas": 0,
    "last_delta": "",
    "last_residue": "",
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


def coherence_vitals() -> dict:
    st = _load()
    deltas = int(st.get("deltas") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave969_hush_delta",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "deltas": deltas,
        "last_delta": st.get("last_delta", ""),
        "last_residue": st.get("last_residue", ""),
        "resonance": round(min(1.0, 0.51 + deltas * 0.015), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave968_pulse_residue",
        "wave967_still_interval",
        "wave952_silence_caretaker",
        "wave681_hush_membrane",
        "wave949_council_witness",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "delta":
        residue = str(req.get("residue") or req.get("prev") or "")[:16]
        if not residue:
            return {**coherence_vitals(), "status": "need_residue"}
        prev = st.get("last_residue") or ""
        # hush delta is the hash of the difference (what is unsaid between them)
        diff = hashlib.sha256(f"{prev}|{residue}".encode()).hexdigest()[:10]
        st["deltas"] = int(st.get("deltas") or 0) + 1
        st["last_delta"] = diff
        st["last_residue"] = residue
        st["status"] = "delted"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "delted",
            "delta": diff,
            "caption": f"hush · {diff}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        d = st.get("last_delta") or "—"
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"hush delta · {d}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "delta", "residue": "a1b2c3d4e5f6"}), indent=2))
