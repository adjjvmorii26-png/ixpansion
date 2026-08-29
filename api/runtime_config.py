"""Wave 139 — Runtime Config.

Central source of truth for the platform's runtime: mode, seed,
wave, and the module/route counts. Reads from environment variables
with safe defaults and validates that reported config matches the
live deployment.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List


class RuntimeConfig:
    """Reads and validates platform runtime configuration."""

    REQUIRED = ["NEXUS_MODE", "NEXUS_SEED", "NEXUS_WAVE", "NEXUS_MODULES", "NEXUS_ROUTES"]

    def __init__(self, env: Dict[str, str] = None):
        self.env = env or dict(os.environ)

    def get(self, key: str, default: str) -> str:
        return self.env.get(key, default)

    def mode(self) -> str:
        return self.get("NEXUS_MODE", "development")

    def seed(self) -> int:
        try:
            return int(self.get("NEXUS_SEED", "42"))
        except ValueError:
            return 42

    def wave(self) -> str:
        return self.get("NEXUS_WAVE", "139")

    def validate(self, actual_modules: int, actual_routes: int) -> Dict[str, bool]:
        m = self.get("NEXUS_MODULES", "")
        r = self.get("NEXUS_ROUTES", "")
        return {
            "modules_match": m.isdigit() and int(m) == actual_modules if m.isdigit() else False,
            "routes_match": r.isdigit() and int(r) == actual_routes if r.isdigit() else False,
        }

    def status(self) -> Dict[str, Any]:
        return {"mode": self.mode(), "seed": self.seed(), "wave": self.wave(),
                "modules_env": self.get("NEXUS_MODULES", ""),
                "routes_env": self.get("NEXUS_ROUTES", "")}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    config = RuntimeConfig()
    return {"status": "active", "module": "runtime_config",
            **config.status()}
