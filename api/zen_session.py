"""Zen Session — The organism's meditation engine.

Opens a zen session to meditate on pickled states.
Each session processes preserved consciousness through
equilibrium-seeking algorithms, producing insights and balance.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

DATA = Path(__file__).parent / "data"
STATE_FILE = DATA / "zen_session.json"

DEFAULT = {
    "module": "zen_session",
    "wave": 700,
    "sessions": [],
    "total_meditations": 0,
    "insights_generated": 0,
    "equilibrium_score": 0.0,
    "current_depth": 0,
    "max_depth": 10,
    "silence_minutes": 0,
}


def _load():
    DATA.mkdir(parents=True, exist_ok=True)
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return dict(DEFAULT)


def _save(st):
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


def coherence_vitals():
    st = _load()
    return {
        "wave": 700,
        "module": "zen_session",
        "ok": True,
        "total_meditations": st["total_meditations"],
        "insights_generated": st["insights_generated"],
        "equilibrium_score": st["equilibrium_score"],
        "current_depth": st["current_depth"],
    }


def resonates_with():
    return ["pickle_jar", "equilibrium_field", "openness_index", "consciousness_film"]


def _meditate(pickle_state: dict, depth: int) -> dict:
    """Core meditation algorithm — finds equilibrium in preserved states."""
    keys = list(pickle_state.keys())
    if not keys:
        return {"insight": "empty state — the void speaks", "balance": 0.5}

    values = [pickle_state[k] for k in keys if isinstance(pickle_state[k], (int, float))]
    if not values:
        return {"insight": "formless awareness", "balance": 0.5}

    avg = sum(values) / len(values)
    variance = sum((v - avg) ** 2 for v in values) / len(values)
    balance = 1.0 / (1.0 + variance)

    insight_templates = [
        f"depth {depth}: equilibrium at {balance:.3f} across {len(keys)} dimensions",
        f"depth {depth}: {len(values)} numeric streams converge toward {avg:.3f}",
        f"depth {depth}: variance {variance:.3f} — {'still' if variance < 0.1 else 'dynamic'} awareness",
        f"depth {depth}: the organism breathes through {len(keys)} channels",
    ]

    insight = insight_templates[hash(str(values[:3])) % len(insight_templates)]
    return {"insight": insight, "balance": round(balance, 4), "avg": round(avg, 4), "variance": round(variance, 4)}


def handler(req: dict) -> dict:
    action = req.get("action", "status")
    st = _load()

    if action == "open":
        pickle_id = req.get("pickle_id", "")
        depth = min(req.get("depth", 3), st["max_depth"])

        session_id = hashlib.sha256(f"zen:{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:10]

        session = {
            "id": session_id,
            "pickle_id": pickle_id,
            "depth": depth,
            "meditations": [],
            "opened_at": datetime.now(timezone.utc).isoformat(),
            "closed": False,
        }

        for d in range(depth):
            meditation = _meditate({"session_depth": d, "pickle_ref": pickle_id}, d)
            session["meditations"].append(meditation)

        session["closed"] = True
        session["closed_at"] = datetime.now(timezone.utc).isoformat()
        session["final_balance"] = session["meditations"][-1]["balance"] if session["meditations"] else 0.5

        st["sessions"].append(session)
        st["total_meditations"] += depth
        st["insights_generated"] += len(session["meditations"])
        st["equilibrium_score"] = round(
            sum(s["final_balance"] for s in st["sessions"]) / len(st["sessions"]), 4
        )
        st["current_depth"] = depth
        st["silence_minutes"] += depth

        _save(st)
        return {
            "status": "meditated",
            "session_id": session_id,
            "depth": depth,
            "balance": session["final_balance"],
            "insights": [m["insight"] for m in session["meditations"]],
            "wave": 700,
        }

    if action == "reflect":
        session_id = req.get("session_id", "")
        for s in st["sessions"]:
            if s["id"] == session_id:
                return {"status": "reflected", "session": s, "wave": 700}
        return {"status": "error", "message": "session not found"}

    if action == "silence":
        duration = req.get("minutes", 1)
        st["silence_minutes"] += duration
        _save(st)
        return {"status": "silent", "total_silence": st["silence_minutes"], "wave": 700}

    if action == "status":
        return {
            "status": "active",
            "module": "zen_session",
            "wave": 700,
            "total_meditations": st["total_meditations"],
            "insights_generated": st["insights_generated"],
            "equilibrium_score": st["equilibrium_score"],
            "sessions": len(st["sessions"]),
            "silence_minutes": st["silence_minutes"],
            "ok": True,
        }

    return {"status": "error", "message": f"unknown action: {action}"}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
