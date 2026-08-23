from pathlib import Path
from typing import Any

import json


def load(path: str | Path) -> dict[str, Any]:
    with open(path) as f:
        return json.load(f)


def overlay(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    result = base.copy()
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = overlay(result[key], value)
        else:
            result[key] = value
    return result


def resolve(*layers: str | Path) -> dict[str, Any]:
    """Merge multiple JSON config files in order (later wins)."""
    merged: dict[str, Any] = {}
    for path in layers:
        merged = overlay(merged, load(path))
    return merged
