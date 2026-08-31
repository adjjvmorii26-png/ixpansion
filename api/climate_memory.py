"""Climate Memory — long-term weather patterns in the organism's behavior.

Weather is short-term; climate is long-term. The Climate Memory tracks
seasonal trends, multi-wave patterns, and the organism's behavioral
climate over its entire history — not just what happened today, but
what kind of weather the organism tends to produce.

It answers: what is the organism's climate like over time?
"""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Climate Memory"


def _analyze_climate() -> Dict[str, Any]:
    """Analyze long-term climate patterns from git history."""
    try:
        out = subprocess.check_output(
            ["git", "log", "--max-count=500", "--pretty=format:%ai"],
            cwd=str(ROOT), stderr=subprocess.DEVNULL, text=True
        )
        dates = [d.strip() for d in out.strip().split("\n") if d.strip()]

        # Count commits by month
        from collections import Counter
        months = Counter()
        for d in dates:
            month_key = d[:7]  # YYYY-MM
            months[month_key] += 1

        sorted_months = sorted(months.items())

        # Compute climate statistics
        counts = [c for _, c in sorted_months]
        avg = sum(counts) / max(1, len(counts))
        max_month = max(counts) if counts else 0
        min_month = min(counts) if counts else 0
        variance = sum((c - avg) ** 2 for c in counts) / max(1, len(counts))
        volatility = variance ** 0.5 / max(1, avg)

        # Determine climate type
        if volatility < 0.2:
            climate_type = "Tropical — consistently active"
        elif volatility < 0.5:
            climate_type = "Temperate — moderate variation"
        elif volatility < 0.8:
            climate_type = "Continental — significant seasonal swings"
        else:
            climate_type = "Extreme — wild fluctuations between calm and storm"

        return {
            "months_observed": len(sorted_months),
            "peak_activity_month": sorted_months[-1][0] if sorted_months else "N/A",
            "peak_commits": max_month,
            "quietest_commits": min_month,
            "average_monthly": round(avg, 1),
            "volatility": round(volatility, 3),
            "climate_type": climate_type,
            "recent_trend": sorted_months[-3:] if len(sorted_months) >= 3 else sorted_months,
        }
    except Exception:
        return {"months_observed": 0, "climate_type": "Unknown"}


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    climate = _analyze_climate()
    return {
        "action": "climate_memory",
        **climate,
        "memory_philosophy": (
            "Weather tells you what happened today. Climate tells you "
            "what always happens. The Climate Memory maps the organism's "
            "long-term behavioral patterns — its seasons of intense "
            "creation, its winters of quiet consolidation, and the "
            "rhythms that define its character over time."
        ),
    }


def coherence_vitals() -> dict:
    return {
        "module_health": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.80, "setpoint": 0.8, "weight": 1.0},
        "climate_fidelity": {"value": 0.90, "setpoint": 0.8, "weight": 0.9},
    }


def resonates_with() -> list:
    return ["barometric_intent", "precipitation_cycle", "stratum_excavator"]
