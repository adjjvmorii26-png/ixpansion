import json

import pytest

from lab.genome_observatory import (
    SCHEMA,
    build_parser,
    census,
    main,
    render_observatory,
    write_observatory,
)
from lab.mandate_genome import breed, forge, genome_ledger_path, load_genomes
from lab.pulse_oracle import forecast, seal_oracle
from lab.reversible_mandate import execute
from lab.runtime_vault import path, read_json, report_path, state_path
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


def install(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    state_path("sandbox", "engine.json").parent.mkdir(parents=True, exist_ok=True)
    reset_world(sandbox_state())


def reset_world(world):
    state_path("sandbox", "engine.json").write_text(json.dumps(world), encoding="utf-8")


def two_successes():
    first = forge(execute(parliament(read_json(state_path("sandbox", "engine.json")))))
    evolved = read_json(state_path("sandbox", "engine.json"))
    evolved["entropy_budget"] = 0.86
    second = forge(execute(parliament(evolved)))
    return first, second


class TestGenomeObservatory:
    def test_empty_population_is_sealed_with_conservative_guidance(self):
        result = census([])
        assert result["schema"] == SCHEMA
        assert result["status"] == "sealed"
        assert result["population"]["total"] == 0
        assert result["recommendations"] == []
        assert {"empty_population", "insufficient_breeding_pool"} <= {
            item["kind"] for item in result["warnings"]
        }

    def test_census_counts_lineages_and_recommends_unrelated_pair(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        first, second = two_successes()
        reset_world(sandbox_state(entropy=0.16))
        dream = forge(execute(parliament(read_json(state_path("sandbox", "engine.json"))), dry_run=True))
        result = census()
        assert result["population"]["total"] == 3
        assert result["population"]["breedable"] == 2
        assert result["population"]["outcome_counts"] == {"dream": 1, "successful": 2}
        assert result["population"]["policy_counts"] == {"expand": 2, "ration": 1}
        lineages = {item["child_id"]: item["parent_ids"] for item in result["lineages"]}
        assert lineages == {
            first["genome_id"]: [],
            second["genome_id"]: [],
            dream["genome_id"]: [],
        }
        assert len(result["compatibilities"]) == 1
        recommendation = result["recommendations"][0]
        assert recommendation["parent_ids"] == sorted([first["genome_id"], second["genome_id"]])
        assert recommendation["projected_policy"] in {"ration", "stabilize", "expand"}

    def test_existing_child_prevents_parent_remixing(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        first, second = two_successes()
        breed(first, second)
        result = census()
        related_pair = next(item for item in result["compatibilities"] if set(item["parent_ids"]) == {first["genome_id"], second["genome_id"]})
        assert related_pair["related"] is True
        assert all(
            set(item["parent_ids"]) != {first["genome_id"], second["genome_id"]}
            for item in result["recommendations"]
        )
        assert result["population"]["generation_counts"]["2"] == 1

    def test_unknown_ancestor_fails_closed(self):
        forged = [{
            "schema": "aleph.chronoforge.mandate-genome.v1",
            "status": "sealed", "breedable": True, "outcome": "successful",
            "policy": "expand", "traits": {}, "generation": 2,
            "parent_ids": ["MG-MISSING", "MG-MISSING-2"], "genome_id": "MG-CHILD",
            "sigil": "0x00000000", "provenance": {},
        }]
        with pytest.raises(ValueError, match="unknown ancestor"):
            census(forged)

    def test_tampered_genome_ledger_blocks_census(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        two_successes()
        record_path = genome_ledger_path()
        lines = record_path.read_text().splitlines()
        record = json.loads(lines[0])
        record["entry_hash"] = "f" * 64
        record_path.write_text(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
        with pytest.raises(ValueError, match="genome ledger audit failed"):
            census()

    def test_census_cli_seals_atomic_report(self, tmp_path, monkeypatch, capsys):
        install(tmp_path, monkeypatch)
        two_successes()
        capsys.readouterr()
        assert main(["census"]) == 0
        result = json.loads(capsys.readouterr().out)
        stored = read_json(report_path("genome-observatory.json"))
        assert result == stored
        assert result["census_hash"]

    def test_atlas_cli_writes_deterministic_html(self, tmp_path, monkeypatch, capsys):
        install(tmp_path, monkeypatch)
        two_successes()
        assert main(["census"]) == 0
        capsys.readouterr()
        output = tmp_path / "atlas" / "genome.html"
        assert main(["atlas", "--output", str(output)]) == 0
        result = json.loads(capsys.readouterr().out)
        assert result["ok"] is True
        html = output.read_text(encoding="utf-8")
        assert "<svg" in html and "Recommended Pairings" in html
        census_report = read_json(report_path("genome-observatory.json"))
        assert render_observatory(census_report) == html
        monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path / "empty-portable-root"))
        assert render_observatory(census_report) == html

    def test_modified_census_refuses_to_render(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        two_successes()
        report = census()
        modified = dict(report)
        modified["population"] = dict(modified["population"])
        modified["population"]["total"] = 999
        with pytest.raises(ValueError, match="census is missing, unsealed, or modified"):
            render_observatory(modified)

    def test_write_creates_nested_output_and_reports_hash(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        two_successes()
        report = census()
        output = tmp_path / "deep" / "genome-observatory.html"
        result = write_observatory(report, output)
        assert result == {"ok": True, "output": str(output), "census_hash": report["census_hash"]}
        assert output.exists()

    def test_parser_requires_a_command(self):
        with pytest.raises(SystemExit):
            build_parser().parse_args([])
