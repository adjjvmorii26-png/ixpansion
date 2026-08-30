"""Universal Vercel serverless entrypoint (WSGI application).

Dispatches the entire IXpansion API (352 modules / 8 entry points)
through a single WSGI application, reusing the same dispatch logic as
the local `api_server.py`. Exposes both a WSGI `application` (the
canonical @vercel/python build entrypoint) and a dict-style `handler`
for the modern Python Functions runtime.

Routes:
  GET  /health | /modules | /metrics
  GET/POST /api/<module>
"""
from __future__ import annotations

import base64
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

import api_server  # noqa: E402


def _call(request_method: str, request_path: str, body: bytes = b"") -> Dict[str, Any]:
    """Resolve a request to a JSON response payload."""
    path = (request_path or "/").split("?")[0].rstrip("/") or "/"

    if path == "/health":
        return api_server.platform_health()
    if path == "/modules":
        names = sorted(api_server.MODULE_REGISTRY.keys()) if api_server.MODULE_REGISTRY else []
        return {"modules": names, "count": len(names)}
    if path == "/metrics":
        return {"up": 1, "modules": len(api_server.MODULE_REGISTRY) if api_server.MODULE_REGISTRY else 0}
    if path == "/" or path == "/dashboard" or path.startswith("/dashboard/") or path == "/cons":
        return {"status": "active", "version": api_server.VERSION,
                "dashboard": "served by static build"}

    if path == "/revelations":
        rev = ROOT / "REVELATIONS.md"
        if rev.exists():
            return {"markdown": rev.read_text(encoding="utf-8")}
        return {"error": "no revelations yet"}
    if path == "/garden":
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        try:
            from hortus_hexis.lineage import generations, render_ascii
            payload = generations()
            payload["tree"] = render_ascii()
            return payload
        except Exception as e:
            return {"error": str(e)}
    if path.startswith("/api/"):
        module = api_server.route_name_to_module(path[len("/api/"):])
        payload = {}
        if request_method == "POST" and body:
            try:
                text = body.decode("utf-8", errors="replace")
                try:
                    text = base64.b64decode(text, validate=True).decode("utf-8")
                except Exception:
                    pass
                payload = json.loads(text or "{}")
                if not isinstance(payload, dict):
                    payload = {"value": payload}
            except json.JSONDecodeError:
                payload = {"error": "invalid JSON body"}
        result, _status = api_server.call_handler(module, payload)
        return result

    return {"status": "active", "version": api_server.VERSION,
            "endpoint": path, "error": "not found", "code": 404}


def application(environ: Dict[str, Any], start_response):
    """WSGI application entrypoint (canonical @vercel/python build)."""
    method = environ.get("REQUEST_METHOD", "GET")
    path = environ.get("PATH_INFO", "/")
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except (TypeError, ValueError):
        length = 0
    body = environ["wsgi.input"].read(length) if length > 0 else b""

    payload = _call(method, path, body)
    response_body = json.dumps(payload, default=str).encode("utf-8")
    start_response("200 OK", [
        ("Content-Type", "application/json"),
        ("Content-Length", str(len(response_body))),
        ("Access-Control-Allow-Origin", "*"),
    ])
    return [response_body]


def handler(request) -> dict:
    """Modern Python Functions runtime (dict-style request) entrypoint."""
    if isinstance(request, dict):
        method = request.get("method", "GET")
        path = request.get("path", request.get("rawPath", "/"))
        raw = request.get("body", request.get("rawBody", b""))
        if isinstance(raw, str):
            raw = raw.encode("utf-8")
        if not isinstance(raw, (bytes, bytearray)):
            raw = b""
        return _call(method, path, bytes(raw))
    # attribute-style (ASGI-ish) fallback
    method = getattr(request, "method", "GET")
    path = getattr(request, "path", getattr(request, "rawPath", "/"))
    body = getattr(request, "body", getattr(request, "rawBody", b"")) or b""
    return _call(method, path, body)


app = application
