"""Universal Vercel serverless entrypoint.

Dispatch the entire IXpansion API (345 modules / 352 routes) through a
single Python function using the same dispatch logic as the local
`api_server.py`. Handles both dict-style (Vercel raw Python runtime)
and attribute-style request objects.

GET  /health | /modules | /metrics
GET/POST /api/<module>  (also any legacy vercel route dest that maps to a module)
"""
from __future__ import annotations

import base64
import json
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

import api_server  # noqa: E402


def _req_value(request, *keys, default=None):
    """Read a value from a dict-like or attribute-style request."""
    for key in keys:
        if isinstance(request, dict):
            if key in request:
                return request[key]
        else:
            value = getattr(request, key, None)
            if value is not None:
                return value
    return default


def _parse_body(body) -> Dict[str, Any]:
    if not body:
        return {}
    if isinstance(body, dict):
        return body
    if isinstance(body, bytes):
        text = body.decode("utf-8", errors="replace")
    else:
        text = str(body)
    # Vercel base64-encodes binary bodies; try base64 decode first
    try:
        decoded = base64.b64decode(text, validate=True).decode("utf-8")
        text = decoded
    except Exception:
        pass
    try:
        data = json.loads(text or "{}")
        return data if isinstance(data, dict) else {"value": data}
    except json.JSONDecodeError:
        return {"error": "invalid JSON body"}


def handler(request) -> dict:
    """Vercel Python Functions handler."""
    method = (_req_value(request, "method", default="GET") or "GET").upper()
    path = _req_value(request, "path", "rawPath", default="/") or "/"
    path = path.split("?")[0].rstrip("/") or "/"

    if path == "/health":
        return api_server.platform_health()
    if path == "/modules":
        names = sorted(api_server.MODULE_REGISTRY.keys()) if api_server.MODULE_REGISTRY else []
        return {"modules": names, "count": len(names)}
    if path == "/metrics":
        return {"up": 1,
                "modules": len(api_server.MODULE_REGISTRY) if api_server.MODULE_REGISTRY else 0}

    if path.startswith("/api/"):
        module = api_server.route_name_to_module(path[len("/api/"):])
        body = _req_value(request, "body", "rawBody", default=b"")
        payload = _parse_body(body) if method == "POST" else {}
        result, status = api_server.call_handler(module, payload)
        return result

    return {"status": "active", "version": api_server.VERSION,
            "endpoint": path, "error": "not found", "code": 404}
