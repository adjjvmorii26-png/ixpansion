"""Experimental dialect — compressed payloads and delta encoding."""
from typing import Any


def normalize(payload: dict[str, Any]) -> dict[str, Any]:
    return {"_exp": True, **payload}
