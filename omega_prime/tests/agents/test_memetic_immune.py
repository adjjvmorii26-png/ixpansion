import pytest
from omega_prime.agents.cognition.memetic_immune import MemeticImmuneSystem


class TestMemeticImmuneSystem:
    def test_primary_exposure_creates_antibody(self):
        sys_ = MemeticImmuneSystem(seed=42)
        result = sys_.expose("host1", "dangerous_meme_payload")
        assert result["response"] == "primary"
        assert result["antibody_strength"] > 0

    def test_secondary_exposure_boosts(self):
        sys_ = MemeticImmuneSystem(seed=42)
        sys_.expose("h", "meme_payload_xyz")
        r2 = sys_.expose("h", "meme_payload_xyz")
        assert r2["response"] == "secondary"
        assert r2["antibody_strength"] > 0

    def test_parasitic_triggers_stronger_response(self):
        sys_ = MemeticImmuneSystem(seed=42)
        r_normal = sys_.expose("h", "benign_meme", is_parasitic=False)
        sys_.expose("h2", "evil_meme", is_parasitic=True)
        normal_strength = sys_._antibodies["h"][sys_._signature("benign_meme")].strength
        parasite_strength = sys_._antibodies["h2"][sys_._signature("evil_meme")].strength
        assert parasite_strength > normal_strength

    def test_immunity_check(self):
        sys_ = MemeticImmuneSystem(seed=42)
        payload = "specific_meme_v1"
        sys_.expose("h", payload)
        immunity = sys_.check_immunity("h", payload)
        assert immunity > 0

    def test_no_immunity_without_exposure(self):
        sys_ = MemeticImmuneSystem(seed=42)
        assert sys_.check_immunity("naive_host", "unknown_meme") == 0.0

    def test_decay_over_time(self):
        sys_ = MemeticImmuneSystem(seed=42)
        sys_.expose("h", "fading_meme")
        initial_count = sys_.stats["total_antibodies"]
        for _ in range(200):
            sys_.tick_decay()
        final_count = sys_.stats["total_antibodies"]
        assert final_count < initial_count

    def test_transfer_immunity_between_agents(self):
        sys_ = MemeticImmuneSystem(seed=42)
        # Build up donor's antibodies
        for i in range(10):
            sys_.expose("donor", f"meme_pattern_{i}", is_parasitic=(i % 3 == 0))
        transferred = sys_.transfer_immunity("donor", "recipient", fraction=0.5)
        assert transferred > 0
        assert sys_.check_immunity("recipient", "meme_pattern_0") > 0
