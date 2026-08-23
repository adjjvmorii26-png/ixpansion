import math
import pytest
from omega_prime.nucleus.kernel.pulse_harmonics import PulseHarmonics


class TestPulseHarmonics:
    def test_enroll_and_tick(self):
        h = PulseHarmonics()
        h.enroll("a")
        h.enroll("b")
        result = h.tick()
        assert "order" in result

    def test_order_parameter_range(self):
        h = PulseHarmonics()
        for i in range(5):
            h.enroll(f"a{i}")
        for _ in range(50):
            h.tick()
        r = h.order_parameter
        assert 0.0 <= r <= 1.0

    def test_synchronized_agents_amplify(self):
        h = PulseHarmonics(kuramoto_k=5.0)  # Strong coupling
        h.enroll("a", freq=1.0)
        h.enroll("b", freq=1.0)
        # Manually sync phases
        h._oscillators["a"].phase = 1.0
        h._oscillators["b"].phase = 1.05
        actions = [
            {"agent_id": "a", "intent": "attack"},
            {"agent_id": "b", "intent": "attack"},
        ]
        result = h.combine_actions(actions)
        amplified = [r for r in result if r.get("amplified")]
        assert len(amplified) == 1

    def test_desynced_agents_cancel(self):
        h = PulseHarmonics()
        h.enroll("a")
        h.enroll("b")
        # Set anti-phase
        h._oscillators["a"].phase = 0.0
        h._oscillators["b"].phase = math.pi
        actions = [
            {"agent_id": "a", "intent": "move"},
            {"agent_id": "b", "intent": "move"},
        ]
        result = h.combine_actions(actions)
        assert len(result) == 0  # Both cancelled

    def test_single_agent_passthrough(self):
        h = PulseHarmonics()
        actions = [{"agent_id": "solo", "intent": "scan"}]
        result = h.combine_actions(actions)
        assert len(result) == 1
