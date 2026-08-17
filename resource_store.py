"""SQLite-backed provenance and reusable artifacts for public resources."""

from __future__ import annotations

import json
import sqlite3
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Optional


class ResourceStore:
    """Persist bounded resource passports without storing raw fetch payloads."""

    def __init__(self, path: str = "ixpansion_resources.sqlite3") -> None:
        self.connection = sqlite3.connect(path, check_same_thread=False)
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS resources (
                resource_id TEXT PRIMARY KEY,
                source_url TEXT NOT NULL,
                title TEXT NOT NULL,
                links TEXT NOT NULL,
                artifact TEXT NOT NULL,
                fetched_at TEXT NOT NULL,
                UNIQUE(source_url, artifact)
            )
            """
        )
        self.connection.commit()

    def save(
        self,
        resource_id: str,
        *,
        source_url: str,
        title: str,
        links: list[str],
        artifact: dict[str, Any],
    ) -> dict[str, Any]:
        fetched_at = datetime.now(timezone.utc).isoformat()
        self.connection.execute(
            """
            INSERT INTO resources
                (resource_id, source_url, title, links, artifact, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(resource_id) DO UPDATE SET
                source_url=excluded.source_url,
                title=excluded.title,
                links=excluded.links,
                artifact=excluded.artifact,
                fetched_at=excluded.fetched_at
            """,
            (
                resource_id,
                source_url,
                title,
                json.dumps(links),
                json.dumps(artifact),
                fetched_at,
            ),
        )
        self.connection.commit()
        return self.get(resource_id)

    def list(self) -> list[dict[str, Any]]:
        rows = self.connection.execute(
            "SELECT resource_id, source_url, title, links, fetched_at FROM resources ORDER BY fetched_at DESC"
        ).fetchall()
        return [
            {
                "resource_id": row[0],
                "source_url": row[1],
                "title": row[2],
                "links": json.loads(row[3]),
                "fetched_at": row[4],
            }
            for row in rows
        ]

    def get(self, resource_id: str) -> dict[str, Any]:
        row = self.connection.execute(
            "SELECT resource_id, source_url, title, links, artifact, fetched_at "
            "FROM resources WHERE resource_id = ?",
            (resource_id,),
        ).fetchone()
        if row is None:
            raise KeyError(f"No resource named: {resource_id}")
        return {
            "resource_id": row[0],
            "source_url": row[1],
            "title": row[2],
            "links": json.loads(row[3]),
            "artifact": deepcopy(json.loads(row[4])),
            "fetched_at": row[5],
        }

    def close(self) -> None:
        self.connection.close()