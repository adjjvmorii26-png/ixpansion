import struct
from typing import Any

from core.utils.error_handling import ProtocolError


def encode(payload: dict[str, Any], version: int = 2) -> bytes:
    """Encode a dict into a binary hex-protocol frame.

    Frame layout:
      [magic: 2 bytes][version: 1 byte][payload_len: 4 bytes][payload]
    """
    try:
        body = _serialize(payload)
        header = struct.pack("!HBI", 0x4E58, version, len(body))
        return header + body
    except Exception as exc:
        raise ProtocolError(f"Encode failed: {exc}") from exc


def _serialize(payload: dict[str, Any]) -> bytes:
    from ..serialization.json_codec import dumps
    return dumps(payload).encode("utf-8")
