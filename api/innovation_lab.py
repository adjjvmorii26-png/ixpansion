"""Wave 133 — Innovation Lab.

A dedicated space where the workforce runs experiments. Innovations
are triaged by novelty score, executed in isolated pods, and either
promoted into the civilization or archived as learnings.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List


class Innovation:
    """An experimental innovation run by the workforce."""

    def __init__(self, title: str, author: str, novelty: float):
        self.title = title
        self.author = author
        self.novelty = max(0.0, min(1.0, novelty))
        self.status = "queued"
        self.pod_id: str = ""
        self.created = time.time()
        self.id = hashlib.sha256(f"innov:{title}".encode()).hexdigest()[:10]

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "title": self.title, "author": self.author,
                "novelty": self.novelty, "status": self.status, "pod": self.pod_id}


class InnovationLab:
    """Runs and triages workforce experiments."""

    def __init__(self):
        self._innovations: Dict[str, Innovation] = {}
        self._pods: Dict[str, str] = {}  # pod -> innovation title
        self._promoted = 0
        self._archived = 0

    def submit(self, title: str, author: str, novelty: float) -> Innovation:
        innovation = Innovation(title, author, novelty)
        self._innovations[innovation.id] = innovation
        return innovation

    def launch(self, innovation_id: str) -> bool:
        innovation = self._innovations.get(innovation_id)
        if innovation is None or innovation.status != "queued":
            return False
        pod = hashlib.sha256(f"pod:{innovation.title}".encode()).hexdigest()[:8]
        innovation.pod_id = pod
        innovation.status = "running"
        self._pods[pod] = innovation.title
        return True

    def promote(self, innovation_id: str) -> bool:
        innovation = self._innovations.get(innovation_id)
        if innovation is None or innovation.status != "running":
            return False
        innovation.status = "promoted"
        self._promoted += 1
        return True

    def archive(self, innovation_id: str) -> bool:
        innovation = self._innovations.get(innovation_id)
        if innovation is None:
            return False
        innovation.status = "archived"
        self._archived += 1
        return True

    def status(self) -> Dict[str, Any]:
        return {"innovations": len(self._innovations), "running_pods": len(self._pods),
                "promoted": self._promoted, "archived": self._archived}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    lab = InnovationLab()
    return {"status": "active", "module": "innovation_lab",
            **lab.status()}
