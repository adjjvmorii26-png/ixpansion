from __future__ import annotations

import base64
import json
import unittest

from integrations.kitebridge.kitesurf import (
    KitesurfBrowserAdapter,
    KitesurfConfigurationError,
    KitesurfPolicyError,
    KitesurfProtocolError,
)


class FakeTransport:
    def __init__(self, *, status=200, response=None):
        self.status = status
        self.response = response or {
            "success": True,
            "result": {
                "markdown": "# Example\n\nPublic page content.",
                "screenshot": base64.b64encode(b"fake-png-bytes").decode("ascii"),
                "accessibilityTree": {"role": "RootWebArea", "name": "Example"},
            },
            "meta": {"status": 200, "title": "Example"},
        }
        self.calls = []

    def __call__(self, method, url, headers, body, timeout):
        self.calls.append((method, url, headers, json.loads(body), timeout))
        return self.status, self.response


class KitesurfAdapterTests(unittest.TestCase):
    def adapter(self, fake=None):
        return KitesurfBrowserAdapter(
            account_id="account-1", token="test-token",
            allowed_hosts={"docs.example.com"}, transport=fake or FakeTransport(),
        )

    def test_missing_configuration_fails_closed(self):
        with self.assertRaises(KitesurfConfigurationError):
            KitesurfBrowserAdapter(account_id="", token="", allowed_hosts={"docs.example.com"})

    def test_exact_allowlist_and_https_are_required(self):
        adapter = self.adapter()
        self.assertEqual(adapter.validate_url("https://docs.example.com/guide?q=1"),
                         "https://docs.example.com/guide?q=1")
        rejected = (
            "http://docs.example.com/", "https://sub.docs.example.com/",
            "https://docs.example.com.evil.test/", "https://user@docs.example.com/",
            "https://127.0.0.1/", "https://docs.example.com:8443/",
            "https://docs.example.com/#fragment", "file:///etc/passwd",
        )
        for url in rejected:
            with self.subTest(url=url), self.assertRaises(KitesurfPolicyError):
                adapter.validate_url(url)

    def test_capture_uses_kitesurf_snapshot_and_no_page_credentials(self):
        fake = FakeTransport()
        evidence = self.adapter(fake).capture("https://docs.example.com/guide", task_id="test-1")
        method, endpoint, headers, payload, timeout = fake.calls[0]
        self.assertEqual(method, "POST")
        self.assertIn("/browser-run/snapshot?browser=kitesurf", endpoint)
        self.assertEqual(payload["formats"], ["markdown", "screenshot", "accessibilityTree"])
        self.assertEqual(payload["url"], "https://docs.example.com/guide")
        self.assertNotIn("cookies", payload)
        self.assertNotIn("setExtraHTTPHeaders", payload)
        self.assertEqual(headers["Authorization"], "Bearer test-token")
        self.assertEqual(evidence["state"], "LIVE")
        self.assertEqual(evidence["verification"], "PENDING")
        self.assertTrue(self.adapter().verify_evidence(evidence))

    def test_capture_rejects_bad_task_id_before_network(self):
        fake = FakeTransport()
        with self.assertRaises(KitesurfPolicyError):
            self.adapter(fake).capture("https://docs.example.com", task_id="")
        self.assertEqual(fake.calls, [])

    def test_evidence_hash_tampering_is_detected(self):
        evidence = self.adapter().capture("https://docs.example.com", task_id="test-2")
        evidence["markdown"] += "tampered"
        self.assertFalse(KitesurfBrowserAdapter.verify_evidence(evidence))

    def test_malformed_or_oversized_outputs_fail_closed(self):
        fake = FakeTransport(response={"success": True, "result": {"markdown": "x"}})
        with self.assertRaises(KitesurfProtocolError):
            self.adapter(fake).capture("https://docs.example.com", task_id="test-3")
        huge = FakeTransport(response={"success": True, "result": {
            "markdown": "x" * 1_000_001,
            "screenshot": base64.b64encode(b"png").decode("ascii"),
            "accessibilityTree": {},
        }})
        with self.assertRaises(KitesurfProtocolError):
            self.adapter(huge).capture("https://docs.example.com", task_id="test-4")

    def test_http_errors_fail_closed(self):
        with self.assertRaisesRegex(Exception, "HTTP 403"):
            self.adapter(FakeTransport(status=403)).capture("https://docs.example.com", task_id="test-5")
        with self.assertRaisesRegex(Exception, "HTTP 503"):
            self.adapter(FakeTransport(status=503)).capture("https://docs.example.com", task_id="test-6")


if __name__ == "__main__":
    unittest.main()
