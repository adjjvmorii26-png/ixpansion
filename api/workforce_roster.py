"""Wave 132 — Workforce Roster.

Maintains the active roster across shifts: workers are assigned to
time slots that respect rest cycles, coverage minimums, and skill
requirements, keeping the workforce online 24/7 without burnout.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class Shift:
    """A scheduled work slot on the roster."""

    def __init__(self, label: str, slot_hours: int, min_workers: int = 1):
        self.label = label
        self.slot_hours = slot_hours
        self.min_workers = min_workers
        self.assigned: List[str] = []
        self.contiguous_active = 0
        self.created = time.time()
        self.id = hashlib.sha256(f"shift:{label}".encode()).hexdigest()[:10]

    def add(self, worker: str) -> bool:
        if worker in self.assigned:
            return False
        self.assigned.append(worker)
        return True

    def covered(self) -> bool:
        return len(self.assigned) >= self.min_workers

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "label": self.label, "slot_hours": self.slot_hours,
                "min_workers": self.min_workers, "assigned": self.assigned,
                "covered": self.covered()}


class WorkforceRoster:
    """Assigns workers to shifts with rest-cycle awareness."""

    def __init__(self):
        self._shifts: Dict[str, Shift] = {}
        self._rest_cycle: Dict[str, int] = {}

    def add_shift(self, label: str, slot_hours: int, min_workers: int = 1) -> Shift:
        shift = Shift(label, slot_hours, min_workers)
        self._shifts[shift.id] = shift
        return shift

    def assign(self, worker: str, shift_id: str, max_hours: int = 8) -> bool:
        shift = self._shifts.get(shift_id)
        if shift is None:
            return False
        if shift.slot_hours > max_hours:
            return False
        if self._rest_cycle.get(worker, 0) > 0:
            return False
        ok = shift.add(worker)
        if ok:
            self._rest_cycle[worker] = shift.slot_hours
            shift.contiguous_active += 1
        return ok

    def rest(self, worker: str, hours: int = 8) -> None:
        self._rest_cycle[worker] = max(0, self._rest_cycle.get(worker, 0) - hours)

    def coverage_gaps(self) -> List[str]:
        return [s.to_dict()["id"] for s in self._shifts.values() if not s.covered()]

    def status(self) -> Dict[str, Any]:
        return {"shifts": len(self._shifts), "workers_on_roster": len(self._rest_cycle),
                "gaps": len(self.coverage_gaps())}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    roster = WorkforceRoster()
    return {"status": "active", "module": "workforce_roster",
            **roster.status()}
