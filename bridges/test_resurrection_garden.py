import json

import pytest

from bridges.astral_braid import AstralBraidConservatory, ConsentContract, canonical_hash
from bridges.chrono_mycelium import AstralTranscript
from bridges.proof_garden import ProofGarden
from bridges.resurrection_garden import EnvironmentBudget, ResurrectionGarden, main
from mycelium.cognition.dream_compiler import DreamCompiler, build_demo_network


def clock():
    return "2026-08-23T00:00:00+00:00"


def quarantined_report(tmp_path, seed=31):
    dream = DreamCompiler().compile(build_demo_network(seed, steps=12))
    contract = ConsentContract(minimum_confidence=1.01)
    return AstralBraidConservatory(
        AstralTranscript(tmp_path / "bus.jsonl"), contract, clock=clock
    ).braid(dream)


def loose_garden(entropy=1.0, steps=32):
    contract = ConsentContract(maximum_entropy=1.0, maximum_steps=steps, minimum_confidence=0.0)
    environment = EnvironmentBudget(available_entropy=entropy, available_steps=steps)
    return ResurrectionGarden(contract, environment, clock=clock)


def reseal(report):
    stable = {key: value for key, value in report.items() if key not in ("certificate_hash", "emitted", "performed_at")}
    report["certificate_hash"] = canonical_hash(stable)
    return report


class TestResurrectionGarden:
    def test_rejects_promoted_braid(self, tmp_path):
        dream = DreamCompiler().compile(build_demo_network(29, steps=10))
        promoted = AstralBraidConservatory(AstralTranscript(tmp_path / "bus.jsonl")).braid(dream)

        with pytest.raises(ValueError, match="only quarantined"):
            loose_garden().evaluate(promoted)

    def test_rejects_invalid_quarantine_certificate(self, tmp_path):
        report = quarantined_report(tmp_path)
        report["certificate_hash"] = "0" * 64

        with pytest.raises(ValueError, match="certificate hash"):
            loose_garden().evaluate(report)

    def test_relaxed_constraints_awaken_a_dormant_future(self, tmp_path):
        result = loose_garden().evaluate(quarantined_report(tmp_path))

        assert result["verdict"] == "awakened"
        assert result["activation_gate"] == "astral_braid_rehearsal_required"
        assert len(result["lineage_hash"]) == 64
        assert result["selected_strategy"] in {"conservative", "lateral", "paradox"}

    def test_consent_failure_remains_permanently_sealed(self, tmp_path):
        report = quarantined_report(tmp_path)
        report["candidates"][0]["violations"].append("consent_language")
        reseal(report)
        result = loose_garden().evaluate(report)
        assessment = next(item for item in result["assessments"] if item["strategy"] == report["candidates"][0]["strategy"])

        assert assessment["eligible"] is False
        assert "consent_seal" in assessment["blocks"]

    def test_unknown_historical_violation_cannot_awaken(self, tmp_path):
        report = quarantined_report(tmp_path)
        report["candidates"][0]["violations"].append("reality_bleed")
        reseal(report)
        result = loose_garden().evaluate(report)
        assessment = next(item for item in result["assessments"] if item["strategy"] == report["candidates"][0]["strategy"])

        assert "unknown_historical_violation" in assessment["blocks"]

    def test_environment_shortfall_keeps_future_dormant(self, tmp_path):
        result = loose_garden(entropy=0.01, steps=1).evaluate(quarantined_report(tmp_path))

        assert result["verdict"] == "dormant"
        assert result["selected_strategy"] is None
        assert all(item["blocks"] for item in result["assessments"])

    def test_rejects_pollen_packet_for_different_quarantine(self, tmp_path):
        first = quarantined_report(tmp_path)
        second = quarantined_report(tmp_path, seed=37)
        packet = ProofGarden(tmp_path / "garden.jsonl", clock=clock).plant(first)["packet"]

        with pytest.raises(ValueError, match="does not prove"):
            loose_garden().evaluate(second, packet)

    def test_accepts_verified_quarantine_pollen_packet(self, tmp_path):
        report = quarantined_report(tmp_path)
        packet = ProofGarden(tmp_path / "garden.jsonl", clock=clock).plant(report)["packet"]

        assert loose_garden().evaluate(report, packet)["verdict"] == "awakened"

    def test_accepts_nightly_plant_artifact_wrapper(self, tmp_path):
        report = quarantined_report(tmp_path)
        planted = ProofGarden(tmp_path / "garden.jsonl", clock=clock).plant(report)

        assert loose_garden().evaluate(report, planted)["verdict"] == "awakened"

    def test_certificate_is_deterministic_except_issue_time(self, tmp_path):
        hashes = [
            loose_garden().evaluate(quarantined_report(tmp_path))["certificate_hash"]
            for _ in range(2)
        ]
        assert hashes[0] == hashes[1]

    def test_awakening_is_not_direct_execution(self, tmp_path):
        result = loose_garden().evaluate(quarantined_report(tmp_path))

        assert "command" not in result
        assert "script" not in result
        assert result["activation_gate"] != "execute"

    def test_cli_loads_contract_environment_and_report(self, tmp_path, capsys):
        report_path = tmp_path / "quarantine.json"
        report_path.write_text(json.dumps(quarantined_report(tmp_path)), encoding="utf-8")
        contract_path = tmp_path / "contract.json"
        contract_path.write_text(json.dumps({
            "maximum_entropy": 1.0,
            "maximum_steps": 32,
            "minimum_confidence": 0.0,
        }), encoding="utf-8")
        environment_path = tmp_path / "environment.json"
        environment_path.write_text(json.dumps({
            "available_entropy": 1.0,
            "available_steps": 32,
        }), encoding="utf-8")
        output = tmp_path / "result.json"

        exit_code = main([
            "--report", str(report_path),
            "--contract-file", str(contract_path),
            "--environment-file", str(environment_path),
            "--output", str(output),
        ])

        parsed = json.loads(capsys.readouterr().out)
        assert exit_code == 0
        assert parsed["verdict"] == "awakened"
        assert json.loads(output.read_text())["certificate_hash"] == parsed["certificate_hash"]
