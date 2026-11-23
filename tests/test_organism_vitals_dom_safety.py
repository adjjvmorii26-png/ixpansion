import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "dashboard" / "organism-vitals.html").read_text(encoding="utf-8")
SCRIPT = re.search(r"<script>(.*?)</script>", HTML, re.DOTALL).group(1)


class OrganismVitalsDomSafetyTests(unittest.TestCase):
    def test_inline_script_has_no_html_string_sinks(self):
        for sink in (".innerHTML", ".outerHTML", ".insertAdjacentHTML", "document.write"):
            with self.subTest(sink=sink):
                self.assertNotIn(sink, SCRIPT)

    def test_api_wave_and_module_labels_are_rendered_as_text(self):
        self.assertIn("waveNode.textContent", SCRIPT)
        self.assertIn("nameNode.textContent = name", SCRIPT)
        self.assertIn("card.replaceChildren(nameNode, waveNode, coherenceNode, bar)", SCRIPT)

    def test_log_messages_are_text_and_log_growth_is_bounded(self):
        self.assertIn("document.createTextNode(String(msg ?? ''))", SCRIPT)
        self.assertIn("MAX_LOG_ENTRIES = 100", SCRIPT)
        self.assertIn("while (el.children.length > MAX_LOG_ENTRIES)", SCRIPT)

    def test_external_coherence_values_are_finite_and_clamped(self):
        self.assertIn("Number.isFinite(rawScore)", SCRIPT)
        self.assertIn("Math.min(1, Math.max(0, rawScore))", SCRIPT)
        self.assertIn("fill.style.width = `${score * 100}%`", SCRIPT)


if __name__ == "__main__":
    unittest.main()
