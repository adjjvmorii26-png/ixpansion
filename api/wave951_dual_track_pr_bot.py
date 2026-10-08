"""Wave 951 — Dual-Track PR Bot.

Lab gates are not full ALEPH CI. Classify a pull request so experiment
noise cannot be mistaken for an organism failure. Silence is the product
surface: this organ emits no audio.
"""
from __future__ import annotations

from typing import Any, Dict, List

LAB_PREFIXES = ("lab/", "experiment/", "hardening/")
ALEPH_MARKERS = ("api_server.py", "Dockerfile", ".github/workflows/")


def classify(pull: Dict[str, Any] | None = None) -> Dict[str, Any]:
    pull = pull or {}
    title = str(pull.get("title") or "")
    branch = str(pull.get("head") or pull.get("branch") or "")
    files = [str(f) for f in (pull.get("files") or [])]
    lab_branch = branch.startswith(LAB_PREFIXES) or title.lower().startswith("experiment:")
    touches_aleph = any(any(f.startswith(m) or f == m for m in ALEPH_MARKERS) for f in files)
    track = "dual" if lab_branch and touches_aleph else ("lab" if lab_branch else "aleph")
    return {
        "wave": 951,
        "track": track,
        "merge_gate": "lab" if track == "lab" else "organism",
        "audio": None,
        "do_not_merge": title.lower().startswith("experiment:") or bool(pull.get("do_not_merge")),
        "interpretation": "lab_gates_are_not_full_aleph_ci",
    }


def handler(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    action = payload.get("action", "status")
    if action == "classify":
        return classify(payload.get("pull") or payload)
    if action == "status":
        return {"wave": 951, "name": "dual_track_pr_bot", "status": "experimental", "audio": None}
    return {"error": "unknown action", "available": ["status", "classify"]}


def coherence_vitals() -> dict:
    return {"layer": "experimental", "status": "active", "wave": "951", "module": "dual_track_pr_bot", "audio": None}


def resonates_with() -> list:
    return ["wave686_dual_track_sentinel", "wave950_hush_margin"]
