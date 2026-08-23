import pytest
from omega_prime.agents.registry import Registry
from omega_prime.agents.species.sentinel import Sentinel
from omega_prime.agents.species.wanderer import Wanderer
from omega_prime.nucleus.utilities.exception_map import AgentSpawnError


@pytest.fixture(autouse=True)
def setup_species():
    Registry.register("sentinel", Sentinel)
    Registry.register("wanderer", Wanderer)


class TestRegistry:
    def test_spawn_sentinel(self):
        agent = Registry.spawn("s1", "sentinel")
        assert agent.agent_id == "s1"
        assert agent.species == "sentinel"

    def test_spawn_unknown_raises(self):
        with pytest.raises(AgentSpawnError):
            Registry.spawn("x", "nonexistent")

    def test_roster(self):
        Registry.spawn("a", "sentinel")
        Registry.spawn("b", "wanderer")
        roster = Registry.roster()
        assert "a" in roster and "b" in roster
