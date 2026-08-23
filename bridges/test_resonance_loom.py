import json

from bridges.resonance_loom import ResonanceLoom


class TestResonanceLoom:
    def test_identical_states_have_identical_signatures(self):
        first = ResonanceLoom(seed=42).observe("alpha")
        second = ResonanceLoom(seed=42).observe("alpha")
        assert first.signature == second.signature
        assert first.short_signature == second.short_signature

    def test_weave_reaches_all_bridge_layers(self):
        loom = ResonanceLoom(seed=7)
        result = loom.weave("sentinel", valence=0.6, arousal=0.4)
        assert result["mood"]["source_agent"] == "sentinel"
        assert result["deliveries"]["layer"] == "meta"
        assert isinstance(result["chaos"], float)

    def test_persist_creates_jsonl_and_latest_snapshot(self, tmp_path):
        journal = tmp_path / "resonance.jsonl"
        loom = ResonanceLoom(seed=11)
        pulse = loom.persist(journal, "ci-pulse")
        loaded = ResonanceLoom.load(journal)

        assert len(loaded) == 1
        assert loaded[0]["signature"] == pulse.signature
        assert journal.with_suffix(".jsonl.latest").read_text().strip() == (
            journal.read_text().strip()
        )
        json.loads(journal.read_text().splitlines()[0])
