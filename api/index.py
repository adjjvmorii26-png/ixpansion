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
    raw_path = (request_path or "/")
    path = raw_path.split("?")[0].rstrip("/") or "/"

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

    if path == "/oracle":
        return {"status": "active", "page": "oracle", "version": api_server.VERSION}
    if raw_path.split("?")[0].startswith("/echo"):
        from urllib.parse import urlparse, parse_qs
        qs = parse_qs(urlparse(raw_path).query)
        q = (qs.get("q") or [""])[0].strip().lower()
        if not q:
            return {"error": "no query ?q="}
        api_dir = ROOT / "api"
        matches = [f.stem for f in api_dir.glob("*.py")
                   if q in f.stem and f.stem not in ("__init__", "index", "unified_router")]
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        from harbinger.agents.dreamer import dream
        dreamscape = dream(salt=q, k=3, focus=q)
        related = [d["name"] for d in dreamscape.get("dreams", [])]
        return {"query": q, "modules": sorted(matches)[:20], "count": len(matches), "dreams": related}
    if path == "/revelations":
        rev = ROOT / "REVELATIONS.md"
        if rev.exists():
            return {"markdown": rev.read_text(encoding="utf-8")}
        return {"error": "no revelations yet"}
    if path == "/gateway":
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        from gateway.router import handle as gw_handle, render_public
        payload = {}
        if request_method == "POST" and body:
            try:
                payload = json.loads(body.decode("utf-8"))
            except Exception:
                payload = {}
        elif "?" in raw_path:
            from urllib.parse import urlparse, parse_qs
            qs = parse_qs(urlparse(raw_path).query)
            payload = {k: v[0] if v else "" for k, v in qs.items()}
        result, status = gw_handle(payload)
        return result
    if path == "/intent":
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        from tools.frontier_intent import analyze
        return analyze()
    if path == "/meter":
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        from harbinger.meter import measure
        return measure()
    if path == "/ledger":
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        from harbinger.agents.ledger import ledger
        return ledger()
    if path == "/forecast":
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        from tools.frontier_forecast import forecast
        return forecast()
    if path == "/capsule":
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        from tools.time_capsule import seal, verify
        cap = seal()
        cap["verified"] = verify(cap)["integrity"]
        return cap
    if path == "/song":
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        from tools.frontier_song import generate_notes, module_names
        notes = generate_notes(module_names())
        return {"count": len(notes), "notes": notes[:60],
                "total_duration_s": round(sum(n["dur"] for n in notes), 1)}
    if path == "/poem":
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        from harbinger.agents import poet as _poet
        return _poet.run()
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
        # Parse query string params into payload (GET /api/<module>?key=val)
        if "?" in raw_path:
            from urllib.parse import urlparse, parse_qs
            qs = parse_qs(urlparse(raw_path).query)
            payload = {k: (v[0] if v else "") for k, v in qs.items()}
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
    qs = environ.get("QUERY_STRING", "")
    if qs:
        path = path + "?" + qs
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
