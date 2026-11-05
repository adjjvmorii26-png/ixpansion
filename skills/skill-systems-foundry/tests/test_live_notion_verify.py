import json, tempfile, unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from live_notion_verify import digest, verify_live, pin_from_text, strip_notion_noise

class LiveNotionVerifyTests(unittest.TestCase):
    def write_export(self, root, snapshot="seed body\n", pinned=None, page_id="page-abc"):
        (root / "seed_snapshot.md").write_text(snapshot, encoding="utf-8")
        meta = {
            "skill": "test",
            "notion_page_id": page_id,
            "source_snapshot": "seed_snapshot.md",
            "source_sha256": pinned if pinned is not None else digest(snapshot),
            "export_sha256": "",
        }
        (root / "provenance.json").write_text(json.dumps(meta), encoding="utf-8")

    def test_pass_when_live_matches_pin_and_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            body = "canonical seed\n"
            self.write_export(root, snapshot=body, pinned=digest(body))
            r = verify_live(root, fetcher=lambda pid: body)
            self.assertEqual(r.status, "PASS")
            self.assertEqual(r.findings, [])

    def test_live_source_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            snap = "old seed\n"
            self.write_export(root, snapshot=snap, pinned=digest(snap))
            r = verify_live(root, fetcher=lambda pid: "new live content\n")
            codes = [f["code"] for f in r.findings]
            self.assertEqual(r.status, "DRIFT")
            self.assertIn("LIVE_SOURCE_DRIFT", codes)
            self.assertIn("LIVE_VS_SNAPSHOT_DRIFT", codes)

    def test_unavailable_without_fetcher(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_export(root)
            r = verify_live(root, fetcher=None)
            self.assertEqual(r.status, "UNAVAILABLE")
            self.assertIn("LIVE_SOURCE_UNAVAILABLE", [f["code"] for f in r.findings])

    def test_fetcher_exception_is_unavailable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_export(root)
            def boom(_):
                raise RuntimeError("notion 404")
            r = verify_live(root, fetcher=boom)
            self.assertEqual(r.status, "UNAVAILABLE")

    def test_unpinned_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            body = "seed\n"
            self.write_export(root, snapshot=body, pinned="")
            r = verify_live(root, fetcher=lambda pid: body)
            self.assertIn(r.status, ("UNPINNED", "PASS"))
            self.assertIn("SOURCE_HASH_UNPINNED", [f["code"] for f in r.findings])

    def test_pin_from_text_stable(self):
        self.assertEqual(pin_from_text("a\r\nb"), pin_from_text("a\nb"))

    def test_strip_collapses_blank_lines(self):
        self.assertEqual(strip_notion_noise("a\n\n\n\nb"), "a\n\nb\n")

if __name__ == "__main__":
    unittest.main()
