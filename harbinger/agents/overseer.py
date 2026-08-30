"""Overseer — the agent that decides what the frontier does next.

Weighs the scout's evidence against a library of evolution moves
(new module, new test, documentation repair, cleanup, or full wave),
and returns a concrete proposal the conclave can execute.
"""
from __future__ import annotations

from typing import Any, Dict, List

_MOVES = {
    "repair": {
        "trigger": lambda s: s.get("broken_refs") or s.get("dirty", 0) > 8 or (s.get("health") or {}).get("status") != "healthy",
        "title": "Repair & align the frontier",
        "work": ["fix broken README references", "borrow the scout's dirty-file list and address it",
                 "re-run the full suite to prove stability"],
    },
    "module": {
        "trigger": lambda s: False,  # gated by an explicit idea below
        "title": "Grow a new module",
        "work": ["invent a small, useful api/ module with tests", "register it (counts auto-follow)",
                 "bump wave/version and document it"],
    },
    "cleanup": {
        "trigger": lambda s: False,
        "title": "Tend the undergrowth",
        "work": ["remove stale artifacts", "consolidate duplicate doc dirs",
                 "refresh the architecture map"],
    },
    "garden": {
        "trigger": lambda s: False,
        "title": "Plant a garden seed",
        "work": ["grow one organism through HORTUS HEXIS (words -> module -> gate -> commit)",
                 "cross it with a sibling if a fresh hybrid is warranted"],
    },
    "lean": {
        "trigger": lambda s: int(s.get("modules", 0) or 0) == 0,
        "title": "Reignite the core",
        "work": ["restore api/ health", "verify vercel build", "run full suite"],
    },
}


class Overseer:
    """Chooses the next evolution move from scout evidence."""

    def __init__(self, ideas: List[str] = None):
        self.ideas = ideas or []

    def propose(self, scout: Dict[str, Any]) -> Dict[str, Any]:
        for reason, move in _MOVES.items():
            try:
                if move["trigger"](scout):
                    return {"reason": reason, "title": move["title"], "work": move["work"]}
            except Exception:
                continue
        if self.ideas:
            idea = self.ideas[0]
            return {"reason": "idea", "title": idea, "work": [idea, "add tests", "commit cleanly"]}
        if scout.get("tests", 0) < 900:
            return {"reason": "fortify", "title": "Fortify the test lattice",
                    "work": ["add regression tests for the newest modules", "raise the floor"]}
        return {"reason": "rest", "title": "The frontier is stable",
                "work": ["no urgent move — allow the chronicler to close the archive",
                         "optionally plant a garden seed for ceremony"]}


def run(scout: Dict[str, Any], ideas: List[str] = None) -> Dict[str, Any]:
    return {"agent": "overseer", "proposal": Overseer(ideas).propose(scout)}
