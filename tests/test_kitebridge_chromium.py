from __future__ import annotations

import json
import unittest

from integrations.kitebridge.chromium import (
    BrowserSessionLease,
    ChromiumSessionConfigurationError,
    ChromiumSessionError,
    ChromiumSessionProtocolError,
    CloudflareChromiumSessionLauncher,
)


SESSION_ID = "1909cef7-23e8-4394-bc31-27404bf4348f"
WS_URL = (
    "wss://api.cloudflare.com/client/v4/accounts/account-1/"
    "browser-run/devtools/browser/" + SESSION_ID
)


class FakeTransport:
    def __init__(self, *, status=200, response=None):
        self.status = status
        self.response = response or {
            "sessionId": SESSION_ID,
            "webSocketDebuggerUrl": WS_URL,
        }
        self.calls = []

    def __call__(self, method, url, headers, body, timeout):
        self.calls.append({
            "method": method,
            "url": url,
            "headers": headers,
            "payload": json.loads(body) if body else None,
            "timeout": timeout,
        })
        return self.status, self.response


class ChromiumSessionLauncherTests(unittest.TestCase):
    def launcher(self, fake=None):
        return CloudflareChromiumSessionLauncher(
            account_id="account-1",
            token="test-token",
            transport=fake or FakeTransport(),
        )

    def test_missing_credentials_fail_closed(self):
        with self.assertRaises(ChromiumSessionConfigurationError):
            CloudflareChromiumSessionLauncher(account_id="", token="token")
        with self.assertRaises(ChromiumSessionConfigurationError):
            CloudflareChromiumSessionLauncher(account_id="account", token="")

    def test_launch_sends_guardrails_in_session_creation_request(self):
        fake = FakeTransport()
        lease = self.launcher(fake).launch(
            allowed_hosts={"docs.example.com", "*.static.example.com"},
            allowed_domain_sets={"common-cdns"},
            keep_alive_ms=120_000,
        )
        call = fake.calls[0]
        self.assertEqual(call["method"], "POST")
        self.assertIn("/browser-run/devtools/browser?keep_alive=120000", call["url"])
        self.assertEqual(call["headers"]["Authorization"], "Bearer test-token")
        self.assertEqual(
            call["payload"],
            {
                "guardrails": {
                    "allowedDomains": ["*.static.example.com", "docs.example.com"],
                    "allowedDomainSets": ["common-cdns"],
                }
            },
        )
        self.assertEqual(lease.session_id, SESSION_ID)
        self.assertEqual(lease.guardrails, call["payload"]["guardrails"])
        self.assertEqual(lease.keep_alive_ms, 120_000)
        self.assertNotIn("test-token", repr(lease))
        self.assertNotIn(WS_URL, repr(lease))

    def test_domain_set_only_policy_omits_empty_allowed_domains(self):
        fake = FakeTransport()
        self.launcher(fake).launch(allowed_domain_sets={"common-cdns"})
        self.assertEqual(
            fake.calls[0]["payload"],
            {"guardrails": {"allowedDomainSets": ["common-cdns"]}},
        )

    def test_no_network_policy_is_explicit(self):
        fake = FakeTransport()
        self.launcher(fake).launch(allow_no_network=True)
        self.assertEqual(
            fake.calls[0]["payload"],
            {"guardrails": {"allowedDomains": []}},
        )

    def test_missing_or_ambiguous_policy_fails_before_network(self):
        fake = FakeTransport()
        with self.assertRaises(ChromiumSessionConfigurationError):
            self.launcher(fake).launch()
        self.assertEqual(fake.calls, [])

    def test_keep_alive_is_bounded_and_boolean_is_rejected(self):
        for value in (9_999, 1_200_001, True, 60_000.0):
            with self.subTest(value=value), self.assertRaises(ChromiumSessionConfigurationError):
                self.launcher(FakeTransport()).launch(
                    allowed_hosts={"docs.example.com"},
                    keep_alive_ms=value,
                )

    def test_invalid_session_response_is_rejected(self):
        bad_responses = (
            {},
            {"sessionId": "../escape", "webSocketDebuggerUrl": WS_URL},
            {"sessionId": SESSION_ID, "webSocketDebuggerUrl": "https://api.cloudflare.com/evil"},
            {"sessionId": SESSION_ID, "webSocketDebuggerUrl": "wss://evil.example/socket"},
            {"sessionId": SESSION_ID, "webSocketDebuggerUrl": WS_URL + "?token=leak"},
        )
        for response in bad_responses:
            with self.subTest(response=response), self.assertRaises(ChromiumSessionProtocolError):
                self.launcher(FakeTransport(response=response)).launch(
                    allowed_hosts={"docs.example.com"}
                )

    def test_transient_and_permanent_http_errors_are_classified(self):
        with self.assertRaisesRegex(ChromiumSessionError, "transient HTTP 429"):
            self.launcher(FakeTransport(status=429)).launch(
                allowed_hosts={"docs.example.com"}
            )
        with self.assertRaisesRegex(ChromiumSessionError, "HTTP 403"):
            self.launcher(FakeTransport(status=403)).launch(
                allowed_hosts={"docs.example.com"}
            )

    def test_close_uses_only_the_lease_session_id(self):
        fake = FakeTransport()
        launcher = self.launcher(fake)
        lease = launcher.launch(allowed_hosts={"docs.example.com"})
        launcher.close(lease)
        self.assertEqual(fake.calls[1]["method"], "DELETE")
        self.assertTrue(fake.calls[1]["url"].endswith("/" + SESSION_ID))
        self.assertIsNone(fake.calls[1]["payload"])

    def test_close_accepts_empty_204_response(self):
        fake = FakeTransport()
        launcher = self.launcher(fake)
        lease = launcher.launch(allowed_hosts={"docs.example.com"})
        fake.status = 204
        fake.response = {}
        launcher.close(lease)
        self.assertEqual(fake.calls[1]["method"], "DELETE")

    def test_close_rejects_arbitrary_session_id(self):
        with self.assertRaises(ChromiumSessionConfigurationError):
            self.launcher(FakeTransport()).close("some-other-session")


if __name__ == "__main__":
    unittest.main()
