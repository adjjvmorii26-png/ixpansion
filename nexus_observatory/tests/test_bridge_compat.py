import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_bridge():
    spec = importlib.util.spec_from_file_location("omega_ixpansion_bridge", ROOT / "omega_fractal_engine/bridge_ixpansion.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class TestOmegaIxpansionBridge:
    def test_bridge_emits_nexus_compatible_resonance(self):
        bridge = load_bridge()
        first = bridge.bridge(seed=7, ticks=2, clock=lambda: "2026-08-24T00:00:00+00:00")
        second = bridge.bridge(seed=7, ticks=2, clock=lambda: "2026-08-24T00:01:00+00:00")

        assert {"tick", "chaos", "mood", "short_signature"} <= first.keys()
        assert first["signature"] == second["signature"]
        assert first["witnesses"] == second["witnesses"] > 0

    def test_bridge_rejects_unsafe_tick_budget(self):
        with __import__("pytest").raises(ValueError):
            load_bridge().bridge(ticks=0)
