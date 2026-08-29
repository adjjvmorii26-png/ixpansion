"""Unified Router — single entry point to all 191+ API modules.

Routes requests to the appropriate module handler based on the module
name. Provides module discovery, health checks, and batch execution.
The router is the central nervous system of the entire API surface.
"""
from __future__ import annotations

import importlib
import time
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

MODULE_REGISTRY: Dict[str, str] = {}


def _discover_modules():
    api_dir = ROOT / "api"
    for f in api_dir.iterdir():
        if f.suffix == ".py" and f.stem != "__init__" and f.stem != "unified_router":
            module_name = f.stem
            handler_name = f"{module_name}_handler"
            MODULE_REGISTRY[module_name] = handler_name


_discover_modules()


def _get_handler(module_name: str):
    if module_name not in MODULE_REGISTRY:
        return None
    try:
        module = importlib.import_module(f"api.{module_name}")
        handler_name = MODULE_REGISTRY[module_name]
        handler = getattr(module, handler_name, None)
        if handler is None:
            handler = getattr(module, "handler", None)
        return handler
    except ImportError:
        return None


class UnifiedRouter:
    def __init__(self):
        self.request_log: List[Dict[str, Any]] = []
        self.error_count = 0
        self.success_count = 0

    def route(self, module: str, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        payload = payload or {}
        start = time.time()
        handler = _get_handler(module)
        if not handler:
            self.error_count += 1
            return {"error": f"module '{module}' not found", "available": list(MODULE_REGISTRY.keys())[:20]}
        try:
            result = handler(payload)
            elapsed = time.time() - start
            self.success_count += 1
            self.request_log.append({
                "module": module, "action": payload.get("action", "status"),
                "elapsed": round(elapsed, 4), "success": True, "time": time.time(),
            })
            return result
        except Exception as e:
            self.error_count += 1
            return {"error": str(e), "module": module}

    def batch(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for req in requests:
            module = req.get("module", "")
            payload = req.get("payload", {})
            results.append({"module": module, "result": self.route(module, payload)})
        return results

    def list_modules(self) -> List[str]:
        return sorted(MODULE_REGISTRY.keys())

    def health(self) -> Dict[str, Any]:
        healthy = 0
        broken = []
        for module_name in MODULE_REGISTRY:
            handler = _get_handler(module_name)
            if handler:
                healthy += 1
            else:
                broken.append(module_name)
        return {
            "total": len(MODULE_REGISTRY),
            "healthy": healthy,
            "broken": broken,
            "success_rate": round(self.success_count / max(self.success_count + self.error_count, 1), 3),
        }


_router = UnifiedRouter()


def unified_router_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "route":
        return _router.route(payload.get("module", ""), payload.get("payload", {}))
    elif action == "batch":
        return {"results": _router.batch(payload.get("requests", []))}
    elif action == "modules":
        return {"modules": _router.list_modules(), "count": len(MODULE_REGISTRY)}
    elif action == "health":
        return _router.health()
    return {
        "status": "active",
        "total_modules": len(MODULE_REGISTRY),
        "total_requests": len(_router.request_log),
        "success_count": _router.success_count,
        "error_count": _router.error_count,
    }


handler = unified_router_handler
