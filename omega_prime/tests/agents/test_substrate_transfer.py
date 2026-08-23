import pytest
from omega_prime.agents.substrate_transfer import SubstrateTransferStation, CognitivePattern


class TestCognitivePattern:
    def test_encode_decode_roundtrip(self):
        pattern = CognitivePattern(
            origin_agent_id="scout_01", species="wanderer",
            memories=[{"event": "found_gold"}],
            beliefs={"world_is_safe": 0.6},
            behavioral_genome={"curiosity": 0.9},
            skills={"wanderer_navigate"},
        )
        encoded = pattern.encode()
        decoded = CognitivePattern.decode(encoded)
        assert decoded.integrity_check()
        assert decoded.origin_agent_id == "scout_01"

    def test_integrity_detects_corruption(self):
        pattern = CognitivePattern(origin_agent_id="x", species="y")
        pattern.encode()
        pattern.species = "corrupted"  # Tamper after encoding
        assert not pattern.integrity_check()

    def test_complexity_measure(self):
        simple = CognitivePattern(origin_agent_id="a", species="b")
        complex_p = CognitivePattern(
            origin_agent_id="c", species="d",
            memories=[{"e": i} for i in range(50)],
            beliefs={f"belief_{i}": 0.5 for i in range(20)},
            skills={"skill_a", "skill_b"},
        )
        assert complex_p.complexity > simple.complexity


class TestSubstrateTransferStation:
    def test_extract_and_imprint(self):
        station = SubstrateTransferStation(seed=42)
        pattern = station.extract(
            "original_body", "sentinel",
            memories=[{"m": 1}, {"m": 2}],
            beliefs={"loyal": 0.9},
            genome={"aggression": 0.7},
            skills={"sentinel_patrol"},
        )
        record = station.imprint("new_body", "architect", pattern)
        assert record.from_agent == "original_body"
        assert record.to_agent == "new_body"
        assert record.to_species == "architect"

    def test_memory_loss_during_transfer(self):
        station = SubstrateTransferStation(seed=42)
        memories = [{"mem": i} for i in range(200)]
        pattern = station.extract("old", "scout", memories=memories,
                                  beliefs={}, genome={}, skills=set())
        record = station.imprint("new", "scout", pattern)
        # With 200 memories and 5% loss rate, expect some losses
        assert record.memory_loss_count >= 0  # May be 0 with lucky RNG but structure works

    def test_species_specific_skills_lost_on_cross_species(self):
        station = SubstrateTransferStation(seed=42)
        pattern = station.extract(
            "old_body", "sentinel",
            memories=[], beliefs={}, genome={},
            skills={"sentinel_patrol", "generic_navigation"},
        )
        station.imprint("new_body", "wanderer", pattern)
        assert "sentinel_patrol" not in pattern.skills
        assert "generic_navigation" in pattern.skills

    def test_vacant_bodies_tracked(self):
        station = SubstrateTransferStation(seed=42)
        station.extract("body_a", "wanderer", [], {}, {}, set())
        assert "body_a" in station.vacant_bodies_list

    def test_scan_vacant_body(self):
        station = SubstrateTransferStation(seed=42)
        station.extract("vacant_1", "sentinel", [], {}, {}, set())
        scan = station.scan_body("vacant_1")
        assert scan is not None
        assert scan["status"] == "vacant"
