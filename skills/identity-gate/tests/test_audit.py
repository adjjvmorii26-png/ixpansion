import unittest
import importlib
_audit = importlib.import_module("skills.identity-gate.core.audit")
AuditEvent, redact = _audit.AuditEvent, _audit.redact


class AuditTests(unittest.TestCase):
    def test_secret_keys_are_redacted(self):
        self.assertEqual(redact({"api_key": "do-not-log"})["api_key"], "[REDACTED]")

    def test_bearer_values_are_redacted(self):
        self.assertNotIn("abc123", str(redact({"header": "Bearer abc123"})))

    def test_event_id_is_stable_for_same_event(self):
        event = AuditEvent("a", "oidc", "owner", "repo:1", "inspect",
                           "resource.read", None, None, "ALLOW",
                           occurred_at=__import__("datetime").datetime(2026, 1, 1, tzinfo=__import__("datetime").timezone.utc))
        self.assertEqual(event.normalized()["event_id"], event.normalized()["event_id"])


if __name__ == "__main__":
    unittest.main()
