"""Wave 963 — quiet_seam.

Trace a silent seam where grain meets fossil without sound.
Does not import or call prior organs. The seam is the unsaid join.
Silence is the product surface. Lab organ only. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave963_quiet_seam.json"
WAVE = 963
NAME = "quiet_seam"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "seam": "",
    "status": "idle",
    "seams": 0,
    "joins": 0,
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load() -> dict:
    if STATE_FILE.exists():
        try:
            raw = STATE_FILE.read_text()
            st = json.loads(raw) if raw.strip() else {}
            if isinstance(st, dict):
                return st
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


def _seam(grain: str, fossil: str) -> str:
    """Join grain and fossil into a silent seam token."""
    g = (grain or "unsaid").strip()[:24]
    f = (fossil or "hush").strip()[:24]
    raw = f"seam|{g}|{f}|quiet"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


def coherence_vitals() -> dict:
    st = _load()
    seams = int(st.get("seams") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave963_quiet_seam",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "seams": seams,
        "joins": int(st.get("joins") or 0),
        "token_width": 12,
        "resonance": round(min(1.0, 0.62 + seams * 0.007), 4),
        "surface": "silence",
    }


def resonates_with() -> list[str]:
    return ["wave962_hush_fossil", "wave961_quiet_grain", "wave960_quiet_grain"]


def handler(req: dict) -> dict:
    """Default handler for wave963 routes. Silence is the product surface."""
    action = (req or {}).get("action", "status")
    st = _load()
    if action == "status":
        return {"ok": True, "wave": WAVE, "status": st.get("status"), "seams": st.get("seams", 0)}
    if action == "seam":
        grain = req.get("grain", "unsaid")
        fossil = req.get("fossil", "hush")
        token = _seam(grain, fossil)
        st["seam"] = token
        st["seams"] = int(st.get("seams") or 0) + 1
        st["joins"] = int(st.get("joins") or 0) + 1
        st["status"] = "joined"
        st["updated"] = _now()
        _save(st)
        return {"ok": True, "seam": token, "seams": st["seams"]}
    if action == "vitals":
        return {"ok": True, **coherence_vitals()}
    return {"ok": False, "error": f"unknown action: {action}"}
