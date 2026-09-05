"""Wave 139 — Endpoint Docs.

Auto-generates human- and machine-readable documentation for every
live endpoint by scanning the route registry. Each module's docstring
and status fields are exposed so the platform documents itself.
"""
from __future__ import annotations

import importlib
import inspect
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]


class EndpointDocs:
    """Self-documenting endpoint catalog."""

    def __init__(self):
        self._catalog: Dict[str, Dict[str, Any]] = {}

    def scan_module(self, module_name: str) -> Dict[str, Any]:
        if module_name in self._catalog:
            return self._catalog[module_name]
        entry = {"module": module_name, "doc": "", "handler": False}
        try:
            mod = importlib.import_module(module_name)
            entry["doc"] = (inspect.getdoc(mod) or "").split("\n")[0]
            entry["handler"] = hasattr(mod, "handler")
        except Exception as e:
            entry["doc"] = f"import error: {e}"
        self._catalog[module_name] = entry
        return entry

    def scan_all(self, limit: int = 200) -> List[Dict[str, Any]]:
        api_dir = ROOT / "api"
        names = sorted(p.stem for p in api_dir.glob("*.py") if p.stem != "__init__")
        return [self.scan_module(n) for n in names[:limit]]

    def status(self) -> Dict[str, Any]:
        return {"documented": len(self._catalog)}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    docs = EndpointDocs()
    return {"status": "active", "module": "endpoint_docs",
            **docs.status()}

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "interface", "status": "active", "wave": "139", "module": "endpoint_docs"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
