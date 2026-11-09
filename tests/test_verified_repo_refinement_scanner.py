"""Tests for the reusable repository-refinement HTML sink inventory."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = (Path(__file__).resolve().parents[1]
          / "skills" / "verified-repo-refinement" / "scripts" / "scan_html_sinks.py")
SPEC = importlib.util.spec_from_file_location("verified_refinement_scanner", SCRIPT)
SCANNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCANNER)


class VerifiedRefinementScannerTests(unittest.TestCase):
    def test_detects_dom_and_markup_sink_candidates(self):
        source = """\
node.innerHTML = remoteValue;
node.outerHTML = remoteValue;
node.insertAdjacentHTML("beforeend", remoteValue);
document.write(remoteValue);
frame.srcdoc = remoteValue;
<button onclick="run()">run</button>
<a href="javascript:alert(1)">open</a>
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page = root / "candidate.html"
            page.write_text(source, encoding="utf-8")
            found = SCANNER.scan_file(page, root)
        names = {item["candidate"] for item in found}
        self.assertTrue({
            "innerHTML", "outerHTML", "insertAdjacentHTML", "document.write",
            "srcdoc", "event_handler_attribute", "javascript_url",
        }.issubset(names))
        self.assertTrue(all(item["classification"] == "UNTRIAGED_CANDIDATE" for item in found))

    def test_reports_line_numbers_and_does_not_flag_text_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page = root / "safe.html"
            page.write_text("node.textContent = userText;\nnode.innerHTML = value;\n", encoding="utf-8")
            found = SCANNER.scan_file(page, root)
        self.assertEqual([(item["candidate"], item["line"]) for item in found], [("innerHTML", 2)])

    def test_scopes_directories_and_skips_dependency_trees(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "dashboard").mkdir()
            ignored = root / "node_modules" / "pkg"
            ignored.mkdir(parents=True)
            (root / "dashboard" / "page.html").write_text("document.write(x);", encoding="utf-8")
            (ignored / "vendor.html").write_text("x.innerHTML = x;", encoding="utf-8")
            paths = list(SCANNER.iter_html_files(root, ["dashboard"]))
        self.assertEqual([p.relative_to(root).as_posix() for p in paths], ["dashboard/page.html"])


if __name__ == "__main__":
    unittest.main()
