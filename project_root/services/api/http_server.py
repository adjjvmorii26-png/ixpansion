"""Lightweight HTTP API server for the engine."""
from __future__ import annotations

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any


class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        routes: dict[str, tuple[int, dict[str, Any]]] = {
            "/health": (200, {"status": "ok"}),
            "/api/agents": (200, self._get_agents()),
            "/api/sandbox": (200, self._get_sandbox()),
        }
        handler = routes.get(self.path)
        if not handler:
            self._respond(404, {"error": "not found"})
            return
        code, body = handler
        self._respond(code, body)

    def _get_agents(self) -> dict[str, Any]:
        return {"agents": [], "count": 0}

    def _get_sandbox(self) -> dict[str, Any]:
        return {"tick": 0, "entities": 0}

    def _respond(self, code: int, body: dict[str, Any]) -> None:
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt: str, *args: Any) -> None:
        pass


def start(port: int = 8100) -> HTTPServer:
    server = HTTPServer(("0.0.0.0", port), APIHandler)
    return server
