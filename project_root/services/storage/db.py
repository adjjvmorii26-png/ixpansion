"""In-memory database with snapshot/restore."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class MemoryDB:
    def __init__(self) -> None:
        self._tables: dict[str, dict[str, Any]] = {}

    def insert(self, table: str, record_id: str, data: dict[str, Any]) -> None:
        self._tables.setdefault(table, {})[record_id] = data

    def get(self, table: str, record_id: str) -> dict[str, Any] | None:
        return self._tables.get(table, {}).get(record_id)

    def query(self, table: str, **filters: Any) -> list[dict[str, Any]]:
        records = self._tables.get(table, {}).values()
        return [r for r in records if all(r.get(k) == v for k, v in filters.items())]

    def delete(self, table: str, record_id: str) -> bool:
        return self._tables.get(table, {}).pop(record_id, None) is not None

    def export_json(self, filepath: str) -> None:
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        Path(filepath).write_text(json.dumps(self._tables, indent=2, default=str))

    @property
    def tables(self) -> list[str]:
        return list(self._tables.keys())
