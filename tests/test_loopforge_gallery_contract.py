"""Contract checks for the local-first LOOPFORGE browser workbench."""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "dashboard" / "loopforge.html"


class LoopforgeGalleryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8")

    def test_page_has_all_four_workbenches(self):
        for panel in ("meme", "gif", "remix", "gallery"):
            with self.subTest(panel=panel):
                self.assertIn(f'id="{panel}"', self.html)

    def test_page_discloses_provider_and_gif_encoder_boundary(self):
        self.assertIn("does not call an AI provider", self.html)
        self.assertIn("not an encoded GIF", self.html)

    def test_gallery_is_local_and_exportable(self):
        self.assertIn("loopforge.gallery.v1", self.html)
        self.assertIn("Export gallery JSON", self.html)
        self.assertIn("provenance", self.html)

    def test_storyboard_has_four_frames_and_bounded_timing_choices(self):
        self.assertIn("frame_count:4", self.html)
        for delay in ("120", "180", "260", "420"):
            self.assertIn(f'value="{delay}"', self.html)

    def test_visual_export_is_png_not_a_fake_gif_export(self):
        self.assertIn('canvas.toBlob', self.html)
        self.assertIn('"image/png"', self.html)
        self.assertNotIn("download-gif", self.html)

    def test_dynamic_user_content_uses_text_nodes_for_gallery(self):
        self.assertIn("h.textContent=item.title", self.html)
        self.assertIn("p.textContent=item.content", self.html)

    def test_reduced_motion_and_mobile_layout_are_present(self):
        self.assertIn("prefers-reduced-motion:reduce", self.html)
        self.assertIn("@media(max-width:760px)", self.html)


if __name__ == "__main__":
    unittest.main()
