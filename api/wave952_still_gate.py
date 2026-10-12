"""Wave 952 — still_gate.

Silent classifier for dual-track doctrine. Distinguishes lab vs organism
without emitting sound or claiming full ALEPH CI. No audio.
Lab organ only. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave952_still_gate.json"
WAVE = 952
NAME = "still_gate"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "classifications": 0,
    "last_track": "none",
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


def classify(pull: dict | None = None) -> dict:
    """Classify a PR onto lab / organism / dual without noise."""
    pull = pull or {}
    title = str(pull.get("title") or "").lower()
    branch = str(pull.get("head") or pull.get("branch") or "")
    files = [str(f) for f in (pull.get("files") or [])]
    lab = branch.startswith(("lab/", "experiment/", "hardening/")) or title.startswith("experiment:") or title.startswith("lab:")
    organism = any(f.startswith(("api_server.py", "Dockerfile", ".github/")) or f == "api_server.py" for f in files)
    if lab and organism:
        track = "dual"
    elif lab:
        track = "lab"
    else:
        track = "organism"
    return {
        "wave": WAVE,
        "track": track,
        "merge_gate": "lab" if track == "lab" else "organism",
        "do_not_merge": title.startswith("experiment:"),
        "audio": None,
        "surface": "silence",
    }


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave952_still_gate",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "classifications": int(st.get("classifications") or 0),
        "last_track": st.get("last_track", "none"),
        "resonance": 0.62,
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave951_dual_track_pr_bot",
        "wave950_hush_margin",
        "wave822_gate_priority",
        "wave686_dual_track_sentinel",
    ]


def handler(req: dict | None = None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "classify":
        result = classify(req.get("pull") or req)
        st["classifications"] = int(st.get("classifications") or 0) + 1
        st["last_track"] = result["track"]
        st["status"] = "classified"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            **result,
            "status": "classified",
            "caption": f"still gate · {result['track']}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "classify", "title": "lab: test", "head": "lab/foo"}), indent=2))
