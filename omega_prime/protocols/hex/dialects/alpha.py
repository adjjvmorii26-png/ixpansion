from typing import Any


def normalize(payload: dict[str, Any]) -> dict[str, Any]:
    """Dialect α: strip non-primitive values."""
    return {k: v for k, v in payload.items() if isinstance(v, (str, int, float, bool))}
