import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "scan_html_sinks.py"
SPEC = importlib.util.spec_from_file_location("scan_html_sinks", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class HtmlSinkScannerTests(unittest.TestCase):
    def test_finds_dom_sink_candidates_with_line_numbers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page = root / "page.html"
            page.write_text("<script>node.innerHTML = userValue;</script>\nnode.textContent = safeText;\n", encoding="utf-8")
            findings = MODULE.scan_file(page, root)
            self.assertEqual([(x["candidate"], x["line"]) for x in findings], [("innerHTML", 1)])
            self.assertEqual(findings[0]["classification"], "UNTRIAGED_CANDIDATE")

    def test_ignores_dependency_and_build_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ignored = root / "node_modules" / "pkg"
            ignored.mkdir(parents=True)
            (ignored / "vendor.html").write_text("x.innerHTML = value;", encoding="utf-8")
            self.assertEqual(list(MODULE.iter_html_files(root, [])), [])

    def test_scans_only_requested_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a").mkdir()
            (root / "b").mkdir()
            (root / "a" / "one.html").write_text("document.write(value);", encoding="utf-8")
            (root / "b" / "two.html").write_text("x.outerHTML = value;", encoding="utf-8")
            paths = list(MODULE.iter_html_files(root, ["a"]))
            self.assertEqual([p.relative_to(root).as_posix() for p in paths], ["a/one.html"])


if __name__ == "__main__":
    unittest.main()
