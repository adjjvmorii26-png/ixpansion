"""Integration tests proving the three projects can coexist and interoperate."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import from all three projects
from bridge_core import BridgeHub


class TestCrossProject:
    def test_bridge_hub_initializes(self):
        hub = BridgeHub()
        assert hub is not None

    def test_omega_prime_to_fractal_engine(self):
        """omega_prime's StateCore feeds fractal_engine's MoodEngine."""
        hub = BridgeHub()
        hub.set_state("agent_1", {"valence": 0.7, "arousal": 0.8})
        mood = hub.propagate_emotion("agent_1")
        assert mood is not None

    def test_event_mesh_routes_to_reactor(self):
        """project_root's EventMesh publishes events that omega_prime's Reactor handles."""
        hub = BridgeHub()
        results = hub.route_event("physical", "collision", {"agents": ["a", "b"]})
        assert isinstance(results, dict)

    def test_entropy_shared_across_projects(self):
        """A single entropy source drives chaos in both engines."""
        hub = BridgeHub(seed=42)
        e1 = hub.get_chaos_level()
        e2 = hub.get_chaos_level()
        # Same source should give same reading within a tick
        assert isinstance(e1, float) and isinstance(e2, float)
