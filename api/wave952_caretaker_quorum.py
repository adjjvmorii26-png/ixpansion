"""Wave 952 — caretaker_quorum.

Daily caretaker posture for open PRs: merge, close, or hold.
Does not mutate GitHub. Silence is the product surface.
Lab organ only. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave952_caretaker_quorum.json"
WAVE = 952
NAME = "caretaker_quorum"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "decisions": 0,
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


def decide(pr: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Return caretaker posture for one PR-shaped dict.

    Expected keys (all optional): title, head, mergeable_state,
    organism_gate (pass|fail|unknown), lab_gate (pass|fail|unknown),
    superseded (bool), track (lab|aleph|dual|security).
    """
    pr = pr or {}
    title = str(pr.get("title") or "").lower()
    head = str(pr.get("head") or pr.get("branch") or "").lower()
    mergeable = str(pr.get("mergeable_state") or "unknown").lower()
    organism = str(pr.get("organism_gate") or "unknown").lower()
    lab = str(pr.get("lab_gate") or "unknown").lower()
    superseded = bool(pr.get("superseded"))
    track = str(pr.get("track") or "").lower()

    if not track:
        if head.startswith("lab/") or title.startswith("lab:"):
            track = "lab"
        elif head.startswith("security/") or title.startswith("security:"):
            track = "security"
        else:
            track = "aleph"

    if superseded or mergeable == "dirty":
        action = "close"
        reason = "superseded_or_conflicted"
    elif track == "lab" and lab == "pass" and organism in {"pass", "unknown"} and mergeable in {"clean", "unstable", "unknown"}:
        action = "merge"
        reason = "lab_green_safe"
    elif track in {"security", "aleph"} and organism == "pass" and mergeable == "clean":
        action = "merge"
        reason = "organism_green_safe"
    elif organism == "fail" or lab == "fail":
        action = "hold"
        reason = "gate_red"
    elif mergeable == "behind":
        action = "hold"
        reason = "behind_main"
    else:
        action = "hold"
        reason = "insufficient_signal"

    return {
        "wave": WAVE,
        "track": track,
        "action": action,
        "reason": reason,
        "audio": None,
        "surface": "silence",
        "interpretation": "lab_gates_are_not_full_aleph_ci",
    }


def coherence_vitals() -> dict:
    st = _load()
    decisions = int(st.get("decisions") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave952_caretaker_quorum",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "decisions": decisions,
        "resonance": round(min(1.0, 0.55 + decisions * 0.01), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave787_dual_track_pr_bot",
        "wave950_hush_margin",
        "wave949_council_witness",
        "wave770_copilot_council_pulse",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "decide":
        out = decide(req.get("pull") or req)
        st["decisions"] = int(st.get("decisions") or 0) + 1
        st["status"] = "decided"
        st["last_action"] = out["action"]
        st["last_ts"] = _now()
        _save(st)
        return {**coherence_vitals(), **out, "status": "decided", "payload": None}

    if action == "quorum":
        pulls = req.get("pulls") or req.get("prs") or []
        if not isinstance(pulls, list):
            pulls = []
        results: List[dict] = [decide(p if isinstance(p, dict) else {}) for p in pulls[:50]]
        counts = {"merge": 0, "close": 0, "hold": 0}
        for r in results:
            counts[r["action"]] = counts.get(r["action"], 0) + 1
        st["decisions"] = int(st.get("decisions") or 0) + len(results)
        st["status"] = "quorum"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "quorum",
            "counts": counts,
            "results": results,
            "audio": False,
            "surface": "silence",
            "payload": None,
        }

    if action == "caption":
        n = int(st.get("decisions") or 0)
        last = st.get("last_action") or "-"
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"caretaker quorum {n} · last {last}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "decide", "title": "lab: example", "head": "lab/x", "lab_gate": "pass"}), indent=2))
