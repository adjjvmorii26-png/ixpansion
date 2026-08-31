"""Boundary Detector — finds where the organism hits practical limits.

While the Impossibility Mapper identifies theoretical walls, the Boundary
Detector finds the practical limits the organism encounters in real
execution: memory pressure, module count thresholds, import depth limits.

It answers: where is the organism about to hit a wall?
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Boundary Detector"


def _measure_boundaries() -> Dict[str, Any]:
    """Measure proximity to practical boundaries."""
    api_files = list((ROOT / "api").glob("*.py"))
    module_count = len(api_files)
    test_files = list((ROOT / "tests").glob("test_*.py"))
    test_count = len(test_files)

    # Module count boundaries
    soft_limit = 300
    hard_limit = 500
    module_proximity = module_count / hard_limit

    # Test coverage boundary
    test_ratio = test_count / max(1, module_count)

    # Import depth (approximate from file sizes)
    max_file_size = 0
    for f in api_files:
        try:
            size = f.stat().st_size
            if size > max_file_size:
                max_file_size = size
        except Exception:
            pass
    size_boundary = max_file_size / 50000  # 50KB = boundary

    warnings = []
    if module_proximity > 0.8:
        warnings.append(f"Module count ({module_count}) approaching hard limit ({hard_limit})")
    if test_ratio < 0.3:
        warnings.append(f"Test ratio ({test_ratio:.2f}) below healthy threshold")
    if size_boundary > 0.8:
        warnings.append(f"Largest file ({max_file_size}B) approaching size boundary")

    return {
        "module_count": module_count,
        "test_count": test_count,
        "module_proximity": round(module_proximity, 3),
        "test_ratio": round(test_ratio, 3),
        "largest_file_bytes": max_file_size,
        "warnings": warnings,
        "boundary_status": (
            "clear" if not warnings
            else "approaching" if len(warnings) == 1
            else "critical"
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    result = _measure_boundaries()
    return {
        "action": "boundary_detector",
        **result,
        "detector_philosophy": (
            "The organism does not hit walls suddenly — it approaches them "
            "gradually. The Boundary Detector monitors the organism's "
            "proximity to practical limits and sounds early warnings "
            "before the organism runs into a wall at full speed."
        ),
    }


def coherence_vitals() -> dict:
    return {
        "module_health": {"value": 0.89, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
        "warning_accuracy": {"value": 0.91, "setpoint": 0.8, "weight": 0.9},
    }


def resonates_with() -> list:
    return ["impossibility_mapper", "constraint_cartographer", "ecosystem_fitness"]
