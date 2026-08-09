import unittest
from unittest.mock import patch

from security_controls import URLPolicy
from web_resources import PublicResourceCollector


class FakeHeaders:
    def get_content_type(self):
        return "text/html"


class FakeResponse:
    headers = FakeHeaders()

    def geturl(self):
        return "https://docs.example.test/start"

    def read(self, limit):
        self.limit = limit
        return b"<title>Docs</title><script>token=secret</script><p>Keep this fact.</p><a href='/next'>Next</a>"

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class WebResourceTests(unittest.TestCase):
    @patch("web_resources.build_opener")
    def test_collects_public_text_and_links_without_cookie_header(self, build_opener):
        build_opener.return_value.open.return_value = FakeResponse()
        result = PublicResourceCollector(URLPolicy({"docs.example.test"})).collect(
            "https://docs.example.test/start"
        )

        self.assertEqual(result["title"], "Docs")
        self.assertEqual(result["text"], "Docs\nKeep this fact.\nNext")
        self.assertEqual(result["links"], ["https://docs.example.test/next"])
        sent_request = build_opener.return_value.open.call_args.args[0]
        self.assertIsNone(sent_request.get_header("Cookie"))

    def test_rejects_hosts_that_are_not_allowlisted(self):
        collector = PublicResourceCollector(URLPolicy({"docs.example.test"}))
        with self.assertRaises(PermissionError):
            collector.collect("https://other.example.test/start")


if __name__ == "__main__":
    unittest.main()