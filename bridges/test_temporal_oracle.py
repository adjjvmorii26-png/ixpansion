import json
from concurrent.futures import ThreadPoolExecutor

from bridges.resonance_loom import PulseOracle, ResonanceLoom


class TestTemporalOracle:
    def test_analyze_detects_attractor_and_rates(self, tmp_path):
        journal = tmp_path / "time.jsonl"
        loom = ResonanceLoom(seed=42)
        origin = loom.persist(journal, "origin")
        loom.weave("traveler", 0.7, 0.9)
        away = loom.persist(journal, "away")
        returning = origin.payload()
        returning["tick"] = 3
        with journal.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(returning, sort_keys=True) + "\n")

        result = PulseOracle().analyze_journal(journal)
        assert result["pulses"] == 3
        assert result["distinct_states"] == 2
        assert result["attractor_count"] == 1
        assert result["attractors"][0]["signature"] == origin.signature
        assert result["attractors"][0]["count"] == 2
        assert result["recurrence_rate"] == 0.5
        assert result["transitions"]["mutation"] >= 1

    def test_strict_load_rejects_corrupt_interior_record(self, tmp_path):
        journal = tmp_path / "corrupt.jsonl"
        loom = ResonanceLoom(seed=42)
        loom.persist(journal, "good")
        with journal.open("a", encoding="utf-8") as stream:
            stream.write("{broken\n")

        assert len(ResonanceLoom.load(journal)) == 1
        try:
            ResonanceLoom.load(journal, strict=True)
        except ValueError:
            pass
        else:
            raise AssertionError("expected strict load failure")

    def test_concurrent_writes_keep_jsonl_and_latest_valid(self, tmp_path):
        journal = tmp_path / "parallel.jsonl"
        def write(index: int) -> None:
            ResonanceLoom(seed=index).persist(journal, f"writer-{index}")

        with ThreadPoolExecutor(max_workers=6) as pool:
            list(pool.map(write, range(24)))

        loaded = ResonanceLoom.load(journal, strict=True)
        latest = journal.with_suffix(".jsonl.latest")
        assert len(loaded) == 24

    def test_from_payload_requires_complete_record(self):
        try:
            ResonancePulse.from_payload({"tick": 1})
        except ValueError as error:
            assert "missing fields" in str(error)
        else:
            raise AssertionError("expected incomplete pulse failure")


from bridges.resonance_loom import ResonancePulse
