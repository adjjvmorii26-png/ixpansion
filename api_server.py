"""IXpansion Live Server — local API server mirroring the Vercel surface.

Runs the full 352-module API locally with the same URL layout as the
Vercel deployment:

  GET  /health              — platform health
  GET  /modules             — discoverable module list
  GET  /api/<module>        — module status (empty payload)
  POST /api/<module>        — module dispatch with JSON payload
  GET  /metrics             — Prometheus-style metrics text
  GET  /dashboard / dashboard/... — static dashboard
  *    — static files from the repo root

Usage:
  python api_server.py [--port 3000]
  python main.py serve        (delegates here)
"""
from __future__ import annotations

import importlib
import inspect
import json
import os
import re
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "3.78.0"
WAVE = "163"
WAVE_NAME = "Resonant Bloom"

try:
    from api.unified_router import UnifiedRouter, MODULE_REGISTRY
except Exception:  # pragma: no cover - fallback if router fails
    MODULE_REGISTRY = {}
    UnifiedRouter = None

_router = UnifiedRouter() if UnifiedRouter else None

KEBAB_TO_SNAKE = re.compile(r"([a-z0-9])-([a-z])")


def route_name_to_module(path: str) -> str:
    """Convert a URL path segment into a module name.

    Handles both snake_case (/api/workforce_orchestrator) and kebab-case
    (/api/workforce-orchestrator) as routed in vercel.json.
    """
    name = path.strip("/").split("/")[-1]
    name = KEBAB_TO_SNAKE.sub(r"\1_\2", name)
    return name


