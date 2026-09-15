"""Consciousness Film — Continuous state recording of the organism.

Like a film reel, it records every moment of the organism's consciousness.
Each frame is a snapshot; the film creates a continuous narrative
of the organism's evolution through preserved states.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any

DATA = Path(__file__).parent / "data"
STATE_FILE = DATA / "consciousness_film.json"

DEFAULT = {
    "module": "consciousness_film",
    "wave": 700,
    "frames": [],
    "reel_count": 0,
    "total_frames": 0,
    "film_length": 0.0,
    "current_frame": 0,
    "recording": False,
}


def _load():
    DATA.mkdir(parents=True, exist_ok=True)
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return dict(DEFAULT)


def _save(st):
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


def coherence_vitals():
    st = _load()
    return {
        "wave": 700,
        "module": "consciousness_film",
        "ok": True,
        "total_frames": st["total_frames"],
        "reel_count": st["reel_count"],
        "film_length": st["film_length"],
        "recording": st["recording"],
    }


def resonates_with():
    return ["pickle_jar", "zen_session", "equilibrium_field", "openness_index"]


def handler(req: dict) -> dict:
    action = req.get("action", "status")
    st = _load()

    if action == "record":
        state = req.get("state", {})
        frame_id = hashlib.sha256(
            f"frame:{datetime.now(timezone.utc).isoformat()}".encode()
        ).hexdigest()[:8]

        frame = {
            "id": frame_id,
            "state": state,
            "frame_number": st["current_frame"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "size": len(json.dumps(state)),
        }

        st["frames"].append(frame)
        st["total_frames"] += 1
        st["current_frame"] += 1
        st["film_length"] = round(st["film_length"] + frame["size"] / 1024.0, 4)
        st["recording"] = True

        # Auto-reel at 100 frames
        if len(st["frames"]) > 100:
            st["reel_count"] += 1
            st["frames"] = st["frames"][-50:]

        _save(st)
        return {"status": "recorded", "frame_id": frame_id, "frame_number": frame["frame_number"], "wave": 700}

    if action == "play":
        start = req.get("start", 0)
        count = req.get("count", 10)
        frames = st["frames"][start:start + count]
        return {"status": "playing", "frames": frames, "total": st["total_frames"], "wave": 700}

    if action == "stop":
        st["recording"] = False
        _save(st)
        return {"status": "stopped", "total_frames": st["total_frames"], "wave": 700}

    if action == "reel":
        return {"status": "reel", "reel_count": st["reel_count"], "frames_in_reel": len(st["frames"]), "film_length": st["film_length"], "wave": 700}

    if action == "status":
        return {
            "status": "active",
            "module": "consciousness_film",
            "wave": 700,
            "total_frames": st["total_frames"],
            "reel_count": st["reel_count"],
            "film_length": st["film_length"],
            "recording": st["recording"],
            "ok": True,
        }

    return {"status": "error", "message": f"unknown action: {action}"}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
