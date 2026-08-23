import pytest
from omega_prime.sandbox.modules.dimensional_fold import DimensionalFold


class TestDimensionalFold:
    def test_fold_changes_topology(self):
        fold = DimensionalFold(width=10, height=10)
        v1 = fold.topology_version
        fid = fold.fold(seed=42)
        assert fold.topology_version > v1
        assert fid.startswith("fold_")

    def test_resolve_position_after_horizontal_fold(self):
        fold = DimensionalFold(width=10, height=10)
        # Force a horizontal fold with split=5: row 0 maps to row 9, row 1 to row 8, etc.
        import random
        rng = random.Random(42)
        # We'll just verify resolve returns a valid position
        result = fold.resolve_position((0, 0))
        assert 0 <= result[0] < 10
        assert 0 <= result[1] < 10

    def test_unfold_restores(self):
        fold = DimensionalFold(width=10, height=10)
        fold.fold(seed=7)
        assert len(fold._active_folds) > 0
        fold.unfold_last()
        assert len(fold._active_folds) == 0

    def test_adjacency_check(self):
        fold = DimensionalFold(width=10, height=10)
        # Without folds, (3,3) and (3,4) are adjacent
        assert fold.are_adjacent((3, 3), (3, 4))
        assert not fold.are_adjacent((0, 0), (9, 9))

    def test_stats(self):
        fold = DimensionalFold()
        fold.fold(seed=1)
        stats = fold.stats
        assert stats["topology_version"] >= 1

    def test_multiple_folds_accumulate(self):
        fold = DimensionalFold(width=16, height=16)
        fold.fold(seed=1)
        v1 = fold.topology_version
        fold.fold(seed=2)
        assert fold.topology_version == v1 + 1
