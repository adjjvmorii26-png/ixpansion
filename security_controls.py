"""Small, dependency-free safety controls for automation and human gates."""

import json
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, Optional, Set
from urllib.parse import urlparse
from urllib.request import Request, urlopen


PROTECTED_ACTIONS = {"PROD_DEPLOY", "SECRET_ROTATE"}


class AuditStore:
    """Persist every gate decision in a local SQLite database."""

    def __init__(self, path: str = "ixpansion_audit.sqlite3"):
        self.connection = sqlite3.connect(path)
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS gate_audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                tags TEXT NOT NULL,
                trust REAL NOT NULL,
                operator TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                decision TEXT NOT NULL
            )
            """
        )
        self.connection.commit()

    def record(
        self,
        task_id: str,
        tags: Iterable[str],
        trust: float,
        operator: str,
        decision: str,
    ) -> None:
        timestamp = datetime.now(timezone.utc).isoformat()
        self.connection.execute(
            "INSERT INTO gate_audits "
            "(task_id, tags, trust, operator, timestamp, decision) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (task_id, json.dumps(sorted(set(tags))), trust, operator, timestamp, decision),
        )
        self.connection.commit()

    def decisions(self, task_id: Optional[str] = None):
        query = "SELECT task_id, tags, trust, operator, timestamp, decision FROM gate_audits"
        parameters = ()
        if task_id:
            query += " WHERE task_id = ?"
            parameters = (task_id,)
        query += " ORDER BY id"
        return self.connection.execute(query, parameters).fetchall()

    def close(self) -> None:
        self.connection.close()


class TrustStore:
    """Namespaced EMA trust with conservative idle decay."""

    def __init__(self, idle_decay_per_day: float = 0.1):
        self.values = {}
        self.last_seen = {}
        self.idle_decay_per_day = idle_decay_per_day
        self.started_at = time.time()

    def observe(self, subject: str, success: bool, alpha: float = 0.2) -> float:
        current = self.trust(subject)
        target = 1.0 if success else 0.0
        updated = current + alpha * (target - current)
        self.values[subject] = updated
        self.last_seen[subject] = time.time()
        return updated

    def trust(self, subject: str, now: Optional[float] = None) -> float:
        value = self.values.get(subject, 0.5)
        last_seen = self.last_seen.get(subject, self.started_at)
        days_idle = int(max(0.0, (now or time.time()) - last_seen) / 86400)
        return max(0.0, value - days_idle * self.idle_decay_per_day)


@dataclass
class PendingGate:
    task_id: str
    tags: Set[str]
    trust: float
    operator: str


class HumanGate:
    """Require human approval, with dual control for production actions."""

    def __init__(self, audits: AuditStore, trust: TrustStore, minimum_trust: float = 0.5):
        self.audits = audits
        self.trust = trust
        self.minimum_trust = minimum_trust
        self.pending = {}

    def request(self, task_id: str, tags: Iterable[str], operator: str) -> str:
        tag_set = set(tags)
        score = self.trust.trust(f"agent:{operator}")
        if score < self.minimum_trust:
            self.audits.record(task_id, tag_set, score, operator, "REJECTED_LOW_TRUST")
            return "REJECTED_LOW_TRUST"
        self.pending[task_id] = PendingGate(task_id, tag_set, score, operator)
        decision = "PENDING_DUAL_CONTROL" if tag_set & PROTECTED_ACTIONS else "PENDING"
        self.audits.record(task_id, tag_set, score, operator, decision)
        return decision

    def approve(self, task_id: str, operator: str) -> str:
        pending = self.pending.get(task_id)
        if pending is None:
            raise KeyError(f"No pending gate for {task_id}")
        score = self.trust.trust(f"agent:{pending.operator}")
        if score < self.minimum_trust:
            decision = "REJECTED_LOW_TRUST"
        elif pending.tags & PROTECTED_ACTIONS and operator == pending.operator:
            decision = "REJECTED_DUAL_CONTROL"
        else:
            decision = "APPROVED"
        self.audits.record(task_id, pending.tags, score, operator, decision)
        if decision == "APPROVED":
            del self.pending[task_id]
        return decision


class URLPolicy:
    """Allow requests only to explicitly configured hosts."""

    def __init__(self, allowed_hosts: Iterable[str]):
        self.allowed_hosts = {host.lower() for host in allowed_hosts}

    def validate(self, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("URL must use HTTP(S) and include a hostname")
        if parsed.hostname.lower() not in self.allowed_hosts:
            raise PermissionError(f"Host is not allowlisted: {parsed.hostname}")


class API_AUTOMATION:
    """HTTP automation that can be exercised without making real requests."""

    def __init__(self, policy: URLPolicy, dry_run: bool = False):
        self.policy = policy
        self.dry_run = dry_run

    def post(self, url: str, payload: bytes = b"{}") -> str:
        self.policy.validate(url)
        if self.dry_run:
            return f"DRY_RUN: POST {url}"
        request = Request(url, data=payload, method="POST")
        with urlopen(request, timeout=30) as response:
            return response.read().decode("utf-8")