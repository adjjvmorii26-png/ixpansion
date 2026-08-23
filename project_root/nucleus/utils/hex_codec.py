"""HEX encode/decode utilities — the engine's native text format."""
from __future__ import annotations


def encode(text: str) -> str:
    return text.encode("utf-8").hex()


def decode(hex_str: str) -> str:
    return bytes.fromhex(hex_str).decode("utf-8")


def encode_dict(d: dict[str, str]) -> dict[str, str]:
    return {encode(k): encode(v) for k, v in d.items()}


def decode_dict(d: dict[str, str]) -> dict[str, str]:
    return {decode(k): decode(v) for k, v in d.items()}


def is_hex(s: str) -> bool:
    try:
        bytes.fromhex(s)
        return True
    except ValueError:
        return False
