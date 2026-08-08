import os
from pathlib import Path
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from swarm_runtime import app, nodes


class SwarmRuntimeTests(unittest.TestCase):
    def setUp(self):
        nodes.clear()
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


if __name__ == "__main__":
    unittest.main()