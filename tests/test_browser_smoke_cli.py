"""CLI contract tests for the optional browser smoke runner."""
import subprocess
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).parents[1]
    / "skills"
    / "live-reusable-test-surface"
    / "scripts"
    / "browser-smoke.mjs"
)


class BrowserSmokeCliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            ["node", str(SCRIPT), *args],
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )

    def test_help_does_not_require_playwright(self):
        result = self.run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Usage:", result.stdout)

    def test_rejects_non_http_protocol_before_loading_playwright(self):
        result = self.run_cli("file:///etc/passwd")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Only HTTP and HTTPS", result.stderr)

    def test_rejects_out_of_range_viewport(self):
        result = self.run_cli("https://example.com", "--viewport", "100x100")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Viewport dimensions", result.stderr)

    def test_rejects_invalid_timeout(self):
        result = self.run_cli("https://example.com", "--timeout", "10")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Timeout must be an integer", result.stderr)

    def test_rejects_unknown_options(self):
        result = self.run_cli("https://example.com", "--trust-me")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Unknown option", result.stderr)


if __name__ == "__main__":
    unittest.main()
