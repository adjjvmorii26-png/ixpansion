"""Wave 821 — still_interval.

Compresses the dual-track gap (lab gates vs ALEPH noise) into a
silent still interval. The interval length is memory; the surface
is silence. Does not wait on full CI.

Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave821_still_interval.json"
WAVE = 821
NAME = "still_interval"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "stills": 0,
    "last_gap": None,
    "compressed": None,
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


def _compress_gap(lab_ok: bool, aleph_noise: bool) -> dict:
    """Fold the dual-track gap into a single still token."""
    if lab_ok and aleph_noise:
        token = "hold"
        width = 1.0
    elif lab_ok and not aleph_noise:
        token = "clear"
        width = 0.25
    elif not lab_ok and aleph_noise:
        token = "storm"
        width = 1.5
    else:
        token = "void"
        width = 0.5
    return {"token": token, "width": width, "surface": "silence"}


def coherence_vitals() -> dict:
    st = _load()
    stills = int(st.get("stills") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave821_still_interval",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "stills": stills,
        "last_gap": st.get("last_gap"),
        "resonance": round(min(1.0, 0.52 + stills * 0.01), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave820_observatory_pulse",
        "wave816_ci_gate_mirror",
        "wave799_hold_seam",
        "wave798_hush_afterglow",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "still":
        lab_ok = bool(req.get("lab_ok", True))
        aleph_noise = bool(req.get("aleph_noise", True))
        gap = {"lab_ok": lab_ok, "aleph_noise": aleph_noise, "ts": _now()}
        compressed = _compress_gap(lab_ok, aleph_noise)
        st["stills"] = int(st.get("stills") or 0) + 1
        st["last_gap"] = gap
        st["compressed"] = compressed
        st["status"] = "still"
        _save(st)
        return {
            **coherence_vitals(),
            "status": "still",
            "gap": gap,
            "compressed": compressed,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("stills") or 0)
        tok = (st.get("compressed") or {}).get("token")
        line = f"still interval ×{n}" + (f" · {tok}" if tok else "")
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": line,
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "still"}), indent=2))
