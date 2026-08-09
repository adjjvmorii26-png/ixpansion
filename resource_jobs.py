"""Bounded background execution for resource collection jobs."""

from __future__ import annotations

import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
import json
import sqlite3
from typing import Any, Callable


class ResourceJobQueueFull(RuntimeError):
    """Raised when the bounded resource queue cannot accept another job."""


class ResourceJobQueue:
    """Run a bounded number of resource jobs without blocking API requests."""

    def __init__(
        self,
        *,
        workers: int = 2,
        max_pending: int = 20,
        db_path: str = ":memory:",
    ) -> None:
        if workers <= 0 or max_pending <= 0:
            raise ValueError("workers and max_pending must be positive")
        self.executor = ThreadPoolExecutor(max_workers=workers)
        self.max_pending = max_pending
        self.lock = threading.Lock()
        self.jobs: dict[str, dict[str, Any]] = {}
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS resource_jobs "
            "(job_id TEXT PRIMARY KEY, state TEXT NOT NULL)"
        )
        rows = self.connection.execute("SELECT job_id, state FROM resource_jobs").fetchall()
        for job_id, serialized_state in rows:
            state = json.loads(serialized_state)
            if state.get("status") in {"queued", "running"}:
                state = {
                    "job_id": job_id,
                    "status": "interrupted",
                    "error": "resource job interrupted by restart",
                }
                self.connection.execute(
                    "UPDATE resource_jobs SET state = ? WHERE job_id = ?",
                    (json.dumps(state), job_id),
                )
            self.jobs[job_id] = state
        self.connection.commit()

    def _persist(self, state: dict[str, Any]) -> None:
        self.connection.execute(
            "INSERT OR REPLACE INTO resource_jobs (job_id, state) VALUES (?, ?)",
            (state["job_id"], json.dumps(state)),
        )
        self.connection.commit()

    def submit(self, work: Callable[[], dict[str, Any]]) -> dict[str, Any]:
        with self.lock:
            pending = sum(
                state["status"] in {"queued", "running"}
                for state in self.jobs.values()
            )
            if pending >= self.max_pending:
                raise ResourceJobQueueFull("resource job queue is full")
            job_id = f"resource-job-{uuid.uuid4().hex[:16]}"
            self.jobs[job_id] = {"job_id": job_id, "status": "queued"}
            self._persist(self.jobs[job_id])
        self.executor.submit(self._run, job_id, work)
        return self.get(job_id)

    def _run(self, job_id: str, work: Callable[[], dict[str, Any]]) -> None:
        with self.lock:
            self.jobs[job_id]["status"] = "running"
            self._persist(self.jobs[job_id])
        try:
            result = work()
        except Exception:
            with self.lock:
                self.jobs[job_id] = {
                    "job_id": job_id,
                    "status": "failed",
                    "error": "resource collection failed",
                }
                self._persist(self.jobs[job_id])
            return
        with self.lock:
            self.jobs[job_id] = {
                "job_id": job_id,
                "status": "complete",
                "result": result,
            }
            self._persist(self.jobs[job_id])

    def get(self, job_id: str) -> dict[str, Any]:
        with self.lock:
            state = self.jobs.get(job_id)
            if state is None:
                raise KeyError(f"No resource job named: {job_id}")
            return dict(state)

    def close(self) -> None:
        self.executor.shutdown(wait=True)
        self.connection.close()