import pytest
from omega_prime.sandbox.modules.emergent_cartography import CartographyNetwork


class TestCartography:
    def test_explore_creates_map_cell(self):
        cart = CartographyNetwork(world_size=5, seed=42)
        cell = cart.explore_at("explorer", (1, 1))
        assert cell is not None
        assert cell.visit_count == 1

    def test_map_coverage_increases(self):
        cart = CartographyNetwork(world_size=5, seed=42)
        amap = cart.register_agent("mapper")
        assert amap.coverage == 0.0
        for x in range(5):
            cart.explore_at("mapper", (x, 0))
        assert amap.coverage > 0

    def test_map_sharing_transfers_knowledge(self):
        cart = CartographyNetwork(world_size=10, seed=42)
        cart.register_agent("scout")
        cart.register_agent("stay_home")
        # Scout explores
        for x in range(5):
            cart.explore_at("scout", (x, x))
        scout_count = cart._maps["scout"].explored_count
        home_count = cart._maps["stay_home"].explored_count
        transferred = cart.share_maps("scout", "stay_home")
        assert cart._maps["stay_home"].explored_count > home_count

    def test_accuracy_check(self):
        cart = CartographyNetwork(world_size=5, seed=42)
        cart.explore_at("agent", (0, 0))
        result = cart.check_accuracy("agent")
        assert 0.0 <= result["accuracy"] <= 1.0

    def test_repeat_visits_improve_accuracy(self):
        cart = CartographyNetwork(world_size=5, seed=42)
        pos = (2, 2)
        first = cart.explore_at("careful", pos)
        conf_first = first.confidence
        second = cart.explore_at("careful", pos)
        assert second.confidence >= conf_first
