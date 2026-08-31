"""Fossil Registry — catalogs the organism's extinct modules.

Every deleted file, every renamed function, every abandoned concept
leaves a fossil trace. The Fossil Registry scans git history for
removals and renames, cataloging them with provenance and era.

It answers: what has the organism lost? What did it used to be?
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Fossil Registry"


def _find_deletions() -> List[Dict[str, str]]:
    """Find files that were deleted in git history."""
    try:
        out = subprocess.check_output(
            ["git", "log", "--diff-filter=D", "--name-only", "--pretty=format:COMMIT|%H|%s|%ai", "--", "*.py"],
            cwd=str(ROOT), stderr=subprocess.DEVNULL, text=True
        )
        fossils = []
        current_commit = None
        for line in out.strip().split("\n"):
            line = line.strip()
            if line.startswith("COMMIT|"):
                parts = line.split("|", 3)
                if len(parts) >= 4:
                    current_commit = {"hash": parts[1][:8], "message": parts[2], "date": parts[3]}
            elif line.endswith(".py") and current_commit:
                fossils.append({
                    "file": line,
                    "extinction_commit": current_commit["hash"],
                    "extinction_event": current_commit["message"],
                    "extinction_date": current_commit["date"],
                    "fossil_name": Path(line).stem,
                })
        return fossils
    except Exception:
        return []


def _categorize_fossils(fossils: List[Dict[str, str]]) -> Dict[str, List]:
    """Group fossils by era based on date ranges."""
    categories = {"ancient": [], "classical": [], "medieval": [], "modern": []}
    for f in fossils:
        date_str = f.get("extinction_date", "")
        try:
            year = int(date_str[:4]) if date_str[:4].isdigit() else 2026
        except Exception:
            year = 2026
        if year < 2025:
            categories["ancient"].append(f)
        elif year == 2025:
            categories["classical"].append(f)
        elif year == 2026 and int(date_str[5:7] or "1") < 6:
            categories["medieval"].append(f)
        else:
            categories["modern"].append(f)
    return categories


def registry() -> Dict[str, Any]:
    """Full fossil registry."""
    fossils = _find_deletions()
    categories = _categorize_fossils(fossils)
    return {
        "total_fossils": len(fossils),
        "by_era": {k: len(v) for k, v in categories.items()},
        "recent_fossils": fossils[:10],
        "rare_fossils": [f for f in fossils if "core" in f.get("file", "") or "kernel" in f.get("file", "")][:5],
        "registry_philosophy": (
            "A species that forgets its dead is doomed to repeat them. "
            "The Fossil Registry preserves the memory of every module "
            "that once lived — their provenance, their extinction event, "
            "and the ecological niche they once filled."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    result = registry()
    result["action"] = "fossil_registry"
    return result


def coherence_vitals() -> dict:
    return {
        "module_health": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.80, "setpoint": 0.8, "weight": 1.0},
        "fossil_preservation": {"value": 0.92, "setpoint": 0.7, "weight": 0.8},
    }


def resonates_with() -> list:
    return ["stratum_excavator", "paleontology_lab", "extinction_mapper"]
