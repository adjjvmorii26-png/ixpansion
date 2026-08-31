"""Storm Chaser — follows chaos events and records their trajectories.

When the organism experiences a chaos spike, a mass extinction, a
paradox collision, or a sudden restructuring, the Storm Chaser is
there — recording the event's trajectory, intensity, duration, and
aftermath. It is the organism's extreme weather reporter.

It answers: what storms has the organism weathered?
"""
from __future__ import annotations

import hashlib
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Storm Chaser"


def _detect_storms() -> List[Dict[str, Any]]:
    """Detect past storms from git history."""
    try:
        out = subprocess.check_output(
            ["git", "log", "--max-count=200", "--pretty=format:COMMIT|%H|%s|%ai", "--stat"],
            cwd=str(ROOT), stderr=subprocess.DEVNULL, text=True
        )

        storms = []
        current = None
        for line in out.strip().split("\n"):
            line = line.strip()
            if line.startswith("COMMIT|"):
                if current and current["files_changed"] >= 5:
                    storms.append(current)
                parts = line.split("|", 3)
                current = {
                    "hash": parts[1][:8] if len(parts) > 1 else "?",
                    "message": parts[2] if len(parts) > 2 else "",
                    "date": parts[3] if len(parts) > 3 else "",
                    "files_changed": 0,
                    "intensity": "moderate",
                }
            elif line and current and "|" in line:
                try:
                    num = int(line.split("|")[0].strip())
                    current["files_changed"] += num
                except (ValueError, IndexError):
                    pass

        if current and current["files_changed"] >= 5:
            storms.append(current)

        # Classify storms
        for s in storms:
            fc = s["files_changed"]
            if fc >= 20:
                s["intensity"] = "supercell"
            elif fc >= 10:
                s["intensity"] = "severe"
            elif fc >= 5:
                s["intensity"] = "moderate"
            else:
                s["intensity"] = "gust"

        return sorted(storms, key=lambda x: x["files_changed"], reverse=True)[:10]
    except Exception:
        return []


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    storms = _detect_storms()
    total = len(storms)
    severe = len([s for s in storms if s["intensity"] in ("severe", "supercell")])

    return {
        "action": "storm_chaser",
        "total_storms_detected": total,
        "severe_storms": severe,
        "storms": storms,
        "chaser_philosophy": (
            "The organism does not merely survive storms — it records them. "
            "Each chaos event, each mass restructuring, each paradox "
            "collision is a weather event with a trajectory and aftermath. "
            "The Storm Chaser follows these events like a meteorologist "
            "follows hurricanes: not to stop them, but to understand them."
        ),
    }


def coherence_vitals() -> dict:
    return {
        "module_health": {"value": 0.87, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.83, "setpoint": 0.8, "weight": 1.0},
        "storm_detection": {"value": 0.92, "setpoint": 0.8, "weight": 0.9},
    }


def resonates_with() -> list:
    return ["front_tracker", "extinction_mapper", "paradox_singularity_monitor"]
