"""Wave 131 — Automation Director.

Schedules recurring automated tasks against the workforce. Jobs can
run on intervals, be delegated to specific roles, and accumulate an
execution ledger that feeds future scheduling decisions.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class AutomationJob:
    """A recurring automated job."""

    def __init__(self, name: str, interval_s: float, role: str = "general"):
        self.name = name
        self.interval_s = interval_s
        self.role = role
        self.next_run = time.time() + interval_s
        self.runs = 0
        self.last_duration = 0.0
        self.created = time.time()
        self.id = hashlib.sha256(f"job:{name}".encode()).hexdigest()[:10]

    def due(self, now: float) -> bool:
        return now >= self.next_run

    def execute(self, now: float, duration_s: float = 0.2) -> bool:
        if not self.due(now):
            return False
        self.runs += 1
        self.last_duration = duration_s
        self.next_run = now + self.interval_s
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "role": self.role,
                "interval_s": self.interval_s, "runs": self.runs,
                "next_run": round(self.next_run, 4)}


class AutomationDirector:
    """Schedules and runs recurring workforce automations."""

    def __init__(self):
        self._jobs: Dict[str, AutomationJob] = {}
        self._execution_ledger: List[str] = []

    def register(self, name: str, interval_s: float, role: str = "general") -> AutomationJob:
        job = AutomationJob(name, interval_s, role)
        self._jobs[job.id] = job
        return job

    def tick(self, now: Optional[float] = None, duration_s: float = 0.2) -> int:
        now = now or time.time()
        executed = 0
        for job in self._jobs.values():
            if job.execute(now, duration_s):
                self._execution_ledger.append(job.id)
                executed += 1
        return executed

    def pause(self, job_id: str) -> bool:
        job = self._jobs.get(job_id)
        if job is None:
            return False
        job.next_run = float("inf")
        return True

    def resume(self, job_id: str, now: Optional[float] = None) -> bool:
        job = self._jobs.get(job_id)
        if job is None:
            return False
        now = now or time.time()
        job.next_run = now + job.interval_s
        return True

    def status(self) -> Dict[str, Any]:
        return {"jobs": len(self._jobs),
                "executions": len(self._execution_ledger),
                "active_jobs": sum(1 for j in self._jobs.values()
                                   if j.next_run != float("inf"))}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    director = AutomationDirector()
    return {"status": "active", "module": "automation_director",
            **director.status()}
