import unittest

from api.apoen_somatic_gc import (
    GCPolicy,
    SomaticGarbageCollector,
    handler,
    sign_heartbeat,
    verify_heartbeat,
    verify_receipt,
)


class SomaticGarbageCollectorTests(unittest.TestCase):
    def setUp(self):
        self.gc = SomaticGarbageCollector(
            "CLUSTER-OMEGA",
            GCPolicy(stale_after_seconds=100, minimum_age_seconds=500, maximum_interactions=2),
        )

    def test_old_stale_inactive_branch_is_candidate_only(self):
        metadata = {"created_at": 100, "last_heartbeat": 200, "interaction_count": 1}
        out = self.gc.evaluate_branch("branch-a", metadata, now=1000)
        self.assertTrue(out["eligible"])
        self.assertEqual(out["decision"], "CANDIDATE")
        self.assertFalse(out["destructive_action_performed"])

    def test_recent_heartbeat_retains_branch(self):
        metadata = {"created_at": 100, "last_heartbeat": 950, "interaction_count": 0}
        out = self.gc.evaluate_branch("branch-a", metadata, now=1000)
        self.assertFalse(out["eligible"])
        self.assertEqual(out["decision"], "RETAIN")

    def test_missing_telemetry_fails_closed(self):
        out = self.gc.evaluate_branch("branch-a", {"created_at": 1}, now=1000)
        self.assertEqual(out["reason"], "missing_telemetry")
        self.assertFalse(out["eligible"])

    def test_invalid_numeric_telemetry_fails_closed(self):
        out = self.gc.evaluate_branch(
            "branch-a",
            {"created_at": "bad", "last_heartbeat": 1, "interaction_count": 0},
            now=1000,
        )
        self.assertEqual(out["reason"], "invalid_telemetry")
        self.assertFalse(out["eligible"])

    def test_hmac_detects_heartbeat_tampering(self):
        payload = {"node": "agent-7", "sequence": 12, "last_seen": 900}
        signature = sign_heartbeat(payload, b"test-secret")
        self.assertTrue(verify_heartbeat(payload, signature, b"test-secret"))
        self.assertFalse(verify_heartbeat({**payload, "sequence": 13}, signature, b"test-secret"))
        self.assertFalse(verify_heartbeat(payload, signature, b"wrong-secret"))

    def test_receipt_is_deterministic_and_tamper_evident(self):
        evaluation = self.gc.evaluate_branch(
            "branch-a",
            {"created_at": 100, "last_heartbeat": 200, "interaction_count": 1},
            now=1000,
        )
        first = self.gc.seal_receipt(evaluation, previous_seal="parent")
        second = self.gc.seal_receipt(evaluation, previous_seal="parent")
        self.assertEqual(first["seal"], second["seal"])
        self.assertTrue(verify_receipt(first))
        changed = {**first, "evaluation": {**evaluation, "decision": "PRUNE"}}
        self.assertFalse(verify_receipt(changed))

    def test_receipt_chain_binds_previous_seal(self):
        evaluation = {"branch_id": "b", "decision": "RETAIN"}
        a = self.gc.seal_receipt(evaluation)
        b = self.gc.seal_receipt(evaluation, previous_seal=a["seal"])
        c = self.gc.seal_receipt(evaluation, previous_seal="different-parent")
        self.assertTrue(verify_receipt(b))
        self.assertNotEqual(b["seal"], c["seal"])

    def test_authenticated_heartbeat_is_bound_to_branch_and_cluster(self):
        metadata = {"created_at": 100, "last_heartbeat": 200, "interaction_count": 1}
        heartbeat = {"branch_id": "branch-a", "cluster_id": "CLUSTER-OMEGA", "created_at": 100, "last_heartbeat": 200, "interaction_count": 1}
        signature = sign_heartbeat(heartbeat, b"test-secret")
        out = self.gc.evaluate_authenticated_branch(
            "branch-a", metadata, heartbeat, signature, b"test-secret", now=1000
        )
        self.assertTrue(out["eligible"])
        wrong_branch = {**heartbeat, "branch_id": "branch-b"}
        out = self.gc.evaluate_authenticated_branch(
            "branch-a", metadata, wrong_branch,
            sign_heartbeat(wrong_branch, b"test-secret"), b"test-secret", now=1000
        )
        self.assertEqual(out["reason"], "heartbeat_binding_mismatch")
        self.assertFalse(out["eligible"])

    def test_authenticated_heartbeat_binds_decision_bearing_activity_fields(self):
        metadata = {"created_at": 100, "last_heartbeat": 200, "interaction_count": 1}
        heartbeat = {"branch_id": "branch-a", "cluster_id": "CLUSTER-OMEGA",
                     "created_at": 100, "last_heartbeat": 200, "interaction_count": 1}
        signature = sign_heartbeat(heartbeat, b"test-secret")
        tampered = {**metadata, "interaction_count": 0}
        out = self.gc.evaluate_authenticated_branch(
            "branch-a", tampered, heartbeat, signature, b"test-secret", now=1000
        )
        self.assertEqual(out["reason"], "heartbeat_binding_mismatch")
        self.assertFalse(out["eligible"])

    def test_invalid_signature_cannot_make_branch_candidate(self):
        metadata = {"created_at": 100, "last_heartbeat": 200, "interaction_count": 1}
        heartbeat = {"branch_id": "branch-a", "cluster_id": "CLUSTER-OMEGA", "last_heartbeat": 200}
        out = self.gc.evaluate_authenticated_branch(
            "branch-a", metadata, heartbeat, "bad-signature", b"test-secret", now=1000
        )
        self.assertEqual(out["reason"], "invalid_heartbeat")
        self.assertFalse(out["eligible"])

    def test_live_lineage_and_leases_are_never_candidates(self):
        base = {"created_at": 100, "last_heartbeat": 200, "interaction_count": 1}
        for guard in ("protected", "has_live_descendants", "active_lease"):
            with self.subTest(guard=guard):
                out = self.gc.evaluate_branch("branch-a", {**base, guard: True}, now=1000)
                self.assertEqual(out["reason"], "lineage_or_lease_protected")
                self.assertFalse(out["eligible"])
                self.assertFalse(out["destructive_action_performed"])

    def test_boolean_and_future_timestamps_fail_closed(self):
        base = {"created_at": 100, "last_heartbeat": 200, "interaction_count": 1}
        out = self.gc.evaluate_branch("branch-a", {**base, "interaction_count": True}, now=1000)
        self.assertEqual(out["reason"], "invalid_telemetry")
        out = self.gc.evaluate_branch("branch-a", {**base, "last_heartbeat": 1001}, now=1000)
        self.assertEqual(out["reason"], "future_timestamp")

    def test_status_is_non_destructive(self):
        out = handler()
        self.assertEqual(out["mode"], "policy_only")
        self.assertFalse(out["destructive_actions_enabled"])


if __name__ == "__main__":
    unittest.main()
