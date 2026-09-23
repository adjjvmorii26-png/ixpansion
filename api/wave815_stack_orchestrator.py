"""Wave 815 — stack_orchestrator.

One-shot silent path: triad → bridge → discovery → meta tick.
Does not auto-promote; stops before human_review when possible.

Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave815_stack_orchestrator.json"
WAVE = 815
NAME = "stack_orchestrator"

DEFAULT = {"wave": WAVE, "name": NAME, "runs": 0, "status": "idle"}


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
        "module": "wave815_stack_orchestrator",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "runs": int(st.get("runs") or 0),
        "resonance": round(min(1.0, 0.5 + int(st.get("runs") or 0) * 0.02), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave810_question_triad",
        "wave811_triad_discovery_bridge",
        "wave808_discovery_cycle_engine",
        "wave809_meta_experiment_loop",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "run":
        question = str(req.get("question") or req.get("text") or "what scales?").strip()[:300]
        steps = {}
        try:
            triad = _import_api("wave810_question_triad")
            steps["ask"] = triad.handler({"action": "ask", "question": question})
            for role, note in (
                ("archaeologist", "prior organs 808-814"),
                ("skeptic", "900-series CI still open"),
                ("builder", "bridge then discovery jump"),
            ):
                triad.handler({"action": "role", "role": role, "text": note})
            steps["triad"] = triad.handler({"action": "status"})
        except Exception as e:
            steps["triad"] = {"error": str(e)[:80]}
        try:
            bridge = _import_api("wave811_triad_discovery_bridge")
            steps["bridge"] = bridge.handler({"action": "bridge"})
        except Exception as e:
            steps["bridge"] = {"error": str(e)[:80]}
        try:
            disc = _import_api("wave808_discovery_cycle_engine")
            steps["discovery"] = disc.handler({"action": "run_once"})
        except Exception as e:
            steps["discovery"] = {"error": str(e)[:80]}
        try:
            meta = _import_api("wave809_meta_experiment_loop")
            steps["meta"] = meta.handler({"action": "advance", "note": "stack run"})
        except Exception as e:
            steps["meta"] = {"error": str(e)[:80]}
        st["runs"] = int(st.get("runs") or 0) + 1
        st["status"] = "ran"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "ran",
            "question": question,
            "steps": {k: (v.get("status") if isinstance(v, dict) else v) for k, v in steps.items()},
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("runs") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"stack orchestrator runs {n}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "run", "question": "probe"}), indent=2))
