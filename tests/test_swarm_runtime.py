import os
from pathlib import Path
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from swarm_runtime import app, nodes, tasks


class SwarmRuntimeTests(unittest.TestCase):
    def setUp(self):
        nodes.clear()
        tasks.clear()
        self.client = TestClient(app)

    def test_health_is_public_and_registration_requires_token(self):
        with patch.dict(os.environ, {"SWARM_ROLE": "hub", "SWARM_TOKEN": "secret"}):
            self.assertEqual(self.client.get("/health").json()["role"], "hub")
            self.assertEqual(self.client.post("/register?node_id=node-1").status_code, 401)
            response = self.client.post(
                "/register?node_id=node-1",
                headers={"X-Swarm-Token": "secret"},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["node_id"], "node-1")

    def test_status_requires_token_and_lists_registered_nodes(self):
        with patch.dict(os.environ, {"SWARM_TOKEN": "secret"}):
            self.client.post("/register?node_id=node-1", headers={"X-Swarm-Token": "secret"})
            response = self.client.get("/status", headers={"X-Swarm-Token": "secret"})
            self.assertEqual(response.status_code, 200)
            self.assertIn("node-1", response.json()["nodes"])

    def test_empty_token_enables_local_swarm_mode(self):
        with patch.dict(os.environ, {"SWARM_TOKEN": ""}, clear=False):
            register = self.client.post("/register?node_id=local-node")
            status = self.client.get("/status")
        self.assertEqual(register.status_code, 200)
        self.assertEqual(status.status_code, 200)
        self.assertIn("local-node", status.json()["nodes"])

    def test_swarm_services_do_not_publish_host_ports(self):
        compose = Path(__file__).parents[1].joinpath("compose.yaml").read_text()
        self.assertNotIn('"8765:8765"', compose)
        self.assertNotIn('"8080:8080"', compose)

    def test_heartbeat_updates_node_capacity_and_health(self):
        with patch.dict(os.environ, {"SWARM_TOKEN": "secret"}):
            headers = {"X-Swarm-Token": "secret"}
            self.client.post("/register?node_id=node-1", headers=headers)
            response = self.client.post(
                "/heartbeat",
                headers=headers,
                json={"node_id": "node-1", "load": 0.25, "capacity": 0.75, "health": 1.0},
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["state"]["capacity"], 0.75)
        self.assertEqual(response.json()["state"]["status"], "ready")

    def test_task_queue_leases_and_completes_once(self):
        with patch.dict(os.environ, {"SWARM_TOKEN": "secret"}):
            headers = {"X-Swarm-Token": "secret"}
            self.client.post("/register?node_id=node-1", headers=headers)
            queued = self.client.post(
                "/tasks", headers=headers, json={"task": "Inspect the mesh", "task_id": "task-1"}
            )
            claimed = self.client.get("/tasks/claim?node_id=node-1", headers=headers)
            completed = self.client.post(
                "/tasks/task-1/complete",
                headers=headers,
                json={"node_id": "node-1", "result": "mesh inspected"},
            )
            replay = self.client.post(
                "/tasks/task-1/complete",
                headers=headers,
                json={"node_id": "node-1", "result": "different result"},
            )
        self.assertEqual(queued.json()["status"], "queued")
        self.assertEqual(claimed.json()["task"]["task_id"], "task-1")
        self.assertEqual(completed.json()["task"]["status"], "completed")
        self.assertTrue(replay.json()["replayed"])

    def test_task_completion_rejects_wrong_node(self):
        with patch.dict(os.environ, {"SWARM_TOKEN": "secret"}):
            headers = {"X-Swarm-Token": "secret"}
            self.client.post("/register?node_id=node-1", headers=headers)
            self.client.post("/register?node_id=node-2", headers=headers)
            self.client.post("/tasks", headers=headers, json={"task": "Bounded work", "task_id": "task-2"})
            self.client.get("/tasks/claim?node_id=node-1", headers=headers)
            response = self.client.post(
                "/tasks/task-2/complete",
                headers=headers,
                json={"node_id": "node-2"},
            )
        self.assertEqual(response.status_code, 409)

    def test_degraded_node_cannot_claim_work(self):
        with patch.dict(os.environ, {"SWARM_TOKEN": "secret"}):
            headers = {"X-Swarm-Token": "secret"}
            self.client.post("/register?node_id=node-1", headers=headers)
            self.client.post(
                "/heartbeat",
                headers=headers,
                json={"node_id": "node-1", "health": 0.2, "capacity": 0.8, "load": 0.1},
            )
            self.client.post("/tasks", headers=headers, json={"task": "Do not assign"})
            response = self.client.get("/tasks/claim?node_id=node-1", headers=headers)
        self.assertEqual(response.status_code, 409)

    def test_invalid_heartbeat_values_are_rejected(self):
        with patch.dict(os.environ, {"SWARM_TOKEN": "secret"}):
            headers = {"X-Swarm-Token": "secret"}
            self.client.post("/register?node_id=node-1", headers=headers)
            response = self.client.post(
                "/heartbeat",
                headers=headers,
                json={"node_id": "node-1", "load": 1.1},
            )
        self.assertEqual(response.status_code, 422)

    def test_expired_lease_is_requeued_for_another_node(self):
        with patch.dict(os.environ, {"SWARM_TOKEN": "secret"}):
            headers = {"X-Swarm-Token": "secret"}
            self.client.post("/register?node_id=node-1", headers=headers)
            self.client.post("/register?node_id=node-2", headers=headers)
            self.client.post("/tasks", headers=headers, json={"task": "Retry me", "task_id": "task-expired"})
            self.client.get("/tasks/claim?node_id=node-1", headers=headers)
            tasks["task-expired"]["lease_expires_at"] = 0
            response = self.client.get("/tasks/claim?node_id=node-2", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["task"]["assigned_to"], "node-2")

    def test_queue_limit_is_bounded_but_duplicate_replays(self):
        with patch.dict(os.environ, {"SWARM_TOKEN": "secret"}), patch("swarm_runtime.MAX_TASKS", 1):
            headers = {"X-Swarm-Token": "secret"}
            first = self.client.post("/tasks", headers=headers, json={"task": "One", "task_id": "task-one"})
            full = self.client.post("/tasks", headers=headers, json={"task": "Two", "task_id": "task-two"})
            replay = self.client.post("/tasks", headers=headers, json={"task": "Changed", "task_id": "task-one"})
        self.assertEqual(first.status_code, 200)
        self.assertEqual(full.status_code, 429)
        self.assertEqual(replay.status_code, 200)
        self.assertTrue(replay.json()["replayed"])


if __name__ == "__main__":
    unittest.main()