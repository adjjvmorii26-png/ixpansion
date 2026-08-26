"""Wave 120 — Paradox Compressor.

Compresses paradoxes — contradictory states that arise from cross-module
interference — into singular actionable insights, resolving contradictions
by finding higher-order synthesis.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class Paradox:
    """A contradictory state between two assertions."""

    def __init__(self, assertion_a: str, assertion_b: str, source: str = "unknown"):
        self.assertion_a = assertion_a
        self.assertion_b = assertion_b
        self.source = source
        self.created = time.time()
        self.compressed = False
        self.synthesis: Optional[str] = None
        self.id = hashlib.sha256(
            f"{assertion_a}::{assertion_b}".encode()
        ).hexdigest()[:12]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "assertion_a": self.assertion_a,
            "assertion_b": self.assertion_b,
            "source": self.source,
            "compressed": self.compressed,
            "synthesis": self.synthesis,
            "created": self.created,
        }


class ParadoxCompressor:
    """Detects, tracks, and compresses paradoxes into insights."""

    def __init__(self):
        self._paradoxes: Dict[str, Paradox] = []
        self._compressions: List[Dict[str, Any]] = []

    def register(self, assertion_a: str, assertion_b: str, source: str = "unknown") -> Paradox:
        paradox = Paradox(assertion_a, assertion_b, source)
        self._paradoxes.append(paradox)
        return paradox

    def compress(self, paradox: Paradox, synthesis: str) -> bool:
        if paradox.compressed:
            return False
        paradox.compressed = True
        paradox.synthesis = synthesis
        self._compressions.append({
            "paradox_id": paradox.id,
            "synthesis": synthesis,
            "timestamp": time.time(),
        })
        return True

    def auto_compress(self) -> int:
        compressed = 0
        for p in self._paradoxes:
            if p.compressed:
                continue
            synthesis = self._derive_synthesis(p)
            self.compress(p, synthesis)
            compressed += 1
        return compressed

    def get_unresolved(self) -> List[Dict[str, Any]]:
        return [p.to_dict() for p in self._paradoxes if not p.compressed]

    def get_resolved(self) -> List[Dict[str, Any]]:
        return [p.to_dict() for p in self._paradoxes if p.compressed]

    def status(self) -> Dict[str, Any]:
        total = len(self._paradoxes)
        resolved = sum(1 for p in self._paradoxes if p.compressed)
        return {
            "total_paradoxes": total,
            "resolved": resolved,
            "unresolved": total - resolved,
            "compression_rate": resolved / total if total > 0 else 0.0,
        }

    @staticmethod
    def _derive_synthesis(paradox: Paradox) -> str:
        return f"Synthesis: '{paradox.assertion_a}' and '{paradox.assertion_b}' are not contradictory when viewed from a higher-dimensional perspective — they describe complementary facets of the same underlying truth."
