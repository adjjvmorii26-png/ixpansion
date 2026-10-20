"""Wave 968 — pulse_residue.

Compress successive pulse captions into a short residue token.
The residue is memory. No full replay. No payload.
Lab organ only. Lab gates ≠ ALEPH CI. Silence is the product surface.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave968_pulse_residue.json"
WAVE = 968
NAME = "pulse_residue"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "residues": 0,
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
    residues = int(st.get("residues") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave968_pulse_residue",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "residues": residues,
        "last_residue": st.get("last_residue", ""),
        "resonance": round(min(1.0, 0.48 + residues * 0.018), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave967_still_interval",
        "wave966_ci_sentinel",
        "wave949_council_witness",
        "wave952_silence_caretaker",
        "wave681_hush_membrane",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "compress":
        captions = req.get("captions") or []
        if not isinstance(captions, list):
            captions = [str(captions)]
        text = "|".join(str(c)[:80] for c in captions[-8:])  # last 8, truncated
        residue = hashlib.sha256(text.encode()).hexdigest()[:12]
        st["residues"] = int(st.get("residues") or 0) + 1
        st["last_residue"] = residue
        st["status"] = "compressed"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "compressed",
            "residue": residue,
            "caption": f"residue · {residue}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        res = st.get("last_residue") or "—"
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"pulse residue · {res}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "compress", "captions": ["still 12.4s", "sentinel lab_noise"]}), indent=2))
