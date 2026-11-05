"""Local control server must not expose private council data cross-origin."""
import http.client
import threading
from http.server import ThreadingHTTPServer

from lab.ops.dashboard_server import Handler


def test_local_control_api_does_not_grant_wildcard_cross_origin_reads():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        connection = http.client.HTTPConnection(*server.server_address, timeout=5)
        try:
            connection.request(
                "GET",
                "/api/health",
                headers={"Origin": "https://untrusted.example"},
            )
            response = connection.getresponse()
            response.read()
            assert response.status == 200
            assert response.getheader("Access-Control-Allow-Origin") is None
        finally:
            connection.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
