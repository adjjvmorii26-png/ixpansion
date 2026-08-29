"""Wave 134 — Autonomy Dial.

A supervisor-controlled dial that tunes how much the workforce may
decide for itself. At low settings every action requires approval;
at high settings the civilization self-directs within safety rails.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List

LEVELS = ["supervised", "assisted", "semi_autonomous", "autonomous", "self_directing"]


class AutonomyDial:
    """Grants or constrains workforce self-direction."""

    def __init__(self, level: int = 1):
        self.level = max(0, min(len(LEVELS) - 1, level))
        self._overrides: Dict[str, bool] = {}
        self._safety_rails = True

    def set_level(self, level: int) -> str:
        self.level = max(0, min(len(LEVELS) - 1, level))
        return self.current()

    def current(self) -> str:
        return LEVELS[self.level]

    def may_act_alone(self, action: str) -> bool:
        base = self.level >= 2
        if action in self._overrides:
            return self._overrides[action]
        if self.level >= 4 and self._safety_rails:
            return action not in ("rewrite_core", "delete_data")
        return base

    def escalate(self, action: str, allow: bool) -> None:
        self._overrides[action] = allow

    def summary(self) -> Dict[str, Any]:
        return {"level": self.level, "mode": self.current(),
                "overrides": len(self._overrides),
                "safety_rails": self._safety_rails}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    dial = AutonomyDial()
    return {"status": "active", "module": "autonomy_dial",
            **dial.summary()}
