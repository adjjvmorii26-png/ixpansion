"""Wave 819 — forge_ledger_mirror.

Mirror skillforge evolution_ledger decisions into a compact local trail
and optional null_evidence when decision is compost/archive.

Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave819_forge_ledger_mirror.json"
WAVE = 819
NAME = "forge_ledger_mirror"

DEFAULT = {"wave": WAVE, "name": NAME, "mirrors": 0, "trail": [], "status": "idle"}


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
        "module": "wave819_forge_ledger_mirror",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "mirrors": int(st.get("mirrors") or 0),
        "trail_len": len(st.get("trail") or []),
        "resonance": round(min(1.0, 0.5 + int(st.get("mirrors") or 0) * 0.02), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave817_skillforge_engine",
        "wave813_null_evidence_registry",
        "wave818_skillforge_stack_bridge",
        "wave814_lineage_null_fuse",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {
            **coherence_vitals(),
            "trail_tail": (st.get("trail") or [])[-5:],
            "audio": False,
            "surface": "silence",
        }

    if action == "mirror":
        decision = str(req.get("decision") or "hold").lower()
        note = str(req.get("note") or "")[:160]
        skill = str(req.get("skill") or "skill")[:80]
        try:
            forge = _import_api("wave817_skillforge_engine")
            entry = forge.handler({"action": "ledger", "decision": decision, "note": note or skill})
            steps = {"forge": entry.get("status")}
        except Exception as e:
            steps = {"forge": {"error": str(e)[:80]}}
        if decision in ("compost", "archive"):
            try:
                reg = _import_api("wave813_null_evidence_registry")
                reg.handler({
                    "action": "record",
                    "hypothesis": f"promote:{skill}",
                    "note": f"{decision}: {note}",
                })
                steps["null"] = "recorded"
            except Exception as e:
                steps["null"] = str(e)[:60]
        trail = list(st.get("trail") or [])
        trail.append({"skill": skill, "decision": decision, "ts": _now()})
        st["trail"] = trail[-64:]
        st["mirrors"] = int(st.get("mirrors") or 0) + 1
        st["status"] = "mirrored"
        _save(st)
        return {
            **coherence_vitals(),
            "status": "mirrored",
            "decision": decision,
            "steps": steps,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("mirrors") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"forge ledger mirrors {n}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "mirror", "skill": "x", "decision": "hold"}), indent=2))
