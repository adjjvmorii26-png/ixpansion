"""Wave 940 — caretaker_silence.

Record a quiet hold of the daily caretaker pulse.
Silence is the product surface. No audio. Lab organ only.
Dual-track: lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave940_caretaker_silence.json"
WAVE = 940
NAME = "caretaker_silence"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "holds": 0,
    "main_sha": "",
    "open_prs": 0,
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
    holds = int(st.get("holds") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave940_caretaker_silence",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "holds": holds,
        "main_sha": st.get("main_sha") or "",
        "open_prs": int(st.get("open_prs") or 0),
        "resonance": round(min(1.0, 0.54 + holds * 0.02), 4),
        "surface": "silence",
        "track": "lab",
    }


def resonates_with() -> list:
    return [
        "wave939_residual_bind",
        "wave938_pulse_compress",
        "lab.ops.copilots.council",
        "dual_track_sentinel",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "hold":
        sha = str(req.get("main_sha") or st.get("main_sha") or "unknown")[:12]
        try:
            open_prs = int(req.get("open_prs") if req.get("open_prs") is not None else st.get("open_prs") or 0)
        except (TypeError, ValueError):
            open_prs = 0
        st["holds"] = int(st.get("holds") or 0) + 1
        st["main_sha"] = sha
        st["open_prs"] = max(0, open_prs)
        st["status"] = "held"
        st["ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "held",
            "hold": {"main_sha": sha, "open_prs": st["open_prs"], "token": "quiet"},
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("holds") or 0)
        sha = st.get("main_sha") or "unset"
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"caretaker silence hold {n} @ {sha}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action, "audio": False}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "hold", "main_sha": "767bd5faaa33", "open_prs": 20}), indent=2))
