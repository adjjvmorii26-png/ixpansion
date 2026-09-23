"""Wave 816 — ci_gate_mirror.

Local mirror of dual-track gate advice: lab vs experiment.
Records last advised merge candidate from experiment_queue_atlas.

Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave816_ci_gate_mirror.json"
WAVE = 816
NAME = "ci_gate_mirror"

DEFAULT = {"wave": WAVE, "name": NAME, "checks": 0, "status": "idle"}


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


def _import_api(mod: str):
    api = ROOT / "api"
    if str(api) not in sys.path:
        sys.path.insert(0, str(api))
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    return __import__(mod)


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave816_ci_gate_mirror",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "checks": int(st.get("checks") or 0),
        "last_candidate": st.get("last_candidate"),
        "resonance": round(min(1.0, 0.5 + int(st.get("checks") or 0) * 0.02), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave812_experiment_queue_atlas",
        "wave787_dual_track_pr_bot",
        "wave815_stack_orchestrator",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "check":
        candidate = None
        try:
            atlas = _import_api("wave812_experiment_queue_atlas")
            ranked = atlas.handler({"action": "rank"})
            candidate = ranked.get("next_merge_candidate")
        except Exception as e:
            err = str(e)[:80]
        else:
            err = None
        st["checks"] = int(st.get("checks") or 0) + 1
        st["last_candidate"] = candidate
        st["status"] = "checked"
        st["last_ts"] = _now()
        _save(st)
        out = {
            **coherence_vitals(),
            "status": "checked",
            "next_merge_candidate": candidate,
            "advice": "hold experiment merges until CI green; lab path is clear",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }
        if err:
            out["error"] = err
        return out

    if action == "caption":
        n = int(st.get("checks") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"ci gate checks {n}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "check"}), indent=2))
