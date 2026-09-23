"""Wave 814 — lineage_null_fuse.

Fuse null_evidence_registry with a lightweight lineage edge list so
failed hypotheses stay attached to their parent question/wave id.

Pairs with open experiment PRs 905 lineage graph / 904 evidence ledger
without depending on them.

Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave814_lineage_null_fuse.json"
WAVE = 814
NAME = "lineage_null_fuse"

DEFAULT = {"wave": WAVE, "name": NAME, "edges": [], "fuses": 0, "status": "idle"}


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
        "module": "wave814_lineage_null_fuse",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "fuses": int(st.get("fuses") or 0),
        "edges": len(st.get("edges") or []),
        "resonance": round(min(1.0, 0.5 + int(st.get("fuses") or 0) * 0.02), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave813_null_evidence_registry",
        "wave812_experiment_queue_atlas",
        "wave810_question_triad",
        "wave808_discovery_cycle_engine",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {
            **coherence_vitals(),
            "edges_tail": (st.get("edges") or [])[-5:],
            "audio": False,
            "surface": "silence",
        }

    if action == "fuse":
        parent = str(req.get("parent") or req.get("question") or "unknown")[:120]
        hyp = str(req.get("hypothesis") or "")[:200]
        note = str(req.get("note") or "null")[:200]
        try:
            reg = _import_api("wave813_null_evidence_registry")
            reg.handler({"action": "record", "hypothesis": hyp or parent, "note": note})
            null_ok = True
        except Exception:
            null_ok = False
        edge = {"parent": parent, "hypothesis": hyp, "kind": "null", "ts": _now()}
        edges = list(st.get("edges") or [])
        edges.append(edge)
        st["edges"] = edges[-64:]
        st["fuses"] = int(st.get("fuses") or 0) + 1
        st["status"] = "fused"
        _save(st)
        return {
            **coherence_vitals(),
            "status": "fused",
            "null_ok": null_ok,
            "edge": edge,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("fuses") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"lineage-null fuses {n}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "fuse", "parent": "q1", "hypothesis": "h", "note": "no effect"}), indent=2))
