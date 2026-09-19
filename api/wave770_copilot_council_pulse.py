"""Wave 770 — copilot_council_pulse.

Bridges AEGIS · HELIX · QUILL into an organ surface so the dashboard,
API, and GitHub Copilot agents share one pulse contract.

Silence is the product surface. Captions only — no audio.
Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave770_copilot_council_pulse.json"
WAVE = 770
NAME = "copilot_council_pulse"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "pulses": 0,
    "last_posture": "unknown",
    "last_headline": "",
    "last_ts": None,
    "status": "idle",
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


def _run_council() -> dict:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    try:
        from lab.ops.copilots.council import run_council

        return run_council()
    except Exception as e:
        return {"ok": False, "error": str(e), "council": []}


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave770_copilot_council_pulse",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "pulses": int(st.get("pulses") or 0),
        "last_posture": st.get("last_posture", "unknown"),
        "resonance": round(min(1.0, 0.55 + int(st.get("pulses") or 0) * 0.01), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave768_hush_compass",
        "wave769_void_index",
        "wave767_mycelial_truths",
        "lab.ops.copilots.council",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {
            **coherence_vitals(),
            "last_headline": st.get("last_headline") or "",
            "last_ts": st.get("last_ts"),
            "surface": "silence",
        }

    if action == "pulse":
        package = _run_council()
        scan = ((package.get("aegis") or {}).get("scan") or {}) if isinstance(package, dict) else {}
        quill = (package.get("quill") or {}) if isinstance(package, dict) else {}
        posture = scan.get("posture") or "unknown"
        headline = quill.get("headline") or ""
        st["pulses"] = int(st.get("pulses") or 0) + 1
        st["last_posture"] = posture
        st["last_headline"] = str(headline)[:200]
        st["last_ts"] = _now()
        st["status"] = "pulsed"
        _save(st)
        next_moves = package.get("next_moves") if isinstance(package, dict) else []
        return {
            **coherence_vitals(),
            "status": "pulsed",
            "posture": posture,
            "headline": headline,
            "next_moves": next_moves[:5] if isinstance(next_moves, list) else [],
            "payload": None,
            "surface": "silence",
            "audio": False,
        }

    if action == "caption":
        posture = st.get("last_posture") or "unknown"
        n = int(st.get("pulses") or 0)
        caption = f"council {posture} · pulses {n}"
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
