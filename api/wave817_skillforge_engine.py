"""Wave 817 — skillforge_engine.

SKILLFORGE pipeline:
  skills|builders|tests → observatory → mutation_lab → forge_lab
  → hypotheses|experiments|challenges → evidence_graph → evolution_ledger

Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave817_skillforge_engine.json"
WAVE = 817
NAME = "skillforge_engine"

STAGES = (
    "intake",
    "observatory",
    "mutation_lab",
    "forge_lab",
    "hypotheses",
    "experiments",
    "challenges",
    "evidence_graph",
    "evolution_ledger",
)

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "stage": "intake",
    "runs": 0,
    "ledger": [],
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
        "module": "wave817_skillforge_engine",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "stage": st.get("stage", "intake"),
        "runs": int(st.get("runs") or 0),
        "ledger_len": len(st.get("ledger") or []),
        "resonance": round(min(1.0, 0.5 + int(st.get("runs") or 0) * 0.02), 4),
        "surface": "silence",
        "stages": list(STAGES),
    }


def resonates_with() -> list:
    return [
        "wave810_question_triad",
        "wave808_discovery_cycle_engine",
        "wave809_meta_experiment_loop",
        "wave813_null_evidence_registry",
        "wave815_stack_orchestrator",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "diagram":
        lines = [
            "SKILLFORGE",
            "  ├─ SKILLS  BUILDERS  TESTS",
            "  ▼ OBSERVATORY → MUTATION LAB → FORGE LAB",
            "  ├─ HYPOTHESES  EXPERIMENTS  CHALLENGES",
            "  ▼ EVIDENCE GRAPH → EVOLUTION LEDGER",
        ]
        return {
            **coherence_vitals(),
            "status": "diagram",
            "diagram": lines,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "intake":
        skills = req.get("skills") if isinstance(req.get("skills"), list) else []
        builders = req.get("builders") if isinstance(req.get("builders"), list) else []
        tests = req.get("tests") if isinstance(req.get("tests"), list) else []
        st["intake"] = {
            "skills": [str(s)[:80] for s in skills[:24]],
            "builders": [str(b)[:80] for b in builders[:12]],
            "tests": [str(t)[:80] for t in tests[:24]],
            "ts": _now(),
        }
        st["stage"] = "observatory"
        st["status"] = "intake_ok"
        _save(st)
        return {
            **coherence_vitals(),
            "status": "intake_ok",
            "intake": st["intake"],
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "advance":
        note = str(req.get("note") or "")[:160]
        cur = st.get("stage") or "intake"
        if cur not in STAGES:
            cur = "intake"
        i = STAGES.index(cur)
        nxt = STAGES[min(i + 1, len(STAGES) - 1)]
        st["stage"] = nxt
        st["status"] = "advanced"
        if cur == "evolution_ledger" or nxt == "evolution_ledger":
            ledger = list(st.get("ledger") or [])
            ledger.append({"note": note or "checkpoint", "ts": _now()})
            st["ledger"] = ledger[-64:]
            st["runs"] = int(st.get("runs") or 0) + 1
            st["status"] = "ledger_entry"
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

    if action == "mutate":
        parent = str(req.get("parent") or "skill")[:80]
        variant = str(req.get("variant") or f"{parent}-mut")[:80]
        st["stage"] = "mutation_lab"
        st["last_mutation"] = {"parent": parent, "variant": variant, "ts": _now()}
        st["status"] = "mutated"
        _save(st)
        return {
            **coherence_vitals(),
            "status": "mutated",
            "mutation": st["last_mutation"],
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "ledger":
        decision = str(req.get("decision") or "hold").lower()
        note = str(req.get("note") or "")[:160]
        if decision not in ("hold", "archive", "promote", "compost"):
            decision = "hold"
        entry = {"decision": decision, "note": note, "ts": _now()}
        ledger = list(st.get("ledger") or [])
        ledger.append(entry)
        st["ledger"] = ledger[-64:]
        st["stage"] = "evolution_ledger"
        st["status"] = f"ledger_{decision}"
        st["runs"] = int(st.get("runs") or 0) + 1
        _save(st)
        return {
            **coherence_vitals(),
            "status": st["status"],
            "entry": entry,
            "payload": None,
            "audio": False,
            "surface": "silence",
            "human_review": decision == "promote",
        }

    if action == "caption":
        n = int(st.get("runs") or 0)
        s = st.get("stage") or "intake"
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"skillforge · {s} · runs {n}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "diagram"}), indent=2))
