import json

from bridges.chrono_mycelium import (
    AstralTranscript,
    ChronoMyceliumBridge,
    RecursionAnchor,
    load_dream,
    main,
    stable_sigil,
)
from mycelium.cognition.dream_compiler import DreamCompiler, build_demo_network


def fixed_clock():
    return "2026-08-23T00:00:00+00:00"


def living_dream(seed=29):
    network = build_demo_network(seed, steps=0)
    network.plant(
        __import__("mycelium.hyphae.hypha", fromlist=["Spore"]).Spore(
            "chrono-test", {"curiosity": .3, "patience": .5}, viability=1
        ),
        (0, 0),
    )
    for _ in range(8):
        network.pulse()
    return DreamCompiler().compile(network)


class TestChronoMyceliumBridge:
    def test_stable_sigils_match_chrono_hex_contract(self):
        assert stable_sigil("forge_mind") == "0x" + __import__("hashlib").sha256(b"forge_mind").hexdigest()[:8].upper()

    def test_astral_transcript_appends_and_reads_jsonl(self, tmp_path):
        path = tmp_path / "astral.jsonl"
        bus = AstralTranscript(path, clock=fixed_clock)
        first = bus.send("alpha", {"value": 1})
        second = bus.send("beta", {"value": 2})

        assert first["topic"] == "alpha"
        assert second["payload"]["value"] == 2
        assert [item["topic"] for item in bus.tail(10)] == ["alpha", "beta"]
        assert len(path.read_text().splitlines()) == 2

    def test_recursion_anchor_limits_and_resets(self, tmp_path):
        anchor = RecursionAnchor(tmp_path / "anchor.json", maximum_depth=2)
        assert anchor.enter("one")["ok"] is True
        assert anchor.enter("two")["ok"] is True
        third = anchor.enter("three")
        assert third["ok"] is False
        assert third["reason"] == "recursion_anchor_trip"
        assert anchor.reset()["depth"] == 0

    def test_ritual_binds_dream_and_releases_anchor(self, tmp_path):
        dream = living_dream()
        transcript = AstralTranscript(tmp_path / "astral.jsonl", clock=fixed_clock)
        anchor = RecursionAnchor(tmp_path / "anchor.json")
        bridge = ChronoMyceliumBridge(transcript, anchor, clock=fixed_clock)
        report = bridge.ritual(dream)

        expected_sigil = stable_sigil(f"dream:{dream.dream_id}")
        assert report["dream_sigil"] == expected_sigil
        assert report["topics"] == ["dream.sigil", "dream.invocation"]
        assert report["evidence_hash"]
        assert anchor._read()["depth"] == 0
        assert transcript.tail(10)[0]["payload"]["sigil"] == expected_sigil

    def test_blocked_ritual_preserves_evidence_without_invoking_dream(self, tmp_path):
        dream = living_dream()
        transcript = AstralTranscript(tmp_path / "astral.jsonl", clock=fixed_clock)
        anchor = RecursionAnchor(tmp_path / "anchor.json", maximum_depth=1)
        anchor.enter("preexisting")
        bridge = ChronoMyceliumBridge(transcript, anchor, clock=fixed_clock)

        report = bridge.ritual(dream)
        assert report["topics"] == ["ritual.blocked"]
        assert report["anchor"]["reason"] == "recursion_anchor_trip"
        assert transcript.tail(1)[0]["payload"]["dream_sigil"] != ""

    def test_bridge_is_deterministic_except_transport_timestamp(self, tmp_path):
        dream = living_dream()
        hashes = []
        for index in range(2):
            transcript = AstralTranscript(tmp_path / f"bus-{index}.jsonl", clock=fixed_clock)
            report = ChronoMyceliumBridge(
                transcript,
                RecursionAnchor(tmp_path / f"anchor-{index}.json"),
                clock=fixed_clock,
            ).ritual(dream)
            hashes.append(report["evidence_hash"])
        assert hashes[0] == hashes[1]

    def test_cli_loads_artifact_and_writes_ritual(self, tmp_path, capsys):
        dream_file = tmp_path / "dream.json"
        dream = living_dream()
        dream_file.write_text(json.dumps({"dream": {
            **{key: value for key, value in dream.payload().items()},
        }}), encoding="utf-8")
        output = tmp_path / "ritual.json"
        assert main([
            "--dream-file", str(dream_file),
            "--transcript", str(tmp_path / "bus.jsonl"),
            "--anchor-state", str(tmp_path / "anchor.json"),
            "--output", str(output),
        ]) == 0
        loaded = load_dream(dream_file)
        assert loaded.dream_id == dream.dream_id
        assert json.loads(capsys.readouterr().out)["topics"] == [
            "dream.sigil", "dream.invocation",
        ]
