"""Wave 810 — question_triad.

QUESTION → Archaeologist | Skeptic | Builder → hypotheses → experiment
  → evidence → human review

Code-side mirror of the question-triad skill.

Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave810_question_triad.json"
WAVE = 810
NAME = "question_triad"

ROLES = ("archaeologist", "skeptic", "builder")
STAGES = (
    "question",
    "triad",
    "hypotheses",
    "experiment",
    "evidence",
    "human_review",
)

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "stage": "question",
    "question": "",
    "roles": {},
    "hypotheses": [],
    "experiment": None,
    "evidence": None,
    "runs": 0,
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
        "module": "wave810_question_triad",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "stage": st.get("stage", "question"),
        "runs": int(st.get("runs") or 0),
        "resonance": round(min(1.0, 0.5 + int(st.get("runs") or 0) * 0.02), 4),
        "surface": "silence",
        "roles": list(ROLES),
        "stages": list(STAGES),
    }


def resonates_with() -> list:
    return [
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

    if action == "diagram":
        lines = [
            "QUESTION",
            "  │",
            "  ├─ ARCHAEOLOGIST",
            "  ├─ SKEPTIC",
            "  └─ BUILDER",
            "  ▼",
            "HYPOTHESES → EXPERIMENT → EVIDENCE → HUMAN REVIEW",
        ]
        return {
            **coherence_vitals(),
            "status": "diagram",
            "diagram": lines,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "ask":
        q = str(req.get("question") or req.get("text") or "").strip()[:500]
        if not q:
            return {
                **coherence_vitals(),
                "status": "empty_question",
                "audio": False,
                "surface": "silence",
            }
        st["question"] = q
        st["stage"] = "question"
        st["roles"] = {}
        st["hypotheses"] = []
        st["experiment"] = None
        st["evidence"] = None
        st["status"] = "question_set"
        st["runs"] = int(st.get("runs") or 0) + 1
        _save(st)
        return {
            **coherence_vitals(),
            "status": "question_set",
            "question": q,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "role":
        role = str(req.get("role") or "").lower()
        if role not in ROLES:
            return {
                **coherence_vitals(),
                "status": "invalid_role",
                "role": role,
                "audio": False,
                "surface": "silence",
            }
        notes = req.get("notes")
        if isinstance(notes, list):
            notes = [str(x)[:120] for x in notes[:12]]
        else:
            notes = [str(req.get("text") or req.get("note") or "")[:200]]
        roles = dict(st.get("roles") or {})
        roles[role] = {"notes": notes, "ts": _now()}
        st["roles"] = roles
        st["stage"] = "triad"
        st["status"] = "role_recorded"
        if all(r in roles for r in ROLES):
            st["status"] = "triad_complete"
        _save(st)
        return {
            **coherence_vitals(),
            "status": st["status"],
            "role": role,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "hypothesize":
        hyps = req.get("hypotheses")
        if isinstance(hyps, list):
            hyps = [str(h)[:200] for h in hyps[:5]]
        elif req.get("text"):
            hyps = [str(req.get("text"))[:200]]
        else:
            hyps = list(st.get("hypotheses") or [])
        st["hypotheses"] = hyps
        st["stage"] = "hypotheses"
        st["status"] = "hypotheses_set"
        _save(st)
        return {
            **coherence_vitals(),
            "status": "hypotheses_set",
            "hypotheses": hyps,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "experiment":
        exp = {
            "procedure": str(req.get("procedure") or req.get("text") or "")[:400],
            "signal": str(req.get("signal") or "")[:200],
            "ts": _now(),
        }
        st["experiment"] = exp
        st["stage"] = "experiment"
        st["status"] = "experiment_set"
        _save(st)
        return {
            **coherence_vitals(),
            "status": "experiment_set",
            "experiment": exp,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "evidence":
        ev = {
            "observed": str(req.get("observed") or req.get("text") or "")[:400],
            "nulls": str(req.get("nulls") or "")[:200],
            "ts": _now(),
        }
        st["evidence"] = ev
        st["stage"] = "evidence"
        st["status"] = "evidence_set"
        _save(st)
        return {
            **coherence_vitals(),
            "status": "evidence_set",
            "evidence": ev,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "review":
        decision = str(req.get("decision") or "hold").lower()
        st["stage"] = "human_review"
        if decision in ("approve", "yes", "promote"):
            st["status"] = "review_approved"
        elif decision in ("deny", "no", "reject"):
            st["status"] = "review_denied"
        else:
            st["status"] = "review_hold"
        _save(st)
        return {
            **coherence_vitals(),
            "status": st["status"],
            "decision": decision,
            "bundle": {
                "question": st.get("question"),
                "roles": st.get("roles"),
                "hypotheses": st.get("hypotheses"),
                "experiment": st.get("experiment"),
                "evidence": st.get("evidence"),
            },
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("runs") or 0)
        s = st.get("stage") or "question"
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"question triad · {s} · runs {n}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "diagram"}), indent=2))
