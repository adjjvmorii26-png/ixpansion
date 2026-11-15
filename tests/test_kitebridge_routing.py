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

    def test_chromium_guardrails_are_normalized_and_sorted(self):
        self.assertEqual(
            build_chromium_guardrails(allowed_hosts={"DOCS.example.com.", "app.example.com"}),
            {"allowedDomains": ["app.example.com", "docs.example.com"]},
        )

    def test_guardrails_support_one_leading_wildcard_pattern(self):
        self.assertEqual(
            build_chromium_guardrails(allowed_hosts={"*.EXAMPLE.com", "example.com"}),
            {"allowedDomains": ["*.example.com", "example.com"]},
        )

    def test_guardrails_support_domain_sets(self):
        self.assertEqual(
            build_chromium_guardrails(
                allowed_hosts={"docs.example.com"},
                allowed_domain_sets={"common-cdns", "internal-api"},
            ),
            {
                "allowedDomains": ["docs.example.com"],
                "allowedDomainSets": ["common-cdns", "internal-api"],
            },
        )

    def test_guardrails_can_explicitly_block_all_web_requests(self):
        self.assertEqual(
            build_chromium_guardrails(allow_no_network=True),
            {"allowedDomains": []},
        )

    def test_guardrails_reject_unbounded_or_ambiguous_policies(self):
        cases = (
            ({"hosts": set(), "sets": set(), "no_network": False}, "allowlist"),
            ({"hosts": {"bad host.example"}, "sets": set()}, "hostname"),
            ({"hosts": {"https://docs.example.com"}, "sets": set()}, "hostname"),
            ({"hosts": {"docs.example.com:443"}, "sets": set()}, "hostname"),
            ({"hosts": {"a.*.example.com"}, "sets": set()}, "wildcard"),
            ({"hosts": set(), "sets": {"common-cdns"}, "no_network": True}, "no_network"),
        )
        for args, expected in cases:
            with self.subTest(args=args), self.assertRaisesRegex(ValueError, expected):
                build_chromium_guardrails(
                    allowed_hosts=args.get("hosts"),
                    allowed_domain_sets=args.get("sets"),
                    allow_no_network=args.get("no_network", False),
                )

    def test_guardrails_enforce_cloudflare_documented_limits(self):
        with self.assertRaisesRegex(ValueError, "50"):
            build_chromium_guardrails(allowed_hosts={f"h{i}.example.com" for i in range(51)})
        with self.assertRaisesRegex(ValueError, "four"):
            build_chromium_guardrails(allowed_domain_sets={f"set-{i}" for i in range(5)})

    def test_guardrails_reject_invalid_domain_set_identifiers(self):
        for name in ("", "two words", "set/name"):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "domain-set"):
                build_chromium_guardrails(allowed_domain_sets={name})


if __name__ == "__main__":
    unittest.main()
