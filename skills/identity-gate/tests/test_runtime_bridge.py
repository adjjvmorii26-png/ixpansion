import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone

import importlib
_auth = importlib.import_module("skills.identity-gate.core.authorization")
_bridge = importlib.import_module("skills.identity-gate.core.runtime_bridge")
AuthorizationGrant = _auth.AuthorizationGrant
GrantRejected, execute_authorized = _bridge.GrantRejected, _bridge.execute_authorized
_grant_authority = _core.HMACGrantAuthority(b"test-grant-signing-key-32-bytes!!")
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
    unsigned = AuthorizationGrant(**values)
    signature = _grant_authority.sign(_auth.grant_payload(unsigned))
    return replace(unsigned, signature=signature)


def context(**overrides):
    values = dict(actor="actor", target="repo:one", request_id="req-1")
    values.update(overrides)
    return ExecutionContext(**values)


class RuntimeBridgeTests(unittest.TestCase):
    def test_valid_scoped_grant_dispatches_with_narrow_risk_class(self):
        runtime = Runtime()
        result = execute_authorized(runtime=runtime, adapter_id="github",
            capability_name="write_file", payload={}, context=context(),
            grant=grant(), grant_authority=_grant_authority, verified_tenant_id="tenant", operation="modify_file", now=NOW)
        self.assertEqual(result, "dispatched")
        self.assertEqual(len(runtime.calls), 1)
        self.assertEqual(next(iter(runtime.calls[0][3].approved_for)).value, "sensitive_write")

    def test_wrong_actor_is_rejected_before_dispatch(self):
        runtime = Runtime()
        with self.assertRaises(GrantRejected):
            execute_authorized(runtime=runtime, adapter_id="github",
                capability_name="write_file", payload={}, context=context(actor="intruder"),
                grant=grant(), grant_authority=_grant_authority, verified_tenant_id="tenant", operation="modify_file", now=NOW)
        self.assertEqual(runtime.calls, [])

    def test_wrong_resource_is_rejected_before_dispatch(self):
        runtime = Runtime()
        with self.assertRaises(GrantRejected):
            execute_authorized(runtime=runtime, adapter_id="github",
                capability_name="write_file", payload={}, context=context(target="repo:two"),
                grant=grant(), grant_authority=_grant_authority, verified_tenant_id="tenant", operation="modify_file", now=NOW)
        self.assertEqual(runtime.calls, [])

    def test_expired_grant_is_rejected_before_dispatch(self):
        runtime = Runtime()
        with self.assertRaises(GrantRejected):
            execute_authorized(runtime=runtime, adapter_id="github",
                capability_name="write_file", payload={}, context=context(),
                grant=grant(expires_at=NOW), grant_authority=_grant_authority, verified_tenant_id="tenant", operation="modify_file", now=NOW)
        self.assertEqual(runtime.calls, [])

    def test_wrong_operation_is_rejected_before_dispatch(self):
        runtime = Runtime()
        with self.assertRaises(GrantRejected):
            execute_authorized(runtime=runtime, adapter_id="github",
                capability_name="write_file", payload={}, context=context(),
                grant=grant(), grant_authority=_grant_authority, verified_tenant_id="tenant", operation="delete", now=NOW)
        self.assertEqual(runtime.calls, [])

    def test_forged_grant_signature_is_rejected(self):
        runtime = Runtime()
        forged = replace(grant(), signature="forged")
        with self.assertRaises(GrantRejected):
            execute_authorized(runtime=runtime, adapter_id="github",
                capability_name="write_file", payload={}, context=context(),
                grant=forged, grant_authority=_grant_authority,
                verified_tenant_id="tenant", operation="modify_file", now=NOW)
        self.assertEqual(runtime.calls, [])

    def test_wrong_verified_tenant_is_rejected(self):
        runtime = Runtime()
        with self.assertRaises(GrantRejected):
            execute_authorized(runtime=runtime, adapter_id="github",
                capability_name="write_file", payload={}, context=context(),
                grant=grant(), grant_authority=_grant_authority,
                verified_tenant_id="tenant-b", operation="modify_file", now=NOW)
        self.assertEqual(runtime.calls, [])


if __name__ == "__main__":
    unittest.main()
