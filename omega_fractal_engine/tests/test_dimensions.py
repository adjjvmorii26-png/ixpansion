import math
import pytest
from omega_fractal_engine.lattice.dimensions.euclid.euclidean_space import EuclideanSpace
from omega_fractal_engine.lattice.dimensions.non_euclid.non_euclidean_space import NonEuclideanSpace
from omega_fractal_engine.lattice.dimensions.hyperbolic.hyperbolic_space import HyperbolicSpace


class TestEuclidean:
    def test_distance_2d(self):
        space = EuclideanSpace(dimensions=2)
        d = space.distance((0, 0), (3, 4))
        assert d == pytest.approx(5.0)

    def test_adjacency_count(self):
        space = EuclideanSpace(dimensions=3)
        neighbors = space.adjacency((0, 0, 0))
        assert len(neighbors) == 6  # ±x, ±y, ±z


class TestNonEuclidean:
    def test_distance_positive(self):
        space = NonEuclideanSpace(warp_factor=0.5)
        d = space.distance((1, 2), (4, 6))
        assert d > 0

    def test_distance_asymmetric(self):
        space = NonEuclideanSpace(warp_factor=0.8)
        a = (1, 2, 3)
        b = (7, 8, 9)
        # May or may not be symmetric — just ensure both are positive
        assert space.distance(a, b) > 0
        assert space.distance(b, a) > 0

    def test_warp_resolution(self):
        space = NonEuclideanSpace()
        space.add_warp((1, 1), (99, 99))
        assert space.resolve((1, 1)) == (99, 99)
        assert space.resolve((2, 2)) == (2, 2)


class TestHyperbolic:
    def test_circumference_grows(self):
        space = HyperbolicSpace(curvature=-1.0)
        c1 = space.circumference_at_radius(1)
        c2 = space.circumference_at_radius(2)
        c3 = space.circumference_at_radius(3)
        assert c1 < c2 < c3

    def test_area_exponential(self):
        space = HyperbolicSpace(curvature=-1.0)
        a1 = space.area_at_radius(1)
        a2 = space.area_at_radius(2)
        assert a2 > a1 * 2  # Exponential growth means area at r=2 >> 2× area at r=1

    def test_is_infinite(self):
        space = HyperbolicSpace()
        assert space.is_infinite is True

    def test_neighbors_within_increases(self):
        space = HyperbolicSpace(curvature=-1.0)
        n1 = space.neighbors_within((0, 0), 1)
        n2 = space.neighbors_within((0, 0), 3)
        assert n2 > n1
