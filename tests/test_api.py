import unittest

from fastapi.testclient import TestClient

from api.main import app


class ApiTests(unittest.TestCase):
    def test_health_endpoints(self):
        client = TestClient(app)
        self.assertEqual(client.get("/").status_code, 200)
        self.assertEqual(client.get("/health").json(), {"status": "healthy"})