import struct
from typing import Any

from core.utils.error_handling import ProtocolError

MAGIC = 0x4E58  # "NX"


def decode(raw: bytes) -> dict[str, Any]:
    """Decode a binary hex-protocol frame back into a dict."""
    if len(raw) < 7:
        raise ProtocolError("Frame too short")

    magic, version, payload_len = struct.unpack("!HBI", raw[:7])
    if magic != MAGIC:
        raise ProtocolError(f"Invalid magic: {hex(magic)}")
    if len(raw) < 7 + payload_len:
        raise ProtocolError(f"Payload truncated: expected {payload_len}, got {len(raw) - 7}")

    body = raw[7:7 + payload_len].decode("utf-8")
    from ..serialization.json_codec import loads
    return loads(body)
