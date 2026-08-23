import struct
from typing import Any

from ...nucleus.utilities.exception_map import HexEncodeError

MAGIC: int = 0x4F50  # "OP"
SUPPORTED_DIALECTS = {1, 2, 3}


def frame(payload: dict[str, Any], dialect: int = 2) -> bytes:
    """Encode payload into a binary OP-protocol frame.

    Layout: [magic:u16][dialect:u8][length:u32][body]
    """
    if dialect not in SUPPORTED_DIALECTS:
        raise HexEncodeError(f"Unsupported dialect: {dialect}")

    from ..serialization.json_codec import dumps as json_dumps
    from .dialects import normalize_for

    normalized = normalize_for(dialect, payload)
    body = json_dumps(normalized).encode("utf-8")
    header = struct.pack("!HBI", MAGIC, dialect, len(body))
    return header + body
