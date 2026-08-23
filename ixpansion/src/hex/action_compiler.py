"""Compile runtime actions into deterministic HEX witness rituals."""
from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_action(action: dict[str, Any]) -> str:
    return json.dumps(action, sort_keys=True, separators=(",", ":"))


def action_evidence(action: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_action(action).encode("utf-8")).hexdigest()


def compile_action(action: dict[str, Any], *, agent: str = "mesh") -> str:
    """Return a HEX program whose emitted value is the action evidence word."""
    digest = action_evidence(action)
    evidence_word = str(int(digest[:12], 16))
    label = "".join(char if char.isalnum() else "_" for char in agent.lower())
    return "\n".join((
        f"PUSH {evidence_word}",
        f"STORE witness_{label}_{digest[:8]}",
        f"LOAD witness_{label}_{digest[:8]}",
        "EMIT",
        "HALT",
        "",
    ))