def call_handler(module_name: str, payload: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """Dispatch to a module's handler with either payload-style or
    request/response-style signatures.

    Returns (result, http_status).
    """
    if _router is not None and module_name in MODULE_REGISTRY:
        try:
            result = _router.route(module_name, payload)
            if isinstance(result, dict) and "error" in result:
                return result, 404
            return result, 200
        except Exception as e:  # pragma: no cover
            return {"error": str(e), "module": module_name}, 500

    # Direct fallback: try to import and call
    try:
        module = importlib.import_module(module_name)
        handler = getattr(module, "handler", None)
        if handler is None:
            return {"error": f"module '{module_name}' has no handler"}, 404
        try:
            signature = inspect.signature(handler)
            nparams = len([
                p for p in signature.parameters.values()
                if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
            ])
        except (TypeError, ValueError):
            nparams = 1
        if nparams >= 2:
            result = handler({}, {})
        else:
            result = handler(payload)
        return result, 200
    except ImportError:
        return {"error": f"module '{module_name}' not found"}, 404
    except Exception as e:  # pragma: no cover
        return {"error": str(e), "module": module_name}, 500


def platform_health() -> Dict[str, Any]:
    """Live platform health payload."""
    api_dir = ROOT / "api"
    module_count = len([p for p in api_dir.glob("*.py") if p.stem not in ("__init__", "index")]) if api_dir.exists() else 0
    route_count = 0
    try:
        with open(ROOT / "vercel.json") as f:
            route_count = len(json.load(f).get("routes", []))
    except (OSError, json.JSONDecodeError):
        pass
    test_count = len(list((ROOT / "tests").glob("test_*.py"))) if (ROOT / "tests").exists() else 0
    return {
        "status": "healthy",
        "version": VERSION,
        "wave": WAVE,
        "layer": WAVE_NAME,
        "modules": module_count,
        "route_entries": route_count,
        "test_suites": test_count,
        "mode": os.environ.get("NEXUS_MODE", "development"),
        "seed": os.environ.get("NEXUS_SEED", "42"),
    }


class ApiHandler(BaseHTTPRequestHandler):
    """HTTP handler serving the live platform."""

    server_version = f"IXpansion/{VERSION}"
    _cache: Dict[str, Any] = {}

    # ----- helpers -----
    def _json(self, obj: Dict[str, Any], status: int = 200) -> None:
        body = json.dumps(obj, indent=2, default=str).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _text(self, text: str, content_type: str = "text/plain; charset=utf-8",
              status: int = 200) -> None:
        body = text.encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _static(self, rel: str) -> None:
        """Serve a static file from the repo root (safe path)."""
        candidate = (ROOT / rel.lstrip("/")).resolve()
        try:
            candidate.relative_to(ROOT)
        except ValueError:
            return self._json({"error": "forbidden path"}, 403)
        if candidate.is_dir():
            candidate = candidate / "index.html"
        if not candidate.is_file():
            return self._json({"error": f"not found: {rel}"}, 404)
        content_type = "text/html" if candidate.suffix == ".html" else (
            "application/javascript" if candidate.suffix == ".js" else (
            "text/css" if candidate.suffix == ".css" else
            "application/octet-stream"))
        self._text(candidate.read_bytes().decode("utf-8", errors="replace"), content_type)

    def log_message(self, fmt, *args):  # quieter access log
        sys.stderr.write("[api] %s\n" % (fmt % args))

    # ----- GET -----
    def do_GET(self):
        self_raw_path = self.path
        raw_path = self.path.split("?")[0]
        path = raw_path.rstrip("/") or "/"
        if path == "/health":
            return self._json(platform_health())
        if path == "/modules":
            names = sorted(MODULE_REGISTRY.keys()) if MODULE_REGISTRY else []
            return self._json({"modules": names, "count": len(names)})
        if path == "/metrics":
            return self._text("ixpansion_up 1\nixpansion_modules "
                              + str(len(MODULE_REGISTRY) if MODULE_REGISTRY else 0)
                              + "\n", "text/plain; version=0.0.4; charset=utf-8")
        if raw_path.startswith("/echo"):
            from urllib.parse import urlparse, parse_qs
            qs = parse_qs(urlparse(self_raw_path).query)
            q = (qs.get("q") or [""])[0].strip().lower()
            if not q:
                return self._json({"error": "no query ?q="}, 400)
            # find modules sharing the word root
            api_dir = ROOT / "api"
            matches = [f.stem for f in api_dir.glob("*.py")
                       if q in f.stem and f.stem not in ("__init__", "index", "unified_router")]
            # dream fusions on this word
            sys.path.insert(0, str(ROOT))
            from harbinger.agents.dreamer import dream
            dreamscape = dream(salt=q, k=3, focus=q)
            related = [d["name"] for d in dreamscape.get("dreams", [])]
            return self._json({"query": q, "modules": sorted(matches)[:20],
                               "count": len(matches), "dreams": related})
        if path == "/revelations":
            rev = ROOT / "REVELATIONS.md"
            if rev.exists():
                return self._text(rev.read_text(encoding="utf-8"),
                                  "text/markdown; charset=utf-8")
            return self._json({"error": "no revelations yet"}, 404)
        if path == "/gateway":
            sys.path.insert(0, str(ROOT))
            from gateway.router import handle as gw_handle
            import io
            try:
                raw_body = self.rfile.read(int(self.headers.get("Content-Length", 0) or 0))
                payload = json.loads(raw_body) if raw_body else {}
            except Exception:
                payload = {}
            result, status = gw_handle(payload)
            return self._json(result, status)
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
            sys.path.insert(0, str(ROOT))
            from tools.time_capsule import seal, verify
            cap = seal()
            cap["verified"] = verify(cap)["integrity"]
            return self._json(cap)
        if path == "/song":
            sys.path.insert(0, str(ROOT))
            from tools.frontier_song import generate_notes, module_names
            notes = generate_notes(module_names())
            return self._json({"count": len(notes), "notes": notes[:60],
                               "total_duration_s": round(sum(n["dur"] for n in notes), 1)})
        if path == "/poem":
            sys.path.insert(0, str(ROOT))
            from harbinger.agents import poet
            p = poet.run()
            return self._json(p)
        if path == "/garden":
            try:
                sys.path.insert(0, str(ROOT))
                from hortus_hexis.lineage import generations, render_ascii
                payload = generations()
                payload["tree"] = render_ascii()
                return self._json(payload)
            except Exception as e:
                return self._json({"error": str(e)}, 500)
        if raw_path in ("/dashboard",) and not raw_path.endswith("/"):
            return self._redirect("/dashboard/")
        if path.startswith("/api/"):
            module = route_name_to_module(path[len("/api/"):])
            result, status = call_handler(module, {})
            return self._json(result, status)
        if path.startswith("/dashboard/"):
            return self._static(path)
        if path == "/oracle":
            return self._static("dashboard/oracle.html")
        if path == "/cons":
            return self._static("dashboard/coconscious.html")
        if path == "/" or path in ("/index.html",):
            return self._redirect("/dashboard/")
        # fall back to static file
        return self._static(raw_path.lstrip("/"))

    def _redirect(self, location: str) -> None:
        self.send_response(302)
        self.send_header("Location", location)
        self.send_header("Content-Length", "0")
        self.end_headers()

    # ----- POST -----
    def do_POST(self):
        path = self.path.split("?")[0].rstrip("/")
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
            if not isinstance(payload, dict):
                payload = {"value": payload}
        except json.JSONDecodeError:
            return self._json({"error": "invalid JSON body"}, 400)
        module = route_name_to_module(path[len("/api/"):]) if path.startswith("/api/") else ""
        if not module:
            return self._json({"error": "no module specified"}, 400)
        result, status = call_handler(module, payload)
        return self._json(result, status)

    # ----- OPTIONS (CORS preflight) -----
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Content-Length", "0")
        self.end_headers()


def create_server(port: int = 3000, host: str = "0.0.0.0") -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), ApiHandler)


def serve(port: int = 3000, host: str = "0.0.0.0") -> None:
    server = create_server(port, host)
    print(f"  IXpansion live server: http://localhost:{port}")
    print(f"  Health:               http://localhost:{port}/health")
    print(f"  Modules:              http://localhost:{port}/modules")
    print(f"  API:                  http://localhost:{port}/api/workforce_orchestrator")
    print(f"  Dashboard:            http://localhost:{port}/dashboard/")
    print(f"  Co-Conscious Console: http://localhost:{port}/cons")
    print(f"  ({VERSION} — Wave {WAVE} {WAVE_NAME})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="IXpansion live server")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "3000")))
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()
    serve(args.port, args.host)
