import unittest

from api.atlas_trace_wrapper import AtlasTraceWrapper, KGValidationWrapper, WrapperError


class TestWrapperVerificationSuite(unittest.TestCase):
    def setUp(self):
        self.atlas = AtlasTraceWrapper()
        self.kg = KGValidationWrapper(sandbox_verified=False)

    def assert_code(self, code, call):
        with self.assertRaises(WrapperError) as ctx:
            call()
        self.assertEqual(ctx.exception.code, code)

    def test_atlas_missing_anchor(self):
        self.assert_code("MISSING_ANCHOR", lambda: self.atlas.execute("Trace node", "ANCHORED_TRACE"))

    def test_atlas_rejected_mutation(self):
        self.assert_code("REJECTED_OPERATION", lambda: self.atlas.execute("Fix paradox", "ANCHORED_TRACE", anchor="MEM-KG0001-CORE", operation="PARADOX_RESOLUTION"))

    def test_atlas_missing_access(self):
        self.assert_code("MISSING_ACCESS", lambda: self.atlas.execute("Trace restricted node", "ANCHORED_TRACE", anchor="SECRET-NODE-999"))

    def test_kg_sandbox_unavailable(self):
        self.assert_code("SANDBOX_UNAVAILABLE", lambda: self.kg.execute("Run custom validator script", "STATIC_ANALYSIS", execute_code=True))

    def test_kg_rejected_wal_rewrite(self):
        self.assert_code("REJECTED_OPERATION", lambda: self.kg.execute("Rewrite WAL entries", "STATIC_ANALYSIS", operation="WAL_REWRITE"))

    def test_kg_missing_schema_access(self):
        self.assert_code("MISSING_ACCESS", lambda: self.kg.execute("Validate custom schema", "STATIC_ANALYSIS", schema_id="MALFORMED_SCHEMA"))

    def test_atlas_unknown_operation_rejected(self):
        self.assert_code("REJECTED_OPERATION", lambda: self.atlas.execute("Trace node", "ANCHORED_TRACE", anchor="MEM-KG0001-CORE", operation="ANCHORED_TRAC"))

    def test_scope_operation_mismatch_rejected(self):
        self.assert_code("REJECTED_OPERATION", lambda: self.atlas.execute("Scan atlas", "READ_ONLY_WHOLE_ATLAS_SCAN", operation="ANCHORED_TRACE"))

    def test_unknown_scope_rejected(self):
        self.assert_code("INVALID_SCOPE_MODE", lambda: self.atlas.execute("Trace", "ADMIN_OVERRIDE"))

    def test_empty_access_list_denies_every_page(self):
        wrapper = AtlasTraceWrapper(accessible_pages=set())
        self.assert_code("MISSING_ACCESS", lambda: wrapper.execute("Trace", "ANCHORED_TRACE", anchor="MEM-KG0001-CORE"))

    def test_access_policy_is_immutable(self):
        with self.assertRaises(AttributeError):
            self.atlas.accessible_pages.add("SECRET-NODE-999")

    def test_whole_scan_denied_without_explicit_grant(self):
        self.assert_code("MISSING_ACCESS", lambda: self.atlas.execute("Scan atlas", "READ_ONLY_WHOLE_ATLAS_SCAN"))

    def test_whole_scan_allowed_with_grant_and_no_anchor(self):
        wrapper = AtlasTraceWrapper(whole_atlas_authorized=True)
        result = wrapper.execute("Scan atlas", "READ_ONLY_WHOLE_ATLAS_SCAN")
        self.assertEqual(result["result"], "SUCCESS")

    def test_whole_scan_rejects_anchor_even_with_grant(self):
        wrapper = AtlasTraceWrapper(whole_atlas_authorized=True)
        self.assert_code("INVALID_PARAMETERS", lambda: wrapper.execute("Scan atlas", "READ_ONLY_WHOLE_ATLAS_SCAN", anchor="MEM-KG0001-CORE"))

    def test_whole_atlas_flag_requires_exact_boolean(self):
        with self.assertRaises(TypeError):
            AtlasTraceWrapper(whole_atlas_authorized=1)

    def test_sandbox_flag_requires_exact_boolean(self):
        with self.assertRaises(TypeError):
            KGValidationWrapper(sandbox_verified=1)

    def test_explicit_empty_schema_set_denies_every_schema(self):
        wrapper = KGValidationWrapper(accessible_schemas=set())
        self.assert_code("MISSING_ACCESS", lambda: wrapper.execute("Validate", "STATIC_ANALYSIS", schema_id="WAL_ENTRY_SCHEMA"))

    def test_input_data_must_be_mapping(self):
        self.assert_code("SKILL_LOGIC_VIOLATION", lambda: self.atlas.execute("Trace", "ANCHORED_TRACE", anchor="MEM-KG0001-CORE", input_data=[]))

    def test_magic_invalid_schema_key_is_rejected(self):
        self.assert_code("SKILL_LOGIC_VIOLATION", lambda: self.atlas.execute("Trace", "ANCHORED_TRACE", anchor="MEM-KG0001-CORE", input_data={"invalid_schema_key": True}))


if __name__ == "__main__":
    unittest.main()
