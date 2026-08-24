import json

import pytest

from lab.ancestral_echo import SCHEMA, build_parser, echo, echo_is_sealed, main
from lab.mandate_genome import find_genome, forge, load_genomes
from lab.pulse_oracle import forecast, seal_oracle
from lab.reversible_mandate import execute
from lab.runtime_vault import (
    append_jsonl,
    ledger_path,
    read_json,
    read_jsonl,
    state_path,
)
from lab.ritual_parliament import deliberate


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
    sealed_oracle = seal_oracle(forecast(
        sandbox_state=world,
        pulse_state={"beats": 8, "phase": 0.2},
        flux_state={"gen": 2},
        ledger_records=[{"type": "proof"}],
        audit={"ok": True, "tail_hash": "a" * 64},
        horizon=5,
    ))
    return deliberate(sealed_oracle)


def install(tmp_path, monkeypatch, world=None):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    path = state_path("sandbox", "engine.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    value = world or sandbox_state()
    path.write_text(json.dumps(value), encoding="utf-8")
    return value


def reset_world(world):
    state_path("sandbox", "engine.json").write_text(json.dumps(world), encoding="utf-8")


def make_genome():
    return forge(execute(parliament(read_json(state_path("sandbox", "engine.json")))))


class TestAncestralEcho:
    def test_successful_ancestor_resonates_without_mutation(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        genome = make_genome()
        before_world = sandbox_state()
        reset_world(before_world)
        proof_before = len(read_jsonl(ledger_path()))
        result = echo(genome["genome_id"])
        assert result["schema"] == SCHEMA
        assert result["original_policy"] == "expand"
        assert result["echo_policy"] == "expand"
        assert result["verdict"] == "resonant"
        assert result["projected_ticks"] == 3
        assert result["resonance"] >= 0.78
        assert read_json(state_path("sandbox", "engine.json")) == before_world
        assert len(read_jsonl(ledger_path())) == proof_before
        echoes = read_jsonl(ledger_path("genome-echoes.jsonl"))
        assert len(echoes) == 1
        assert echoes[0]["entry_hash"] == result["ledger_entry_hash"]
        stored = read_json(tmp_path / "reports" / "genome-echo.json")
        assert stored["echo_hash"] == result["echo_hash"]
        assert echo_is_sealed(stored) is True
        assert echo_is_sealed(echoes[0]) is True

    def test_latest_alias_selects_the_newest_sealed_lineage(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        genome = make_genome()
        reset_world(sandbox_state())
        direct = echo(genome["genome_id"], record=False)
        reset_world(sandbox_state())
        alias = echo("@latest", record=False)
        assert alias["genome_id"] == genome["genome_id"]
        assert alias["resonance"] == direct["resonance"]

    def test_terminal_report_remains_verifiable_after_ledger_metadata(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        genome = make_genome()
        reset_world(sandbox_state())
        result = echo(genome["genome_id"])
        assert echo_is_sealed(result) is True
        modified = dict(result)
        modified["resonance"] = 1.0
        assert echo_is_sealed(modified) is False

    def test_depleted_present_turns_expansion_into_a_fossil(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        genome = make_genome()
        present = sandbox_state(entropy=0.16, energy=0.78)
        reset_world(present)
        result = echo(genome["genome_id"])
        assert result["original_policy"] == "expand"
        assert result["echo_policy"] == "ration"
        assert result["verdict"] in {"drifting", "fossilized"}
        assert result["policy_alignment"] < 1.0
        assert read_json(state_path("sandbox", "engine.json")) == present

    def test_echo_can_be_observed_without_sealing_a_ledger_record(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        genome = make_genome()
        reset_world(sandbox_state())
        result = echo(genome["genome_id"], record=False)
        assert result["verdict"] == "resonant"
        assert "ledger_entry_hash" not in result
        assert not ledger_path("genome-echoes.jsonl").exists()

    def test_custom_max_tick_is_bound_and_respected(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        genome = make_genome()
        reset_world(sandbox_state())
        result = echo(genome["genome_id"], max_ticks=1, record=False)
        assert result["projected_ticks"] == 1

    def test_out_of_bounds_tick_budget_fails_closed(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        genome = make_genome()
        with pytest.raises(ValueError, match="max-ticks"):
            echo(genome["genome_id"], max_ticks=0)

    def test_missing_or_running_state_refuses(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        genome = make_genome()
        with pytest.raises(ValueError, match="malformed"):
            echo(genome["genome_id"], current_state={})
        running = sandbox_state()
        running["status"] = "running"
        with pytest.raises(ValueError, match="sandbox is running"):
            echo(genome["genome_id"], current_state=running)

    def test_tampered_genome_ledger_blocks_the_echo(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        genome = make_genome()
        genomes_path = tmp_path / "ledgers" / "genomes.jsonl"
        lines = genomes_path.read_text().splitlines()
        record = json.loads(lines[0])
        record["entry_hash"] = "f" * 64
        genomes_path.write_text(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
        with pytest.raises(ValueError, match="genome ledger audit failed"):
            echo(genome["genome_id"])

    def test_cli_accepts_custom_state_and_no_ledger(self, tmp_path, monkeypatch, capsys):
        install(tmp_path, monkeypatch)
        genome = make_genome()
        source = tmp_path / "present.json"
        source.write_text(json.dumps(sandbox_state()), encoding="utf-8")
        capsys.readouterr()
        assert main([genome["genome_id"], "--state", str(source), "--no-ledger"]) == 0
        result = json.loads(capsys.readouterr().out)
        assert result["verdict"] == "resonant"

    def test_parser_requires_a_genome_identity(self):
        with pytest.raises(SystemExit):
            build_parser().parse_args([])
