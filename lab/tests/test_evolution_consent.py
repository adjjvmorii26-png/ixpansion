import json

import pytest

from lab.evolution_consent import (
    SCHEMA,
    _terminal_hash,
    approve,
    build_parser,
    consent_is_sealed,
    execute,
    main,
    request,
)
from lab.evolution_council import deliberate
from lab.mandate_genome import forge, load_genomes
from lab.pulse_oracle import forecast, seal_oracle
from lab.reversible_mandate import execute as execute_mandate
from lab.runtime_vault import ledger_path, read_json, read_jsonl, state_path
from lab.ritual_parliament import deliberate as parliament_vote


def sandbox_state(entropy=0.90, energy=0.30, ticks=10):
    return {
        "entropy_budget": entropy,
        "novelty": 1.1,
        "ticks": ticks,
        "phase": 0.4,
        "status": "idle",
        "history": [{"tick": index, "energy": energy} for index in range(1, 8)],
    }


def parliament(world):
    oracle = seal_oracle(forecast(
        sandbox_state=world,
        pulse_state={"beats": 8, "phase": 0.2},
        flux_state={"gen": 2},
        ledger_records=[{"type": "proof"}],
        audit={"ok": True, "tail_hash": "a" * 64},
        horizon=5,
    ))
    return parliament_vote(oracle)


def install(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    monkeypatch.setenv("ALEPH_CONSENT_KEY", "operator-hold-the-line-2026")
    path = state_path("sandbox", "engine.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sandbox_state()), encoding="utf-8")


def two_successes():
    first_world = read_json(state_path("sandbox", "engine.json"))
    first = forge(execute_mandate(parliament(first_world)))
    evolved = read_json(state_path("sandbox", "engine.json"))
    evolved["entropy_budget"] = 0.86
    second = forge(execute_mandate(parliament(evolved)))
    return first, second


def proposed_council(tmp_path, monkeypatch):
    install(tmp_path, monkeypatch)
    first, second = two_successes()
    base = deliberate(record=False)
    base["warnings"] = []
    base["census_hash"] = "c" * 64
    base["recommendations"] = [{
        "parent_ids": sorted([first["genome_id"], second["genome_id"]]),
        "compatibility": 0.91,
        "projected_policy": "stabilize",
        "projected_traits": {"risk_appetite": 0.70},
    }]
    monkeypatch.setattr("lab.evolution_council.census", lambda genomes: base)
    return deliberate(), sorted([first["genome_id"], second["genome_id"]])


def fixed_clock():
    return "2026-08-24T00:00:00+00:00"


class TestEvolutionConsentGate:
    def test_two_phase_approval_executes_exactly_one_breed(self, tmp_path, monkeypatch):
        council, parents = proposed_council(tmp_path, monkeypatch)
        before = len(load_genomes())
        requested = request(parents=parents, operator="ALEPH operator", council_source=tmp_path / "reports" / "evolution-council.json", clock=fixed_clock)
        assert requested["status"] == "requested"
        assert requested["mutation_allowed"] is False
        assert consent_is_sealed(requested) is True

        approved = approve(requested["request_id"], clock=fixed_clock)
        assert approved["status"] == "approved"
        assert approved["mutation_allowed"] is True
        assert consent_is_sealed(approved) is True

        executed = execute(requested["request_id"], clock=fixed_clock)
        assert executed["status"] == "executed"
        assert executed["child_genome_id"]
        assert executed["mutation_allowed"] is False
        assert len(load_genomes()) == before + 1
        assert consent_is_sealed(executed) is True
        events = [
            record.get("event") for record in read_jsonl(ledger_path("evolution-consents.jsonl"))
        ]
        assert events == ["requested", "approved", "executed"]

    def test_wrong_key_cannot_approve(self, tmp_path, monkeypatch):
        council, parents = proposed_council(tmp_path, monkeypatch)
        requested = request(parents=parents, operator="operator", clock=fixed_clock)
        monkeypatch.setenv("ALEPH_CONSENT_KEY", "a-completely-different-key")
        with pytest.raises(ValueError, match="approval key"):
            approve(requested["request_id"])
        assert read_json(tmp_path / "reports" / "evolution-consent.json")["status"] == "requested"

    def test_execute_requires_prior_approval(self, tmp_path, monkeypatch):
        council, parents = proposed_council(tmp_path, monkeypatch)
        requested = request(parents=parents, operator="operator", clock=fixed_clock)
        with pytest.raises(ValueError, match="approved state"):
            execute(requested["request_id"])
        assert len(load_genomes()) == 2

    def test_tampered_report_is_rejected_even_with_recomputed_hash(self, tmp_path, monkeypatch):
        council, parents = proposed_council(tmp_path, monkeypatch)
        requested = request(parents=parents, operator="operator", clock=fixed_clock)
        tampered = dict(requested)
        tampered["operator_label"] = "attacker"
        tampered["consent_hash"] = _terminal_hash(tampered)
        target = tmp_path / "reports" / "evolution-consent.json"
        target.write_text(json.dumps(tampered), encoding="utf-8")
        with pytest.raises(ValueError, match="ledger witness"):
            approve(requested["request_id"])

    def test_blocked_council_candidate_cannot_request_consent(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        two_successes()
        assert deliberate()
        parents = [item["genome_id"] for item in load_genomes()[:2]]
        with pytest.raises(ValueError, match="absent, blocked, or ambiguous"):
            request(parents=parents, operator="operator")

    def test_short_key_is_refused_before_a_request_is_written(self, tmp_path, monkeypatch):
        council, parents = proposed_council(tmp_path, monkeypatch)
        monkeypatch.setenv("ALEPH_CONSENT_KEY", "short")
        with pytest.raises(ValueError, match="at least 16 bytes"):
            request(parents=parents, operator="operator", clock=fixed_clock)

    def test_cli_status_reports_absent_without_artifact(self, tmp_path, monkeypatch, capsys):
        install(tmp_path, monkeypatch)
        assert main(["status"]) == 0
        result = json.loads(capsys.readouterr().out)
        assert result["status"] == "absent"

    def test_parser_requires_a_command(self):
        with pytest.raises(SystemExit):
            build_parser().parse_args([])
