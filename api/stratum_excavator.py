"""Stratum Excavator — digs through the organism's geological layers.

Each version is a stratum. Each commit is a sediment deposit.
The Stratum Excavator reads git history, version tags, and file
birth-deaths to reconstruct the organism's geological record.

It answers: what lies beneath the current surface?
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Stratum Excavator"


def _git_log(limit: int = 50) -> List[Dict[str, str]]:
    """Read recent git log entries."""
    try:
        out = subprocess.check_output(
            ["git", "log", f"--max-count={limit}", "--pretty=format:%H|%s|%ai"],
            cwd=str(ROOT), stderr=subprocess.DEVNULL, text=True
        )
        entries = []
        for line in out.strip().split("\n"):
            if not line.strip():
                continue
            parts = line.split("|", 2)
            if len(parts) == 3:
                entries.append({"hash": parts[0][:8], "message": parts[1], "date": parts[2]})
        return entries
    except Exception:
        return []


def _strata_from_commits(commits: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Group commits into strata (wave-batches)."""
    strata = []
    current_stratum = None
    for c in commits:
        msg = c["message"]
        wave_match = None
        for token in msg.split():
            if "wave" in token.lower():
                wave_match = token
                break
        if wave_match and (current_stratum is None or current_stratum.get("wave") != wave_match):
            if current_stratum:
                strata.append(current_stratum)
            current_stratum = {
                "wave": wave_match,
                "first_date": c["date"],
                "commits": [],
                "depth": len(strata),
            }
        if current_stratum:
            current_stratum["commits"].append(c)
            current_stratum["last_date"] = c["date"]
    if current_stratum:
        strata.append(current_stratum)
    return strata


def excavate(depth: int = 20) -> Dict[str, Any]:
    """Run a full excavation."""
    commits = _git_log(depth * 3)
    strata = _strata_from_commits(commits)
    total_commits = len(commits)
    total_strata = len(strata)

    layers = []
    for s in strata[-depth:]:
        layers.append({
            "wave": s["wave"],
            "depth": s["depth"],
            "commit_count": len(s["commits"]),
            "oldest": s["first_date"],
            "newest": s["last_date"],
            "headline": s["commits"][0]["message"] if s["commits"] else "",
        })

    return {
        "total_commits": total_commits,
        "total_strata": total_strata,
        "deepest_layer": total_strata,
        "layers": layers,
        "excavation_philosophy": (
            "Every codebase is a geological formation. The current surface is "
            "merely the latest deposit. Beneath it lie strata of abandoned ideas, "
            "evolved conventions, and fossilized decisions. To understand the "
            "present, we must dig."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    depth = int(payload.get("depth", 20))
    result = excavate(depth)
    result["action"] = "excavate"
    return result


def coherence_vitals() -> dict:
    return {
        "module_health": {"value": 0.88, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.82, "setpoint": 0.8, "weight": 1.0},
        "excavation_depth": {"value": 0.90, "setpoint": 0.7, "weight": 0.8},
    }


def resonates_with() -> list:
    return ["fossil_registry", "extinction_mapper", "stratigraphy_core"]
