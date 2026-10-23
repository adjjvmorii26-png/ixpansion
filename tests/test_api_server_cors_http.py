"""Exercise actual HTTP responses, not just CORS helper source text."""
import http.client
import json
import threading
from http.server import ThreadingHTTPServer

import pytest

from api.cors_middleware import DEFAULT_HEADERS, MAX_AGE
from api_server import ApiHandler


@pytest.fixture
def server_address(monkeypatch):
    monkeypatch.setenv("IXPANSION_CORS_ORIGINS", "https://trusted.example")
    server = ThreadingHTTPServer(("127.0.0.1", 0), ApiHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server.server_address
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def request(address, method, origin):
    connection = http.client.HTTPConnection(*address, timeout=5)
    try:
        headers = {"Origin": origin} if origin else {}
        connection.request(method, "/health", headers=headers)
        response = connection.getresponse()
        return response.status, response.headers, response.read()
    finally:
        connection.close()


@pytest.mark.parametrize("origin", [None, "https://trusted.example", "https://evil.example"])
def test_health_returns_complete_json_without_optional_preflight_headers(server_address, origin):
    status, headers, body = request(server_address, "GET", origin)
    assert status == 200
    assert json.loads(body)["status"] == "healthy"
    assert int(headers["Content-Length"]) == len(body)
    assert headers["Access-Control-Allow-Origin"] == (origin if origin == "https://trusted.example" else "")
    assert headers["Access-Control-Expose-Headers"] == "X-Request-ID, X-Rate-Limit"


@pytest.mark.parametrize("origin", [None, "https://trusted.example", "https://evil.example"])
def test_options_uses_preflight_policy_without_duplicate_headers(server_address, origin):
    status, headers, body = request(server_address, "OPTIONS", origin)
    assert status == 204
    assert body == b""
    assert headers["Access-Control-Max-Age"] == str(MAX_AGE)
    assert headers["Vary"] == "Origin"
    assert headers["Access-Control-Allow-Origin"] == (origin if origin == "https://trusted.example" else "")
    assert headers.get_all("Access-Control-Allow-Methods") == ["GET, POST, OPTIONS"]
    assert headers.get_all("Access-Control-Allow-Headers") == [", ".join(DEFAULT_HEADERS)]


def test_normal_response_forwards_optional_policy_headers(server_address, monkeypatch):
    from api.cors_middleware import CORSMiddleware

    apply = CORSMiddleware.apply

    def apply_with_vary(self, origin):
        return {**apply(self, origin), "Vary": "Origin"}

    monkeypatch.setattr(CORSMiddleware, "apply", apply_with_vary)
    status, headers, _ = request(server_address, "GET", "https://trusted.example")
    assert status == 200
    assert headers["Vary"] == "Origin"
