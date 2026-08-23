from typing import Any


def normalize_for(dialect: int, payload: dict[str, Any]) -> dict[str, Any]:
    if dialect == 1:
        from .alpha import normalize
    elif dialect == 2:
        from .delta import normalize
    else:
        from .omega import normalize
    return normalize(payload)
