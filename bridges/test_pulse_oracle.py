from bridges.resonance_loom import PulseOracle, ResonanceLoom


class TestPulseOracle:
    def test_first_pulse_is_baseline_and_repetition_recurs(self):
        loom = ResonanceLoom(seed=42)
        oracle = PulseOracle()
        first = oracle.record(loom.observe("first"))
        assert first.verdict == "baseline"
        assert first.distance == 0

        second = oracle.record(loom.observe("second"))
        assert second.verdict == "recurrence"
        assert second.distance == 0
        assert second.similarity == 1.0

    def test_state_mutation_has_broad_distance(self):
        loom = ResonanceLoom(seed=42)
        oracle = PulseOracle()
        oracle.record(loom.observe("before"))
        loom.hub.set_state("mutant", {"valence": 0.9, "arousal": 0.1})
        verdict = oracle.record(loom.observe("after"))

        assert verdict.verdict == "mutation"
        assert verdict.similarity < 0.5
        assert "state_keys" in verdict.changed_fields
        assert oracle.attractors == 2

    def test_compare_journals_reports_changed_fields(self, tmp_path):
        old_path = tmp_path / "old.jsonl"
        new_path = tmp_path / "new.jsonl"
        loom = ResonanceLoom(seed=11)
        loom.persist(old_path, "old")
        loom.weave("agent", 0.4, 0.8)
        loom.persist(new_path, "new")

        result = PulseOracle().compare_journals(old_path, new_path)
        assert result["verdict"] in {"stable", "shifting", "mutation"}
        assert result["old_signature"] != result["new_signature"]
        assert "state_keys" in result["changed_fields"]

    def test_compare_requires_valid_journals(self, tmp_path):
        empty = tmp_path / "empty.jsonl"
        empty.touch()
        try:
            PulseOracle().compare_journals(empty, empty)
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError")
