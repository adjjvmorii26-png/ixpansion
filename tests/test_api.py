import unittest

from fastapi.testclient import TestClient

from api.main import app


class ApiTests(unittest.TestCase):
    def test_health_endpoints(self):
        client = TestClient(app)
        self.assertEqual(client.get("/").status_code, 200)
        self.assertEqual(client.get("/health").json(), {"status": "healthy"})

    def test_dashboard_is_a_browser_page(self):
        response = TestClient(app).get("/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        self.assertIn("IXPANSION / Control Room", response.text)

    def test_skill_discovery_and_execution(self):
        client = TestClient(app)
        skills = client.get("/skills")
        self.assertEqual(skills.status_code, 200)
        self.assertTrue(any(item["name"] == "summarize" for item in skills.json()["skills"]))
        response = client.post("/skills/summarize", json={"text": "Inspect the API. Then test."})
        self.assertEqual(response.json(), {"skill": "summarize", "result": "Summary: Inspect the API."})
        self.assertEqual(client.post("/skills/missing", json={}).status_code, 404)

    def test_lattice_status_heartbeat_and_allocation(self):
        client = TestClient(app)
        status = client.get("/lattice")
        self.assertEqual(status.status_code, 200)
        self.assertIn("states", status.json())
        heartbeat = client.post(
            "/lattice/heartbeat",
            json={"machine_id": "api-reuse-0", "load": 0.2},
        )
        self.assertEqual(heartbeat.status_code, 200)
        allocation = client.post(
            "/lattice/allocate",
            json={"task": "reclaimable batch", "lease_seconds": 30},
        )
        self.assertEqual(allocation.status_code, 200)
        self.assertEqual(allocation.json()["leased"], True)