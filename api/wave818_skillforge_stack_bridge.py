"""Wave 818 — skillforge_stack_bridge.

Bridge skillforge_engine (817) into stack_orchestrator (815):
after a forge mutation, seed a triad question about the variant.

Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave818_skillforge_stack_bridge.json"
WAVE = 818
NAME = "skillforge_stack_bridge"

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
        "module": "wave818_skillforge_stack_bridge",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "bridges": int(st.get("bridges") or 0),
        "resonance": round(min(1.0, 0.5 + int(st.get("bridges") or 0) * 0.02), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave817_skillforge_engine",
        "wave815_stack_orchestrator",
        "wave810_question_triad",
        "wave816_ci_gate_mirror",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "bridge":
        steps = {}
        variant = str(req.get("variant") or "").strip()[:80]
        try:
            forge = _import_api("wave817_skillforge_engine")
            fstat = forge.handler({"action": "status"})
            steps["forge"] = {"stage": fstat.get("stage"), "status": fstat.get("status")}
            if not variant:
                parent = str(req.get("parent") or "skill")[:80]
                m = forge.handler({"action": "mutate", "parent": parent, "variant": f"{parent}-lab"})
                variant = (m.get("mutation") or {}).get("variant") or f"{parent}-lab"
                steps["mutate"] = m.get("status")
        except Exception as e:
            steps["forge"] = {"error": str(e)[:80]}
            variant = variant or "skill-lab"
        q = str(req.get("question") or f"Should we promote skill variant {variant}?").strip()[:300]
        try:
            stack = _import_api("wave815_stack_orchestrator")
            steps["stack"] = stack.handler({"action": "run", "question": q})
        except Exception as e:
            steps["stack"] = {"error": str(e)[:80]}
        st["bridges"] = int(st.get("bridges") or 0) + 1
        st["status"] = "bridged"
        st["last_variant"] = variant
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "bridged",
            "variant": variant,
            "steps": {k: (v.get("status") if isinstance(v, dict) else v) for k, v in steps.items()},
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("bridges") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"skillforge→stack bridges {n}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "bridge", "parent": "skillforge"}), indent=2))
