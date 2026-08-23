"""ID generation with optional HEX encoding."""
from __future__ import annotations

import uuid
import time

from .hex_codec import encode


def generate_id(prefix: str = "", hex_encode: bool = False) -> str:
    raw = f"{prefix}_{uuid.uuid4().hex[:12]}_{int(time.time())}"
    return encode(raw) if hex_encode else raw


def short_id(length: int = 8) -> str:
    return uuid.uuid4().hex[:length]
