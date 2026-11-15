import unittest

from integrations.kitebridge.routing import BrowserTask, select_browser_route


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
        self.assertEqual(
            select_browser_route(BrowserTask("https://docs.example.com/", public=False),
                                 allowed_hosts={"docs.example.com"}),
            "deny",
        )
        self.assertEqual(
            select_browser_route(BrowserTask("https://evil.example/", public=True),
                                 allowed_hosts={"docs.example.com"}),
            "deny",
        )
        self.assertEqual(
            select_browser_route(BrowserTask("http://docs.example.com/"),
                                 allowed_hosts={"docs.example.com"}),
            "deny",
        )

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
                self.assertEqual(
                    select_browser_route(BrowserTask(url), allowed_hosts={"docs.example.com"}),
                    "deny",
                )

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


if __name__ == "__main__":
    unittest.main()
