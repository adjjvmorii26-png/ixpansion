"""Wave 808 — discovery_cycle_engine.

Implements the closed discovery loop:

  OBSERVE → DISCOVER → HYPOTHESIZE → MUTATE → REPLAY
         → MEASURE → LEARN → RECORD → HUMAN REVIEW → PROMOTE → OBSERVE

Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave808_discovery_cycle_engine.json"
WAVE = 808
NAME = "discovery_cycle_engine"

STAGES = (
    "observe",
    "discover",
    "hypothesize",
    "mutate",
    "replay",
    "measure",
    "learn",
    "record",
    "human_review",
    "promote",
)

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "stage": "observe",
    "cycles": 0,
    "promotions": 0,
    "log": [],
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
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave808_discovery_cycle_engine",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "stage": st.get("stage", "observe"),
        "cycles": int(st.get("cycles") or 0),
        "promotions": int(st.get("promotions") or 0),
        "resonance": round(
            min(1.0, 0.5 + int(st.get("cycles") or 0) * 0.01 + int(st.get("promotions") or 0) * 0.02),
            4,
        ),
        "surface": "silence",
        "stages": list(STAGES),
    }


def resonates_with() -> list:
    return [
        "wave783_hitl_publish_gate",
        "wave794_organ_debt_auditor",
        "wave770_copilot_council_pulse",
        "wave785_silent_publish_orchestrator",
    ]


def _next_stage(stage: str) -> str:
    if stage not in STAGES:
        return "observe"
    i = STAGES.index(stage)
    return STAGES[(i + 1) % len(STAGES)]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "diagram":
        lines = [
            "OBSERVE",
            "  ↓",
            "DISCOVER",
            "  ↓",
            "HYPOTHESIZE",
            "  ↓",
            "MUTATE",
            "  ↓",
            "REPLAY",
            "  ↓",
            "MEASURE",
            "  ↓",
            "LEARN",
            "  ↓",
            "RECORD",
            "  ↓",
            "HUMAN REVIEW",
            "  ↓",
            "PROMOTE → OBSERVE",
        ]
        return {
            **coherence_vitals(),
            "status": "diagram",
            "diagram": lines,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "advance":
        note = str(req.get("note") or "")[:120]
        cur = st.get("stage") or "observe"
        if cur not in STAGES:
            cur = "observe"
        nxt = _next_stage(cur)
        log = list(st.get("log") or [])
        log.append({"from": cur, "to": nxt, "note": note, "ts": _now()})
        st["log"] = log[-48:]
        st["stage"] = nxt
        st["status"] = "advanced"
        if nxt == "observe" and cur == "promote":
            st["cycles"] = int(st.get("cycles") or 0) + 1
            st["promotions"] = int(st.get("promotions") or 0) + 1
            st["status"] = "cycled"
        _save(st)
        return {
            **coherence_vitals(),
            "status": st["status"],
            "from": cur,
            "to": nxt,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "jump":
        stage = str(req.get("stage") or "").lower().replace(" ", "_")
        if stage not in STAGES:
            return {
                **coherence_vitals(),
                "status": "invalid_stage",
                "stage_requested": stage,
                "audio": False,
                "surface": "silence",
            }
        st["stage"] = stage
        st["status"] = "jumped"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "jumped",
            "stage": stage,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "review":
        decision = str(req.get("decision") or "hold").lower()
        st["stage"] = "human_review"
        if decision in ("approve", "promote", "yes"):
            st["stage"] = "promote"
            st["status"] = "review_approved"
        elif decision in ("deny", "reject", "no"):
            st["status"] = "review_denied"
        else:
            st["status"] = "review_hold"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": st["status"],
            "decision": decision,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "run_once":
        notes = req.get("notes") if isinstance(req.get("notes"), dict) else {}
        path = []
        st["stage"] = "observe"
        for stage in STAGES:
            if stage == "human_review":
                st["stage"] = stage
                path.append(stage)
                break
            st["stage"] = stage
            path.append(stage)
            note = str(notes.get(stage) or "")[:80]
            log = list(st.get("log") or [])
            log.append({"stage": stage, "note": note, "ts": _now()})
            st["log"] = log[-48:]
        st["status"] = "awaiting_human_review"
        _save(st)
        return {
            **coherence_vitals(),
            "status": "awaiting_human_review",
            "path": path,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        c = int(st.get("cycles") or 0)
        s = st.get("stage") or "observe"
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"discovery cycle · stage {s} · cycles {c}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "diagram"}), indent=2))
