import os
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


if __name__ == "__main__":
    unittest.main()