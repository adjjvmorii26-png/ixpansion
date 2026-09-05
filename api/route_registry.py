"""Wave 139 — Route Registry.

The canonical map of the live platform's HTTP routes. Loads routes
from vercel.json (the single source of truth) and resolves which API
module each URL pattern dispatches to, making the runtime self-aware
of its own surface.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]


class RouteRegistry:
    """Parses and indexes the platform's route map."""

    def __init__(self, vercel_path: str = ""):
        self.vercel_path = vercel_path or str(ROOT / "vercel.json")
        self._routes: List[Dict[str, str]] = []
        self._load()

    def _load(self) -> None:
        try:
            with open(self.vercel_path) as f:
                data = json.load(f)
            self._routes = list(data.get("routes", []))
        except (OSError, json.JSONDecodeError):
            self._routes = []

    def count(self) -> int:
        return len(self._routes)

    def destinations(self) -> List[str]:
        return [r.get("dest", "").lstrip("/") for r in self._routes]

    def match(self, path: str) -> str:
        """Return the destination module for a request path."""
        for route in self._routes:
            src = route.get("src", "")
            if src == "/api/(.*)":
                return "unified_router"
            if src.startswith("/api/") and src.endswith("(.*)"):
                base = src.split("(.*)")[0].rstrip("/")
                if path.startswith(base):
                    return route.get("dest", "").lstrip("/")
        return "unified_router"

    def status(self) -> Dict[str, Any]:
        return {"routes": self.count(),
                "unique_destinations": len(set(self.destinations())),
                "source": self.vercel_path}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    registry = RouteRegistry()
    return {"status": "active", "module": "route_registry",
            **registry.status()}

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "interface", "status": "active", "wave": "139", "module": "route_registry"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
