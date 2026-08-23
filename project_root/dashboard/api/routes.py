from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from typing import Any

from .controllers import AgentController, SandboxController, TelemetryController


class NexusAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        routes: dict[str, Callable[[], tuple[int, dict[str, Any]]]] = {
            "/api/agents": lambda: (200, AgentController.list()),
            "/api/sandbox/status": lambda: SandboxController.status(),
            "/api/telemetry": lambda: TelemetryController.snapshot(),
            "/health": lambda: (200, {"status": "healthy"}),
        }
        handler = routes.get(self.path)
        if not handler:
            self._respond(404, {"error": "not found"})
            return
        code, body = handler()
        self._respond(code, body)

    def _respond(self, code: int, body: dict[str, Any]) -> None:
        data = json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt: str, *args: Any) -> None:
        pass  # Suppress default request logging


def start_server(port: int = 8080) -> None:
    server = HTTPServer(("0.0.0.0", port), NexusAPIHandler)
    print(f"Dashboard API listening on :{port}")
    server.serve_forever()
