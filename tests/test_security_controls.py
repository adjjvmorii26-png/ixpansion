import tempfile
import unittest
from pathlib import Path

from security_controls import API_AUTOMATION, AuditStore, HumanGate, TrustStore, URLPolicy


class SecurityControlsTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.audit = AuditStore(str(Path(self.directory.name) / "audit.sqlite3"))
        self.trust = TrustStore()
        self.gate = HumanGate(self.audit, self.trust)

    def tearDown(self):
        self.audit.close()
        self.directory.cleanup()

    def test_audits_persist_and_production_requires_two_operators(self):
        self.assertEqual(self.gate.request("task-1", ["PROD_DEPLOY"], "alice"), "PENDING_DUAL_CONTROL")
        self.assertEqual(self.gate.approve("task-1", "alice"), "REJECTED_DUAL_CONTROL")
        self.assertEqual(self.gate.approve("task-1", "bob"), "APPROVED")
        decisions = [row[-1] for row in self.audit.decisions("task-1")]
        self.assertEqual(decisions, ["PENDING_DUAL_CONTROL", "REJECTED_DUAL_CONTROL", "APPROVED"])

    def test_approval_rechecks_current_trust(self):
        self.gate.request("task-2", ["PROD_DEPLOY"], "alice")
        self.trust.observe("agent:alice", False, alpha=1.0)
        self.assertEqual(self.gate.approve("task-2", "bob"), "REJECTED_LOW_TRUST")

    def test_dry_run_and_url_allowlist(self):
        automation = API_AUTOMATION(URLPolicy({"api.example.com"}), dry_run=True)
        self.assertEqual(automation.post("https://api.example.com/deploy"), "DRY_RUN: POST https://api.example.com/deploy")
        with self.assertRaises(PermissionError):
            automation.post("https://api.internal.net/deploy")

    def test_trust_is_namespaced_and_idle_decay_is_conservative(self):
        self.trust.observe("agent:worker-1", True, alpha=1.0)
        self.trust.observe("node:worker-1", False, alpha=1.0)
        self.assertAlmostEqual(self.trust.trust("agent:worker-1"), 1.0)
        self.assertAlmostEqual(self.trust.trust("node:worker-1"), 0.0)
        self.assertLess(
            self.trust.trust("agent:never-ran", now=self.trust.started_at + 86400),
            0.5,
        )


if __name__ == "__main__":
    unittest.main()