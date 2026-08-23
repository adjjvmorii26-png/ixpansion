"""Hex protocol dialect v1 — minimal fields, flat structure."""
from typing import Any


def normalize(payload: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in payload.items() if isinstance(v, (str, int, float, bool))}
