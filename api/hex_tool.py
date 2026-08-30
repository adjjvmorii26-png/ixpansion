"""HEX Protocol Tool — encode/decode between HEX dialect and human-readable formats.

The HEX protocol is IXpansion's internal language for inter-agent communication.
This endpoint lets external users translate and inspect HEX messages.

Usage:
  POST /api/hex_tool
  {
    "action": "encode",           // "encode" or "decode"
    "input": "hello world"       // text to encode or HEX to decode
  }

  GET /api/hex_tool?dialect=v1   // show dialect specification
  GET /api/hex_tool?help=1       // show all actions
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from typing import Any, Dict, List


# HEX alphabet: maps characters to nibble pairs
HEX_ALPHABET = "0123456789abcdef"

DIALECT_INFO = {
    "v1": {
        "name": "HEX v1 — Foundation",
        "opcodes": {"ping": "00", "pong": "01", "data": "02", "ack": "03", "err": "04"},
        "description": "Base protocol for inter-agent communication. 4-bit opcodes, variable payload.",
        "max_payload": 255,
        "features": ["basic messaging", "acknowledgments", "error reporting"],
    },
    "v2": {
        "name": "HEX v2 — Expansion",
        "opcodes": {"spawn": "05", "merge": "06", "split": "07", "observe": "08", "dream": "09"},
        "description": "Extended protocol for agent lifecycle and consciousness events.",
        "max_payload": 1024,
        "features": ["agent lifecycle", "consciousness events", "entropy budgets"],
    },
    "experimental": {
        "name": "HEX Experimental — Chaos",
        "opcodes": {"glitch": "0A", "paradox": "0B", "metamorph": "0C", "invoke": "0D", "echo": "0E"},
        "description": "Unstable protocol for paradox resolution and metamorphosis.",
        "max_payload": 4096,
        "features": ["paradox handling", "metamorphosis", "chaos injection"],
    },
}


def _text_to_hex(text: str) -> str:
    """Encode text to HEX representation."""
    return text.encode("utf-8").hex()


def _hex_to_text(hex_str: str) -> str:
    """Decode HEX representation to text."""
    clean = hex_str.replace(" ", "").replace("\n", "")
    if not all(c in HEX_ALPHABET for c in clean.lower()):
        raise ValueError(f"Invalid hex: contains non-hex characters")
    if len(clean) % 2 != 0:
        raise ValueError("Invalid hex: odd number of characters")
    return bytes.fromhex(clean).decode("utf-8", errors="replace")


def _make_hex_message(opcode: str, payload: str, dialect: str = "v1") -> str:
    """Create a formatted HEX message with opcode header."""
    dialect_info = DIALECT_INFO.get(dialect, DIALECT_INFO["v1"])
    opcodes = dialect_info.get("opcodes", {})
    op_hex = opcodes.get(opcode, "FF")
    payload_hex = _text_to_hex(payload)
    length = len(payload_hex) // 2
    header = f"{op_hex}{length:04X}"
    return header + payload_hex


def _parse_hex_message(hex_msg: str) -> Dict[str, Any]:
    """Parse a HEX message into its components."""
    clean = hex_msg.replace(" ", "").replace("\n", "").replace("0x", "")
    if len(clean) < 8:
        return {"error": "message too short (need at least 4 bytes: opcode + length)"}

    opcode = clean[:2]
    length = int(clean[2:6], 16)
    payload_hex = clean[6:6 + length * 2]

    # Find which dialect this opcode belongs to
    found_dialect = None
    for name, info in DIALECT_INFO.items():
        for op_name, op_hex in info["opcodes"].items():
            if op_hex == opcode:
                found_dialect = {"dialect": name, "opcode_name": op_name}
                break

    try:
        payload_text = bytes.fromhex(payload_hex).decode("utf-8", errors="replace")
    except Exception:
        payload_text = "(binary data)"

    return {
        "opcode": f"0x{opcode}",
        "length": length,
        "payload_hex": payload_hex,
        "payload_text": payload_text,
        "dialect": found_dialect,
        "raw": hex_msg,
    }


def _intent_fingerprint(text: str) -> str:
    """Generate a unique HEX fingerprint for text intent."""
    sha = hashlib.sha256(text.encode()).hexdigest()
    # Take first 16 hex chars (64-bit fingerprint)
    return sha[:16]


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    action = payload.get("action", "info")
    dialect = payload.get("dialect", "v1")

    if action == "info" or payload.get("help"):
        return {
            "actions": ["encode", "decode", "fingerprint", "parse", "dialects"],
            "description": "HEX Protocol Tool — encode/decode between HEX and human-readable formats",
            "dialects": {name: info["name"] for name, info in DIALECT_INFO.items()},
            "example_encode": {"action": "encode", "input": "hello frontier", "dialect": "v1"},
            "example_decode": {"action": "decode", "input": "02000b68656c6c6f2066726f6e74696572"},
        }

    if action == "encode":
        text = payload.get("input", "")
        opcode = payload.get("opcode", "data")
        hex_text = _make_hex_message(opcode, text, dialect)
        return {
            "action": "encode",
            "input": text,
            "output": hex_text,
            "opcode": opcode,
            "dialect": dialect,
            "length_bytes": len(text.encode("utf-8")),
        }

    if action == "decode":
        hex_input = payload.get("input", "")
        parsed = _parse_hex_message(hex_input)
        return {"action": "decode", **parsed}

    if action == "fingerprint":
        text = payload.get("input", "")
        fp = _intent_fingerprint(text)
        return {
            "action": "fingerprint",
            "input": text,
            "fingerprint": fp,
            "hex_fingerprint": f"0x{fp}",
            "length": len(fp) // 2,
        }

    if action == "parse":
        hex_input = payload.get("input", "")
        parsed = _parse_hex_message(hex_input)
        return {"action": "parse", **parsed}

    if action == "dialects":
        return {"action": "dialects", **DIALECT_INFO}

    return {"error": f"unknown action: {action}", "valid_actions": ["encode", "decode", "fingerprint", "parse", "dialects"]}
