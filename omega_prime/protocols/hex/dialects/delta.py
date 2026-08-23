import time
from typing import Any


def normalize(payload: dict[str, Any]) -> dict[str, Any]:
    """Dialect δ: wrap in metadata envelope with timestamp."""
    return {
        "_hdr": {"d": "δ", "ts": time.time()},
        "body": payload,
    }
