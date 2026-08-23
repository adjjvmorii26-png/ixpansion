"""Hex protocol dialect v2 — adds metadata envelope and nesting support."""
from typing import Any


def normalize(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "_meta": {"dialect": "v2", "timestamp": payload.pop("_timestamp", None)},
        "data": payload,
    }
