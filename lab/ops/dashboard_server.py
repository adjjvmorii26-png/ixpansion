#!/usr/bin/env python3
"""Local Control dashboard server — stdlib only.

  python lab/ops/dashboard_server.py
  python lab/ops/dashboard_server.py --port 8765

Serves:
  GET /                  -> dashboard/local_control.html
  GET /api/council       -> live AEGIS·HELIX·QUILL JSON
  GET /api/health        -> {"ok": true}
  GET /dashboard/*       -> static files under dashboard/
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DASH = ROOT / "dashboard"
CONTROL = DASH / "local_control.html"


def council_payload() -> dict:
    try:
        from lab.ops.copilots.council import run_council

        return run_council()
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "hint": "git pull origin main; ensure lab/ops/copilots exists",
        }


class Handler(BaseHTTPRequestHandler):
    server_version = "IXLocalControl/1.0"

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("[dash] " + (fmt % args) + "\n")

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path in ("/", "/index.html", "/control"):
            if not CONTROL.exists():
                self._send(404, b"local_control.html missing", "text/plain")
                return
            data = CONTROL.read_bytes()
            self._send(200, data, "text/html; charset=utf-8")
            return
        if path == "/api/health":
            self._send(200, b'{"ok":true,"local":true}', "application/json")
            return
        if path == "/api/council":
            payload = council_payload()
            body = json.dumps(payload, indent=2).encode()
            self._send(200, body, "application/json; charset=utf-8")
            return
        if path.startswith("/dashboard/"):
            rel = path[len("/dashboard/") :]
            target = (DASH / rel).resolve()
            if not str(target).startswith(str(DASH.resolve())) or not target.is_file():
                self._send(404, b"not found", "text/plain")
                return
            ctype = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
            self._send(200, target.read_bytes(), ctype)
            return
        self._send(404, b"not found - try / or /api/council", "text/plain")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="IXPANSION local control dashboard")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8765)
    args = p.parse_args(argv)
    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"IX local control -> http://{args.host}:{args.port}/")
    print(f"  council API    -> http://{args.host}:{args.port}/api/council")
    print("  Ctrl+C to stop")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
