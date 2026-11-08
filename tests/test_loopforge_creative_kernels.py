"""Fast contract tests for LOOPFORGE deterministic creative kernels."""
import unittest

from loopforge.creative_kernels import (
    ArtifactStatus,
    assess_artifact,
    generate_meme_seeds,
    loop_seam_score,
    plan_gif,
)


class MemeSeedTests(unittest.TestCase):
    def test_seed_generation_is_deterministic(self):
        self.assertEqual(
            generate_meme_seeds("the build is still running", seed=7),
            generate_meme_seeds("the build is still running", seed=7),
        )

    def test_seed_generation_normalizes_whitespace(self):
        self.assertEqual(
            generate_meme_seeds("  test   loop  ", count=1)[0].premise,
            "test loop",
        )

    def test_seed_count_is_bounded(self):
        with self.assertRaises(ValueError):
            generate_meme_seeds("x", count=33)

    def test_empty_premise_rejected(self):
        with self.assertRaises(ValueError):
            generate_meme_seeds("  ")


class GifReactorTests(unittest.TestCase):
    def test_gif_plan_calculates_duration(self):
        plan = plan_gif(30, fps=15)
        self.assertEqual(plan.frame_duration_ms, 67)
        self.assertEqual(plan.total_duration_ms, 2010)
        self.assertTrue(plan.loop_forever)

    def test_gif_plan_rejects_oversized_duration(self):
        with self.assertRaises(ValueError):
            plan_gif(300, fps=30, max_duration_ms=5000)

    def test_gif_plan_rejects_invalid_fps(self):
        with self.assertRaises(ValueError):
            plan_gif(10, fps=120)

    def test_identical_seam_scores_one(self):
        self.assertEqual(loop_seam_score([0, 50, 255], [0, 50, 255]), 1.0)

    def test_opposite_seam_scores_zero(self):
        self.assertEqual(loop_seam_score([0, 0], [255, 255]), 0.0)

    def test_signature_shape_is_validated(self):
        with self.assertRaises(ValueError):
            loop_seam_score([0], [0, 1])


class ArchaeologistTests(unittest.TestCase):
    def test_referenced_compatible_asset_is_active(self):
        result = assess_artifact(age_days=2, reference_count=3, compatible=True)
        self.assertEqual(result.status, ArtifactStatus.ACTIVE)

    def test_old_referenced_asset_needs_refresh(self):
        result = assess_artifact(age_days=120, reference_count=1, compatible=True)
        self.assertEqual(result.status, ArtifactStatus.REFRESH)

    def test_incompatible_referenced_asset_is_forked(self):
        result = assess_artifact(age_days=2, reference_count=1, compatible=False)
        self.assertEqual(result.status, ArtifactStatus.FORK)

    def test_unknown_provenance_is_quarantined(self):
        result = assess_artifact(age_days=1, reference_count=0, compatible=True, provenance_known=False)
        self.assertEqual(result.status, ArtifactStatus.QUARANTINE)

    def test_old_unreferenced_asset_is_only_candidate(self):
        result = assess_artifact(age_days=200, reference_count=0, compatible=True)
        self.assertEqual(result.status, ArtifactStatus.ARCHIVE_CANDIDATE)
        self.assertIn("approval", result.reason)

    def test_duplicate_is_not_deleted(self):
        result = assess_artifact(
            age_days=1, reference_count=0, compatible=True, duplicate_of="asset-001"
        )
        self.assertEqual(result.status, ArtifactStatus.ARCHIVE_CANDIDATE)
        self.assertIn("retain", result.reason)

    def test_negative_age_rejected(self):
        with self.assertRaises(ValueError):
            assess_artifact(age_days=-1, reference_count=0, compatible=True)


if __name__ == "__main__":
    unittest.main()
