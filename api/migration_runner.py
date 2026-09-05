"""Wave 140 — Migration Runner.

Applies tracked schema migrations to runtime namespaces. Each
migration has a monotonic id and a transform; the runner records
which have applied and avoids re-applying them, keeping persistent
state up to date across releases.
"""
from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional


class Migration:
    """A schema transform applied once to a namespace."""

    def __init__(self, migration_id: str, description: str, transform: Callable[[Any], Any]):
        self.migration_id = migration_id
        self.description = description
        self.transform = transform

    def run(self, data: Any) -> Any:
        return self.transform(data)


class MigrationRunner:
    """Tracks and applies ordered migrations."""

    def __init__(self):
        self._migrations: List[Migration] = []
        self._applied: List[str] = []
        self._executions = 0

    def register(self, migration_id: str, description: str,
                 transform: Callable[[Any], Any]) -> None:
        self._migrations.append(Migration(migration_id, description, transform))

    def applied(self) -> List[str]:
        return list(self._applied)

    def apply_all(self, data: Any) -> Any:
        result = data
        for migration in self._migrations:
            if migration.migration_id in self._applied:
                continue
            result = migration.run(result)
            self._applied.append(migration.migration_id)
            self._executions += 1
        return result

    def pending(self) -> int:
        return sum(1 for m in self._migrations if m.migration_id not in self._applied)

    def status(self) -> Dict[str, Any]:
        return {"registered": len(self._migrations),
                "applied": len(self._applied), "pending": self.pending(),
                "executions": self._executions}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    runner = MigrationRunner()
    return {"status": "active", "module": "migration_runner", **runner.status()}

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "data", "status": "active", "wave": "140", "module": "migration_runner"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
