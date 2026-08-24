import json

import pytest

from lab.ancestral_echo import echo
from lab.evolution_council import (
    SCHEMA,
    build_parser,
    council_is_sealed,
    deliberate,
    main,
)
from lab.mandate_genome import forge
from lab.pulse_oracle import forecast, seal_oracle
from lab.reversible_mandate import execute
from lab.runtime_vault import append_jsonl, ledger_path, read_json, read_jsonl, state_path
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


def install(tmp_path, monkeypatch, world=None):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    path = state_path("sandbox", "engine.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    value = world or sandbox_state()
    path.write_text(json.dumps(value), encoding="utf-8")
    return value


def reset_world(world):
    state_path("sandbox", "engine.json").write_text(json.dumps(world), encoding="utf-8")


def two_successes():
    first_world = read_json(state_path("sandbox", "engine.json"))
    first = forge(execute(parliament(first_world)))
    evolved = read_json(state_path("sandbox", "engine.json"))
    evolved["entropy_budget"] = 0.86
    second = forge(execute(parliament(evolved)))
    return first, second


def empty_council():
    result = deliberate(record=False)
    return result


class TestEvolutionCouncil:
    def test_empty_population_yields_a_sealed_non_mutating_playbook(self):
        result = empty_council()
        assert result["schema"] == SCHEMA
        assert result["status"] == "sealed"
        assert result["mode"] == "advisory-only"
        assert result["mutation_budget"] == 0
        assert result["actions"] == []
        assert result["breeding_candidates"] == []
        assert council_is_sealed(result) is True

    def test_two_resonant_ancestors_receive_preserve_and_pair_proposal(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        first, second = two_successes()
        base = deliberate(record=False)
        base["warnings"] = []
        base["census_hash"] = "b" * 64
        base["recommendations"] = [{
            "parent_ids": sorted([first["genome_id"], second["genome_id"]]),
            "compatibility": 0.9,
            "projected_policy": "stabilize",
            "projected_traits": {"risk_appetite": 0.7},
        }]
        monkeypatch.setattr("lab.evolution_council.census", lambda genomes: base)
        before_genomes = len(read_jsonl(ledger_path("genomes.jsonl")))
        before_proofs = len(read_jsonl(ledger_path()))
        result = deliberate(record=False)
        actions = {item["genome_id"]: item for item in result["actions"]}
        assert actions[first["genome_id"]]["action"] in {"preserve", "monitor"}
        assert actions[second["genome_id"]]["action"] in {"preserve", "monitor"}
        assert result["breeding_candidates"]
        candidate = result["breeding_candidates"][0]
        assert set(candidate["parents"]) == {first["genome_id"], second["genome_id"]}
        assert candidate["status"] == "proposed"
        assert candidate["requires_explicit_consent"] is True
        assert candidate["execution"].startswith("python3 lab/mandate_genome.py breed")
        assert len(read_jsonl(ledger_path("genomes.jsonl"))) == before_genomes
        assert len(read_jsonl(ledger_path())) == before_proofs

    def test_stored_echoes_are_reused_only_for_the_same_present_signature(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        first, second = two_successes()
        present = read_json(state_path("sandbox", "engine.json"))
        echo(first["genome_id"])
        echo(second["genome_id"])
        result = deliberate(record=False)
        assert result["sources"]["stored_echo_count"] == 2
        assert result["sources"]["fresh_echo_count"] == 0
        changed = dict(present)
        changed["entropy_budget"] = 0.72
        stale = deliberate(current_state=changed, record=False)
        assert stale["current_state_signature_hash"] != result["current_state_signature_hash"]
        assert stale["sources"]["fresh_echo_count"] == 2

    def test_quarantined_outcome_becomes_containment_review(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        real_append = append_jsonl

        def fail_second_witness(path, record):
            if record.get("type") == "mandate_tick" and record.get("tick") == 12:
                raise OSError("witness seal failed")
            return real_append(path, record)

        monkeypatch.setattr("lab.reversible_mandate.append_jsonl", fail_second_witness)
        mandate = execute(parliament(read_json(state_path("sandbox", "engine.json"))))
        assert mandate["status"] == "rolled_back"
        genome = forge(mandate)
        result = deliberate(record=False)
        action = next(item for item in result["actions"] if item["genome_id"] == genome["genome_id"])
        assert action["action"] == "containment_review"
        assert action["offices"]["sentinel"] == "block"

    def test_monoculture_blocks_same_policy_breeding(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        first, second = two_successes()
        result = deliberate(record=False)
        matching = [
            item for item in result["breeding_candidates"]
            if set(item["parents"]) == {first["genome_id"], second["genome_id"]}
        ]
        assert matching
        assert all(item["status"] == "blocked" for item in matching)
        assert all("same-policy breeding" in item["blockers"][0] for item in matching)

    def test_tampered_echo_ledger_fails_closed(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        first, second = two_successes()
        reset_world(read_json(state_path("sandbox", "engine.json")))
        echo(first["genome_id"])
        echo(second["genome_id"])
        echo_ledger = ledger_path("genome-echoes.jsonl")
        lines = echo_ledger.read_text().splitlines()
        record = json.loads(lines[0])
        record["entry_hash"] = "f" * 64
        echo_ledger.write_text(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
        with pytest.raises(ValueError, match="echo ledger audit failed"):
            deliberate(record=False)

    def test_final_council_report_remains_sealed_after_ledger_metadata(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        two_successes()
        result = deliberate()
        assert council_is_sealed(result) is True
        stored = read_json(tmp_path / "reports" / "evolution-council.json")
        assert council_is_sealed(stored) is True
        assert len(read_jsonl(ledger_path("evolution-councils.jsonl"))) == 1

    def test_cli_writes_no_ledger_when_requested(self, tmp_path, monkeypatch, capsys):
        install(tmp_path, monkeypatch)
        two_successes()
        capsys.readouterr()
        source = tmp_path / "present.json"
        source.write_text(json.dumps(sandbox_state()), encoding="utf-8")
        assert main(["--state", str(source), "--no-ledger"]) == 0
        result = json.loads(capsys.readouterr().out)
        assert result["mode"] == "advisory-only"
        assert not ledger_path("evolution-councils.jsonl").exists()

    def test_parser_rejects_unknown_arguments(self):
        with pytest.raises(SystemExit):
            build_parser().parse_args(["unknown"])
