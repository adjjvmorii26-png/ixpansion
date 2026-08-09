import unittest

from fastapi.testclient import TestClient

from api.main import app


class ApiTests(unittest.TestCase):
    def test_health_endpoints(self):
        client = TestClient(app)
        self.assertEqual(client.get("/").status_code, 200)
        self.assertEqual(client.get("/health").json(), {"status": "healthy"})

    def test_aether_foundation_snapshot_and_dispatch(self):
        client = TestClient(app)
        snapshot = client.get("/aether")
        self.assertEqual(snapshot.status_code, 200)
        self.assertEqual(snapshot.json()["name"], "aether-lattice")
        dispatch = client.post(
            "/aether/dispatch",
            json={"task": "Inspect the lattice", "task_id": "api-task-1"},
        )
        self.assertEqual(dispatch.status_code, 200)
        self.assertEqual(dispatch.json()["task_id"], "api-task-1")
        self.assertIn("agent", dispatch.json())

    def test_aether_workflows_are_listed_and_runnable(self):
        client = TestClient(app)
        workflows = client.get("/aether/workflows").json()["workflows"]
        self.assertEqual(len(workflows), 6)
        response = client.post(
            "/aether/workflows/extract_tasks",
            json={"text": "TODO: inspect API"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["result"], "Tasks:\n- inspect API")

    def test_aether_data_can_be_saved_and_reused(self):
        client = TestClient(app)
        saved = client.put("/aether/data/reusable-note", json={"value": {"ready": True}})
        self.assertEqual(saved.status_code, 200)
        loaded = client.get("/aether/data/reusable-note")
        self.assertEqual(loaded.json(), {"key": "reusable-note", "value": {"ready": True}})

    def test_recycle_endpoint_returns_bounded_context_artifact(self):
        client = TestClient(app)
        response = client.post(
            "/aether/recycle",
            json={
                "text": "TOKEN=secret-value\nFirst fact.\nFirst fact.",
                "chunk_size": 64,
                "task_id": "api-recycle-1",
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["data_key"], "api-recycle-1")
        self.assertTrue(payload["redacted"])
        self.assertNotIn("secret-value", response.text)
        self.assertGreaterEqual(payload["approximate_tokens"], 1)

    def test_recycle_endpoint_rejects_invalid_chunk_size(self):
        response = TestClient(app).post(
            "/aether/recycle",
            json={"text": "source text", "chunk_size": 10},
        )
        self.assertEqual(response.status_code, 422)

    def test_context_retrieval_endpoint_returns_bounded_chunks(self):
        client = TestClient(app)
        client.post(
            "/aether/recycle",
            json={
                "text": "alpha unrelated.\nbeta database migration.",
                "chunk_size": 64,
                "task_id": "api-retrieve-1",
            },
        )
        response = client.post(
            "/aether/context/api-retrieve-1/retrieve",
            json={"query": "database", "max_tokens": 20},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data_key"], "api-retrieve-1")
        self.assertLessEqual(response.json()["approximate_tokens"], 20)

    def test_context_retrieval_endpoint_reports_missing_data(self):
        response = TestClient(app).post(
            "/aether/context/missing-retrieve/retrieve",
            json={},
        )
        self.assertEqual(response.status_code, 404)

    def test_dashboard_is_a_browser_page(self):
        response = TestClient(app).get("/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        self.assertIn("IXPANSION / Control Room", response.text)
        self.assertIn("Automation workflows", response.text)
        self.assertIn("data-workflow", response.text)

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