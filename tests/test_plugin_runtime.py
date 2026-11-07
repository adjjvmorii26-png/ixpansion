import json
import tempfile
import unittest
from pathlib import Path

from ixpansion_workbench.runtime import (
    ApprovalClass, Capability, EvidenceLedger, ExecutionContext,
    Outcome, PluginRegistry, PluginRuntime, RetryableAdapterError,
)


class FakeAdapter:
    adapter_id = "fake"

    def __init__(self):
        self.calls = 0
        self.failures_remaining = 0
        self.verification = True

    def capabilities(self):
        return {
            "read": Capability("read"),
            "write": Capability("write", ApprovalClass.REVERSIBLE_WRITE),
            "unsafe": Capability("unsafe", ApprovalClass.DESTRUCTIVE),
            "non_idempotent": Capability(
                "non_idempotent", ApprovalClass.REVERSIBLE_WRITE,
                idempotent=False,
            ),
        }

    def execute(self, capability, payload, context):
        self.calls += 1
        if self.failures_remaining:
            self.failures_remaining -= 1
            raise RetryableAdapterError("temporary provider failure")
        return {"ok": True, "echo": dict(payload)}

    def verify(self, capability, payload, result, context):
        return self.verification


class PluginRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.adapter = FakeAdapter()
        registry = PluginRegistry()
        registry.register(self.adapter)
        self.ledger = EvidenceLedger(Path(self.tmp.name) / "evidence.jsonl")
        self.runtime = PluginRuntime(
            registry, self.ledger, max_attempts=3,
            base_delay_seconds=0, sleeper=lambda _: None,
        )
        self.ctx = ExecutionContext(actor="test", target="fixture")

    def tearDown(self):
        self.tmp.cleanup()

    def test_discovery_lists_capabilities(self):
        self.assertEqual(
            self.runtime.registry.discover(),
            {"fake": ("non_idempotent", "read", "unsafe", "write")},
        )

    def test_destructive_action_requires_approval(self):
        result = self.runtime.execute("fake", "unsafe", {}, self.ctx)
        self.assertEqual(result.outcome, Outcome.BLOCKED)
        self.assertEqual(self.adapter.calls, 0)

    def test_read_completes_and_records_evidence(self):
        result = self.runtime.execute("fake", "read", {"q": "ok"}, self.ctx)
        self.assertEqual(result.outcome, Outcome.VERIFIED)
        self.assertTrue(result.evidence_id)
        self.assertEqual(len(self.ledger.read()), 1)

    def test_idempotent_operation_retries_with_bound(self):
        self.adapter.failures_remaining = 2
        result = self.runtime.execute(
            "fake", "write", {}, ExecutionContext("test", "fixture", approved_for=frozenset({ApprovalClass.REVERSIBLE_WRITE}))
        )
        self.assertEqual(result.outcome, Outcome.VERIFIED)
        self.assertEqual(result.attempts, 3)

    def test_non_idempotent_operation_is_never_retried(self):
        self.adapter.failures_remaining = 1
        result = self.runtime.execute(
            "fake", "non_idempotent", {},
            ExecutionContext("test", "fixture", approved_for=frozenset({ApprovalClass.REVERSIBLE_WRITE})),
        )
        self.assertEqual(result.outcome, Outcome.FAILED)
        self.assertEqual(result.attempts, 1)

    def test_failed_read_after_write_is_unverified(self):
        self.adapter.verification = False
        result = self.runtime.execute(
            "fake", "write", {},
            ExecutionContext("test", "fixture", approved_for=frozenset({ApprovalClass.REVERSIBLE_WRITE})),
        )
        self.assertEqual(result.outcome, Outcome.UNVERIFIED)

    def test_evidence_redacts_secret_fields(self):
        self.ledger.append({"token": "top-secret", "nested": {"api_key": "abc"}})
        raw = self.ledger.path.read_text()
        self.assertNotIn("top-secret", raw)
        self.assertNotIn('"abc"', raw)
        record = json.loads(raw)
        self.assertEqual(record["token"], "[REDACTED]")
        self.assertEqual(record["nested"]["api_key"], "[REDACTED]")

    def test_approval_is_class_specific(self):
        context = ExecutionContext("test", "fixture", approved_for=frozenset({ApprovalClass.REVERSIBLE_WRITE}))
        result = self.runtime.execute("fake", "unsafe", {}, context)
        self.assertEqual(result.outcome, Outcome.BLOCKED)
        self.assertEqual(self.adapter.calls, 0)

    def test_unknown_failure_is_not_retried(self):
        class BrokenAdapter(FakeAdapter):
            def execute(self, capability, payload, context):
                self.calls += 1
                raise PermissionError("insufficient scope")
        adapter = BrokenAdapter()
        registry = PluginRegistry()
        registry.register(adapter)
        runtime = PluginRuntime(registry, self.ledger, max_attempts=4, base_delay_seconds=0, sleeper=lambda _: None)
        result = runtime.execute("fake", "read", {}, self.ctx)
        self.assertEqual(result.outcome, Outcome.FAILED)
        self.assertEqual(result.attempts, 1)

    def test_approval_is_class_specific(self):
        context = ExecutionContext("test", "fixture", approved_for=frozenset({ApprovalClass.REVERSIBLE_WRITE}))
        result = self.runtime.execute("fake", "unsafe", {}, context)
        self.assertEqual(result.outcome, Outcome.BLOCKED)
        self.assertEqual(self.adapter.calls, 0)

    def test_unknown_failure_is_not_retried(self):
        class BrokenAdapter(FakeAdapter):
            def execute(self, capability, payload, context):
                self.calls += 1
                raise PermissionError("insufficient scope")
        adapter = BrokenAdapter()
        registry = PluginRegistry()
        registry.register(adapter)
        runtime = PluginRuntime(registry, self.ledger, max_attempts=4, base_delay_seconds=0, sleeper=lambda _: None)
        result = runtime.execute("fake", "read", {}, self.ctx)
        self.assertEqual(result.outcome, Outcome.FAILED)
        self.assertEqual(result.attempts, 1)

    def test_duplicate_adapter_registration_fails(self):
        with self.assertRaises(ValueError):
            self.runtime.registry.register(self.adapter)


if __name__ == "__main__":
    unittest.main()
