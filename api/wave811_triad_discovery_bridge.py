"""Wave 811 — triad_discovery_bridge.

Wire question_triad (810) into discovery_cycle_engine (808):
after triad_complete + hypotheses, seed discovery at hypothesize/mutate.

Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave811_triad_discovery_bridge.json"
WAVE = 811
NAME = "triad_discovery_bridge"

DEFAULT = {"wave": WAVE, "name": NAME, "bridges": 0, "status": "idle"}


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
        "module": "wave811_triad_discovery_bridge",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "bridges": int(st.get("bridges") or 0),
        "resonance": round(min(1.0, 0.5 + int(st.get("bridges") or 0) * 0.02), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave810_question_triad",
        "wave808_discovery_cycle_engine",
        "wave809_meta_experiment_loop",
        "wave783_hitl_publish_gate",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "bridge":
        steps = {}
        try:
            triad = _import_api("wave810_question_triad")
            tstat = triad.handler({"action": "status"})
            steps["triad"] = {"stage": tstat.get("stage"), "status": tstat.get("status")}
        except Exception as e:
            steps["triad"] = {"error": str(e)[:80]}
            tstat = {}
        ready = tstat.get("status") in (
            "triad_complete",
            "hypotheses_set",
            "experiment_set",
            "evidence_set",
        )
        try:
            disc = _import_api("wave808_discovery_cycle_engine")
            if ready:
                j = disc.handler({"action": "jump", "stage": "hypothesize"})
                steps["discovery"] = {"status": j.get("status"), "stage": j.get("stage")}
            else:
                steps["discovery"] = {"status": "skipped", "reason": "triad_not_ready"}
        except Exception as e:
            steps["discovery"] = {"error": str(e)[:80]}
        st["bridges"] = int(st.get("bridges") or 0) + 1
        st["status"] = "bridged" if ready else "waiting"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": st["status"],
            "ready": ready,
            "steps": steps,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("bridges") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"triad→discovery bridges {n}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "bridge"}), indent=2))
