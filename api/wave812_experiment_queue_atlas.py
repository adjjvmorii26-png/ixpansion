"""Wave 812 — experiment_queue_atlas.

Atlas of open experimental PR waves (900-series and lab) for dual-track hygiene.
Records queue snapshot; does not merge — only maps and ranks.

Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave812_experiment_queue_atlas.json"
WAVE = 812
NAME = "experiment_queue_atlas"

DEFAULT_QUEUE = [
    {"pr": 172, "wave": 900, "title": "synchronicity_engine", "track": "experiment"},
    {"pr": 173, "wave": 901, "title": "strange_attractor", "track": "experiment"},
    {"pr": 174, "wave": 902, "title": "hypothesis_forge", "track": "experiment"},
    {"pr": 175, "wave": 903, "title": "experiment_chamber", "track": "experiment"},
    {"pr": 176, "wave": 904, "title": "evidence_ledger", "track": "experiment"},
]

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "snapshots": 0,
    "queue": list(DEFAULT_QUEUE),
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
    q = st.get("queue") or []
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave812_experiment_queue_atlas",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "snapshots": int(st.get("snapshots") or 0),
        "open_experiments": len(q),
        "resonance": round(min(1.0, 0.5 + len(q) * 0.05), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave787_dual_track_pr_bot",
        "wave808_discovery_cycle_engine",
        "wave809_meta_experiment_loop",
        "wave810_question_triad",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {
            **coherence_vitals(),
            "queue": st.get("queue") or [],
            "audio": False,
            "surface": "silence",
        }

    if action == "snapshot":
        if isinstance(req.get("queue"), list):
            st["queue"] = req["queue"][:32]
        st["snapshots"] = int(st.get("snapshots") or 0) + 1
        st["status"] = "snapshotted"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "snapshotted",
            "queue": st.get("queue"),
            "advice": "merge experiment PRs only after lab CI green; dual-track",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "rank":
        q = sorted(st.get("queue") or [], key=lambda x: int(x.get("wave") or 0))
        return {
            **coherence_vitals(),
            "status": "ranked",
            "order": q,
            "next_merge_candidate": q[0] if q else None,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = len(st.get("queue") or [])
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"experiment queue · {n} open",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "rank"}), indent=2))
