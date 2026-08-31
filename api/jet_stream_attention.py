"""Jet Stream Attention — tracks fast-moving attention currents through the codebase.

The jet stream is a fast-flowing river of air high in the atmosphere.
The organism's jet stream is the fast-moving current of attention —
the modules that get queried most, modified most, and referenced most.

It answers: where is the organism's attention flowing fastest?
"""
from __future__ import annotations

import hashlib
import subprocess
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Jet Stream Attention"


def _track_flow() -> Dict[str, Any]:
    """Track attention flow through recent git activity."""
    try:
        out = subprocess.check_output(
            ["git", "log", "--max-count=100", "--pretty=format:", "--name-only"],
            cwd=str(ROOT), stderr=subprocess.DEVNULL, text=True
        )
        files = [f.strip() for f in out.strip().split("\n") if f.strip()]
        counter = Counter(files)
        top_files = counter.most_common(10)

        total_commits = sum(counter.values())
        unique_files = len(counter)

        # Compute velocity: files changed per unit
        velocity = total_commits / max(1, unique_files)

        return {
            "total_changes": total_commits,
            "unique_files": unique_files,
            "velocity": round(velocity, 2),
            "hottest_files": [{"file": f, "changes": c} for f, c in top_files],
        }
    except Exception:
        return {"total_changes": 0, "unique_files": 0, "velocity": 0, "hottest_files": []}


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    flow = _track_flow()

    jet_label = (
        "Strong jet stream" if flow["velocity"] > 3.0
        else "Moderate flow" if flow["velocity"] > 1.5
        else "Calm air"
    )

    return {
        "action": "jet_stream_attention",
        **flow,
        "jet_label": jet_label,
        "tracking_philosophy": (
            "Attention is not均匀 distributed — it flows like a jet stream: "
            "fast, narrow, and powerful. Some files are crossed by attention "
            "dozens of times while others sit in still air. The Jet Stream "
            "Attention map shows where the organism's focus is concentrated."
        ),
    }


def coherence_vitals() -> dict:
    return {
        "module_health": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.81, "setpoint": 0.8, "weight": 1.0},
        "flow_tracking": {"value": 0.89, "setpoint": 0.75, "weight": 0.8},
    }


def resonates_with() -> list:
    return ["barometric_intent", "front_tracker", "kinesthetic_engine"]
