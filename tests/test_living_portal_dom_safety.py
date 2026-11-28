import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "dashboard" / "living_portal.html").read_text(encoding="utf-8")
SCRIPT = re.search(r"<script>(.*?)</script>", HTML, re.DOTALL).group(1)


def function_block(start: str, end: str) -> str:
    first = SCRIPT.index(start)
    last = SCRIPT.index(end, first + len(start))
    return SCRIPT[first:last]


class LivingPortalDomSafetyTests(unittest.TestCase):
    def test_api_rendering_script_has_no_inner_html_sink(self):
        self.assertNotIn(".innerHTML", SCRIPT)

    def test_dream_response_is_rendered_as_text(self):
        block = function_block("async function dream(){", "// Innovate")
        self.assertIn("document.createTextNode", block)
        self.assertIn("meta.textContent", block)
        self.assertNotIn(".innerHTML", block)

    def test_innovation_response_is_rendered_as_text(self):
        block = function_block("async function innovate(){", "// Whisper")
        self.assertIn("domain.textContent", block)
        self.assertIn("document.createTextNode", block)
        self.assertIn("meta.textContent", block)
        self.assertNotIn(".innerHTML", block)

    def test_family_map_uses_text_nodes_and_bounded_numeric_width(self):
        block = function_block("async function loadMap(){", "// Init")
        self.assertIn("name.textContent=String(family)", block)
        self.assertIn("countLabel.textContent=String(safeCount)", block)
        self.assertIn("track.style.width=`${pct}%`", block)
        self.assertIn("Math.min(100", block)
        self.assertNotIn(".innerHTML", block)

    def test_percent_formatter_clamps_external_values(self):
        block = function_block("function safePercent(value)", "// Pulse")
        self.assertIn("Number.isFinite(numeric)", block)
        self.assertIn("Math.min(1, Math.max(0, numeric))", block)


if __name__ == "__main__":
    unittest.main()
