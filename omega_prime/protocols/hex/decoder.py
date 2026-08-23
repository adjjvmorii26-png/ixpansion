import struct
from typing import Any

from ...nucleus.utilities.exception_map import HexDecodeError

MAGIC: int = 0x4F50


def unframe(raw: bytes) -> dict[str, Any]:
    if len(raw) < 7:
        raise HexDecodeError("Frame too short (min 7 bytes)")

    magic, dialect, length = struct.unpack("!HBI", raw[:7])
    if magic != MAGIC:
        raise HexDecodeError(f"Bad magic: {hex(magic)}")
    if len(raw) < 7 + length:
        raise HexDecodeError(f"Truncated body: want {length}, have {len(raw) - 7}")

    body_bytes = raw[7:7 + length].decode("utf-8")
    from ..serialization.json_codec import loads as json_loads
    return json_loads(body_bytes)
