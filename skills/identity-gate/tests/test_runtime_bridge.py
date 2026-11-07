import unittest
from datetime import datetime, timedelta, timezone

from skills.identity_gate.core.authorization import AuthorizationGrant
from skills.identity_gate.core.runtime_bridge import GrantRejected, execute_authorized
from ixpansion_workbench.runtime import ExecutionContext


NOW = datetime(2026, 11, 7, 12, tzinfo=timezone.utc)


class Runtime:
    def __init__(self):
        self.calls = []
    def execute(self, adapter_id, capability_name, payload, context):
        self.calls.append((adapter_id, capability_name, payload, context))
        return "dispatched"


def grant(**overrides):
    values = dict(actor_subject="actor", tenant_id="tenant",
                  resource_id="repo:one", operation="modify_file", risk="R2",
                  issued_at=NOW - timedelta(seconds=1),
                  expires_at=NOW + timedelta(minutes=1), request_id="req-1")
    values.update(overrides)
    return AuthorizationGrant(**values)


def context(**overrides):
    values = dict(actor="actor", target="repo:one", request_id="req-1")
    values.update(overrides)
    return ExecutionContext(**values)


class RuntimeBridgeTests(unittest.TestCase):
    def test_valid_scoped_grant_dispatches_with_narrow_risk_class(self):
        runtime = Runtime()
        result = execute_authorized(runtime=runtime, adapter_id="github",
            capability_name="write_file", payload={}, context=context(),
            grant=grant(), operation="modify_file", now=NOW)
        self.assertEqual(result, "dispatched")
        self.assertEqual(len(runtime.calls), 1)
        self.assertEqual(runtime.calls[0][3].approved_for.pop().value, "sensitive_write")

    def test_wrong_actor_is_rejected_before_dispatch(self):
        runtime = Runtime()
        with self.assertRaises(GrantRejected):
            execute_authorized(runtime=runtime, adapter_id="github",
                capability_name="write_file", payload={}, context=context(actor="intruder"),
                grant=grant(), operation="modify_file", now=NOW)
        self.assertEqual(runtime.calls, [])

    def test_wrong_resource_is_rejected_before_dispatch(self):
        runtime = Runtime()
        with self.assertRaises(GrantRejected):
            execute_authorized(runtime=runtime, adapter_id="github",
                capability_name="write_file", payload={}, context=context(target="repo:two"),
                grant=grant(), operation="modify_file", now=NOW)
        self.assertEqual(runtime.calls, [])

    def test_expired_grant_is_rejected_before_dispatch(self):
        runtime = Runtime()
        with self.assertRaises(GrantRejected):
            execute_authorized(runtime=runtime, adapter_id="github",
                capability_name="write_file", payload={}, context=context(),
                grant=grant(expires_at=NOW), operation="modify_file", now=NOW)
        self.assertEqual(runtime.calls, [])

    def test_wrong_operation_is_rejected_before_dispatch(self):
        runtime = Runtime()
        with self.assertRaises(GrantRejected):
            execute_authorized(runtime=runtime, adapter_id="github",
                capability_name="write_file", payload={}, context=context(),
                grant=grant(), operation="delete", now=NOW)
        self.assertEqual(runtime.calls, [])


if __name__ == "__main__":
    unittest.main()
