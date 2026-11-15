import unittest

from integrations.kitebridge.routing import (
    BrowserTask,
    build_chromium_guardrails,
    select_browser_route,
)


class BrowserRoutingTests(unittest.TestCase):
    def test_public_allowlisted_page_uses_kitesurf(self):
        task = BrowserTask("https://docs.example.com/guide")
        self.assertEqual(select_browser_route(task, allowed_hosts={"docs.example.com"}), "kitesurf")

    def test_authenticated_and_persistent_tasks_use_chromium(self):
        for task in (
            BrowserTask("https://docs.example.com/", authenticated=True),
            BrowserTask("https://docs.example.com/", persistent_session=True),
            BrowserTask("https://docs.example.com/", requires_webgl=True),
            BrowserTask("https://docs.example.com/", requires_video=True),
            BrowserTask("https://docs.example.com/", bot_challenge=True),
        ):
            with self.subTest(task=task):
                self.assertEqual(select_browser_route(task, allowed_hosts={"docs.example.com"}), "chromium")

    def test_private_or_non_allowlisted_pages_are_denied(self):
        for task in (
            BrowserTask("https://docs.example.com/", public=False),
            BrowserTask("https://evil.example/"),
            BrowserTask("http://docs.example.com/"),
        ):
            with self.subTest(task=task):
                self.assertEqual(select_browser_route(task, allowed_hosts={"docs.example.com"}), "deny")

    def test_credentials_ports_fragments_and_ip_literals_are_denied(self):
        for url in (
            "https://user:pass@docs.example.com/",
            "https://docs.example.com:8443/",
            "https://docs.example.com/#fragment",
            "https://127.0.0.1/",
            "https://[::1]/",
            "https://docs.example.com:bad/",
        ):
            with self.subTest(url=url):
                task = BrowserTask(url, authenticated=True)
                self.assertEqual(select_browser_route(task, allowed_hosts={"docs.example.com"}), "deny")

    def test_chromium_flags_do_not_bypass_allowlist_or_url_validation(self):
        tasks = (
            BrowserTask("https://evil.example/", authenticated=True),
            BrowserTask("http://docs.example.com/", persistent_session=True),
            BrowserTask("https://127.0.0.1/", requires_webgl=True),
            BrowserTask("https://user@docs.example.com/", bot_challenge=True),
        )
        for task in tasks:
            with self.subTest(task=task):
                self.assertEqual(select_browser_route(task, allowed_hosts={"docs.example.com"}), "deny")

    def test_allowlist_normalization_and_invalid_allowlist_fail_closed(self):
        self.assertEqual(
            select_browser_route(BrowserTask("https://DOCS.example.com./"),
                                 allowed_hosts={"docs.example.com"}),
            "kitesurf",
        )
        self.assertEqual(
            select_browser_route(BrowserTask("https://docs.example.com/"),
                                 allowed_hosts={"127.0.0.1"}),
            "deny",
        )
        self.assertEqual(
            select_browser_route(BrowserTask("https://docs.example.com/"),
                                 allowed_hosts={"*.example.com"}),
            "deny",
        )

    def test_oversized_urls_are_denied_even_for_chromium(self):
        task = BrowserTask("https://docs.example.com/" + "x" * 2050, authenticated=True)
        self.assertEqual(select_browser_route(task, allowed_hosts={"docs.example.com"}), "deny")

    def test_chromium_guardrails_are_exact_normalized_and_sorted(self):
        self.assertEqual(
            build_chromium_guardrails(allowed_hosts={"DOCS.example.com.", "app.example.com"}),
            {"allowedDomains": ["app.example.com", "docs.example.com"]},
        )

    def test_chromium_guardrails_reject_wildcards_and_empty_lists(self):
        for hosts in (set(), {"*.example.com"}, {"127.0.0.1"}, {"bad host.example"}):
            with self.subTest(hosts=hosts), self.assertRaises(ValueError):
                build_chromium_guardrails(allowed_hosts=hosts)


if __name__ == "__main__":
    unittest.main()
