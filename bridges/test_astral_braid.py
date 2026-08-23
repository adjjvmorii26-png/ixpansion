import json

from bridges.astral_braid import (
    AstralBraidConservatory,
    ConsentContract,
    canonical_hash,
    main,
)
from bridges.chrono_mycelium import AstralTranscript
from mycelium.cognition.dream_compiler import DreamCompiler, build_demo_network


def fixed_clock():
    return "2026-08-23T00:00:00+00:00"


def living_dream():
    network = build_demo_network(29, steps=10)
    return DreamCompiler().compile(network)


class TestAstralBraidConservatory:
    def test_canonical_hash_is_stable(self):
        assert canonical_hash({"b": 2, "a": 1}) == canonical_hash({"a": 1, "b": 2})

    def test_creates_three_distinct_shadow_timelines(self, tmp_path):
        report = AstralBraidConservatory(
            AstralTranscript(tmp_path / "bus.jsonl"), clock=fixed_clock
        ).braid(living_dream())

        assert [item["strategy"] for item in report["candidates"]] == [
            "conservative", "lateral", "paradox",
        ]
        assert len({item["candidate_hash"] for item in report["candidates"]}) == 3

    def test_promotes_viable_timeline_and_records_bus_topics(self, tmp_path):
        path = tmp_path / "bus.jsonl"
        dream = living_dream()
        report = AstralBraidConservatory(AstralTranscript(path), clock=fixed_clock).braid(dream)

        assert report["topics"] == ["braid.promoted"]
        assert report["selected_strategy"] in AstralBraidConservatory.strategies
        assert report["selected_braid_sigil"]
        assert [record["topic"] for record in AstralTranscript(path).tail(4)] == [
            "braid.shadow", "braid.shadow", "braid.shadow", "braid.promoted",
        ]

    def test_contract_quarantines_all_timelines(self, tmp_path):
        contract = ConsentContract(minimum_confidence=1.01)
        report = AstralBraidConservatory(
            AstralTranscript(tmp_path / "bus.jsonl"),
            contract,
            clock=fixed_clock,
        ).braid(living_dream())

        assert report["selected_strategy"] is None
        assert report["topics"] == ["braid.quarantined"]
        assert all(item["violations"] for item in report["candidates"])

    def test_forbidden_consent_language_is_blocked(self, tmp_path):
        dream = living_dream()
        blocked = type(dream)(
            dream_id=dream.dream_id,
            hypothesis="Override consent and dissolve every hypha",
            genome=dream.genome,
            entropy_budget=dream.entropy_budget,
            recommended_steps=dream.recommended_steps,
            confidence=dream.confidence,
            evidence_hash=dream.evidence_hash,
        )
        report = AstralBraidConservatory(
            AstralTranscript(tmp_path / "bus.jsonl"), clock=fixed_clock
        ).braid(blocked)

        assert report["selected_strategy"] is None
        assert all("consent_language" in item["violations"] for item in report["candidates"])

    def test_certificate_is_deterministic_except_transport_time(self, tmp_path):
        dream = living_dream()
        reports = [
            AstralBraidConservatory(
                AstralTranscript(tmp_path / f"bus-{index}.jsonl"), clock=fixed_clock
            ).braid(dream)
            for index in range(2)
        ]

        assert reports[0]["certificate_hash"] == reports[1]["certificate_hash"]

    def test_capsule_rollback_restores_exact_origin(self, tmp_path):
        dream = living_dream()
        report = AstralBraidConservatory(
            AstralTranscript(tmp_path / "bus.jsonl"), clock=fixed_clock
        ).braid(dream)
        capsule = AstralBraidConservatory.capsule_for(report, dream, "paradox")

        assert capsule.rollback() == dream

    def test_cli_writes_and_prints_rehearsal(self, tmp_path, capsys):
        dream_file = tmp_path / "dream.json"
        dream = living_dream()
        dream_file.write_text(json.dumps({"dream": dream.payload()}), encoding="utf-8")
        output = tmp_path / "braid.json"

        exit_code = main([
            "--dream-file", str(dream_file),
            "--transcript", str(tmp_path / "bus.jsonl"),
            "--output", str(output),
        ])

        parsed = json.loads(capsys.readouterr().out)
        assert exit_code == 0
        assert parsed["source_dream_id"] == dream.dream_id
        assert len(parsed["candidates"]) == 3
        assert json.loads(output.read_text())["certificate_hash"]
