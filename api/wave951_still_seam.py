"""Wave 951 — still_seam.

Hold residual silence between hush folds (950/949).
Compression is memory. No payload. Silence is the product surface.
Lab organ only. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave951_still_seam.json"
WAVE = 951
NAME = "still_seam"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "seams": 0,
    "compressed": 0,
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


def _compress(residual: str) -> int:
    """Compression is memory: length of residual becomes stored charge."""
    return max(0, min(64, len(residual or "")))


def coherence_vitals() -> dict:
    st = _load()
    seams = int(st.get("seams") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave951_still_seam",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "seams": seams,
        "compressed": int(st.get("compressed") or 0),
        "resonance": round(min(1.0, 0.62 + seams * 0.008), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave950_hush_margin",
        "wave949_council_witness",
        "wave941_hush_fold",
        "wave681_hush_membrane",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "seam":
        residual = str(req.get("residual") or "")[:128]
        charge = _compress(residual)
        st["seams"] = int(st.get("seams") or 0) + 1
        st["compressed"] = int(st.get("compressed") or 0) + charge
        st["status"] = "seamed"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "seamed",
            "charge": charge,
            "caption": f"still seam · {charge}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        c = int(st.get("compressed") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"compressed silence {c}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "seam", "residual": "hush"}), indent=2))
