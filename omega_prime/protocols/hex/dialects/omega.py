from typing import Any


def normalize(payload: dict[str, Any]) -> dict[str, Any]:
    """Dialect ω: experimental delta-compression mode."""
    return {"_ω": True, **payload}
