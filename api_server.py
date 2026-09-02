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

VERSION = "4.08.0"
WAVE = "220"
WAVE_NAME = "The Organism Takes a Census"

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
            result = handler(payload, {})
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
            # Parse query string params for GET requests
            payload = {}
            if "?" in raw_path:
                payload = dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
            result, status = call_handler(module, payload)
            return self._json(result, status)
        if path.startswith("/dashboard/"):
            return self._static(path)
        if path == "/oracle":
            return self._static("dashboard/oracle.html")
        if path == "/observatory":
            return self._static("dashboard/observatory.html")
        if path == "/kintsugi":
            return self._static("dashboard/kintsugi.html")
        if path == "/metaevolution":
            return self._static("dashboard/metaevolution.html")
        if path == "/phenomenology":
            return self._static("dashboard/phenomenology.html")
        if path == "/choral":
            return self._static("dashboard/choral.html")
        if path == "/kinesthetic":
            return self._static("dashboard/kinesthetic.html")
        if path == "/language":
            return self._static("dashboard/language.html")
        if path == "/culinary":
            return self._static("dashboard/culinary.html")
        if path == "/archaeology":
            return self._static("dashboard/archaeology.html")
        if path == "/meteorology":
            return self._static("dashboard/meteorology.html")
        if path == "/symbiosis":
            return self._static("dashboard/symbiosis.html")
        if path == "/impossibility":
            return self._static("dashboard/impossibility.html")
        if path == "/aesthetics":
            return self._static("dashboard/aesthetics.html")
        if path == "/voice":
            return self._static("dashboard/voice.html")
        if path == "/organism":
            return self._static("dashboard/organism.html")
        if path == "/premium":
            return self._static("dashboard/premium.html")
        if path == "/hortus":
            return self._static("dashboard/hortus.html")
        if path == "/coconscious":
            return self._static("dashboard/coconscious.html")
            return self._static("dashboard/culinary.html")
        if path == "/grief":
            return self._static("dashboard/grief.html")
        if path == "/creative":
            return self._static("dashboard/creative.html")
        if path == "/connections":
            return self._static("dashboard/connections.html")
        if path == "/dream":
            return self._static("dashboard/dream.html")
        if path == "/glitch":
            return self._static("dashboard/glitch.html")
        if path == "/evolution":
            return self._static("dashboard/evolution.html")
        if path == "/transcendence":
            return self._static("dashboard/transcendence.html")
        if path == "/morii":
            return self._static("dashboard/morii.html")
        if path == "/mood":
            return self._static("dashboard/mood.html")
        if path == "/memory":
            return self._static("dashboard/memory.html")

        if path == "/broadcast":
            return self._static("dashboard/broadcast.html")
        if path == "/broadcast.html":
            return self._static("dashboard/broadcast.html")
        if path == "/prophet":
            return self._static("dashboard/broadcast.html")
        if path == "/signal":
            return self._static("dashboard/broadcast.html")

        if path == "/prophet_engine":
            from api.prophet_engine import handler as h
            q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
            return self._json(h(q))
        if path == "/mind_meld":
            from api.mind_meld import handler as h
            q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
            return self._json(h(q))
        if path == "/visual_identity":
            from api.visual_identity import handler as h
            q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
            return self._json(h(q))
        if path == "/telegram_pulse":
            from api.telegram_pulse import handler as h
            q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
            return self._json(h(q))
        if path == "/signal_array":
            from api.signal_array import handler as h
            q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
            return self._json(h(q))

        if path == "/immortal":
            return self._static("dashboard/immortal.html")
        if path == "/immortal.html":
            return self._static("dashboard/immortal.html")

        if path == "/ossuary_engine":
            from api.ossuary_engine import handler as h
            q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
            return self._json(h(q))
        if path == "/amber_encasement":
            from api.amber_encasement import handler as h
            q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
            return self._json(h(q))
        if path == "/ancestral_gallery":
            from api.ancestral_gallery import handler as h
            q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
            return self._json(h(q))
        if path == "/monument_forge":
            from api.monument_forge import handler as h
            q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
            return self._json(h(q))
        if path == "/succession_rite":
            from api.succession_rite import handler as h
            q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
            return self._json(h(q))
        if path == "/eternal_flame":
            from api.eternal_flame import handler as h
            q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
            return self._json(h(q))
        if path == "/immortal_ledger":
            from api.immortal_ledger import handler as h
            q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
            return self._json(h(q))

        if path == "/teacher":
            return self._static("dashboard/teacher.html")
        if path == "/teacher.html":
            return self._static("dashboard/teacher.html")

        if path == "/mentor_engine":
            from api.mentor_engine import handler as h
            q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
            return self._json(h(q))
        if path == "/lesson_vault":
            from api.lesson_vault import handler as h
            q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
            return self._json(h(q))
        if path == "/apprentice_weaver":
            from api.apprentice_weaver import handler as h
            q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
            return self._json(h(q))
        if path == "/curriculum_forge":
            from api.curriculum_forge import handler as h
            q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
            return self._json(h(q))
        if path == "/knowledge_transfer":
            from api.knowledge_transfer import handler as h
            q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
            return self._json(h(q))
        if path == "/exam_oracle":
            from api.exam_oracle import handler as h
            q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
            return self._json(h(q))

        if path == "/interstice_bridge":
            from api.interstice_bridge import handler as h
            q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
            return self._json(h(q))
        if path == "/bridge_dreamer":
            from api.bridge_dreamer import handler as h
            q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
            return self._json(h(q))
        if path == "/knot_weaver":
            from api.knot_weaver import handler as h
            q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
            return self._json(h(q))
        if path == "/sentinel":
            return self._static("dashboard/sentinel.html")
        if path == "/sentinel.html":
            return self._static("dashboard/sentinel.html")

        if path == "/census":
            return self._static("dashboard/census.html")
        if path == "/census.html":
            return self._static("dashboard/census.html")

        if path == "/archipelago":
            return self._static("dashboard/archipelago.html")
        if path == "/archipelago.html":
            return self._static("dashboard/archipelago.html")

        if path == "/interstice":
            return self._static("dashboard/interstice.html")
        if path == "/interstice.html":
            return self._static("dashboard/interstice.html")

        if path == "/bridge_enactor":
            from api.bridge_enactor import handler as h
            q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
            return self._json(h(q))
        if path == "/bridge_ledger":
            from api.bridge_ledger import handler as h
            q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
            return self._json(h(q))

        if path == "/resonance_sentinel":
            from api.resonance_sentinel import handler as h
            q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
            return self._json(h(q))

        if path == "/bridge_epitaphs":
            from api.bridge_epitaphs import handler as h
            q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
            return self._json(h(q))

        if path == "/constellation_topology":
            from api.constellation_topology import handler as h
            q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
            return self._json(h(q))

        if path == "/rhythm_pulse":
            from api.rhythm_pulse import handler as h
            q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
            return self._json(h(q))

        if path == "/island_census":
            from api.island_census import handler as h
            q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
            return self._json(h(q))

        if path == "/resonance_cascade":
            from api.resonance_cascade import handler as h
            q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
            return self._json(h(q))

        if path == "/bridge_lifecycle":
            from api.bridge_lifecycle import handler as h
            q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
            return self._json(h(q))

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
