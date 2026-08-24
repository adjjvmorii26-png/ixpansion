import json

import pytest

from lab.mandate_genome import (
    SCHEMA,
    breed,
    build_parser,
    find_genome,
    forge,
    genome_ledger_path,
    load_genomes,
    main,
)
from lab.pulse_oracle import forecast, seal_oracle
from lab.reversible_mandate import execute
from lab.runtime_vault import append_jsonl, ledger_path, read_json, state_path, verify_jsonl
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


def parliament(entropy=0.90, energy=0.30, world=None):
    sealed_oracle = seal_oracle(forecast(
        sandbox_state=world or sandbox_state(entropy, energy),
        pulse_state={"beats": 8, "phase": 0.2},
        flux_state={"gen": 2},
        ledger_records=[{"type": "proof"}],
        audit={"ok": True, "tail_hash": "a" * 64},
        horizon=5,
    ))
    return deliberate(sealed_oracle)


def install(tmp_path, monkeypatch, state=None):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    path = state_path("sandbox", "engine.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    world = state or sandbox_state()
    path.write_text(json.dumps(world), encoding="utf-8")
    return world


def reset_world(world):
    state_path("sandbox", "engine.json").write_text(json.dumps(world), encoding="utf-8")


class TestMandateGenomeForge:
    def test_dream_becomes_nonbreedable_quarantine_lineage(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        mandate = execute(parliament(), dry_run=True)
        genome = forge(mandate)
        assert genome["schema"] == SCHEMA
        assert genome["outcome"] == "dream"
        assert genome["breedable"] is False
        assert genome["generation"] == 1
        assert genome["provenance"]["witness_hashes"] == []
        assert genome["genome_hash"]

    def test_successful_mandate_seals_breedable_genome(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        genome = forge(execute(parliament()))
        assert genome["outcome"] == "successful"
        assert genome["breedable"] is True
        assert len(genome["provenance"]["witness_hashes"]) == 3
        assert verify_jsonl(ledger_path())["ok"] is True
        loaded = load_genomes()
        assert len(loaded) == 1
        assert loaded[0]["genome_id"] == genome["genome_id"]

    def test_duplicate_mandate_cannot_forge_two_genomes(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        mandate = execute(parliament(), dry_run=True)
        forge(mandate)
        with pytest.raises(ValueError, match="already been forged"):
            forge(mandate)
        assert len(load_genomes()) == 1

    def test_modified_certificate_fails_closed(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        mandate = execute(parliament())
        mandate["execution_certificate"] = "0" * 64
        with pytest.raises(ValueError, match="certificate is missing or modified"):
            forge(mandate)
        assert genome_ledger_path().exists() is False

    def test_rolled_back_mandate_is_quarantined_but_preserved(self, tmp_path, monkeypatch):
        original = install(tmp_path, monkeypatch)
        real_append = append_jsonl

        def fail_second_witness(path, record):
            if record.get("type") == "mandate_tick" and record.get("tick") == 12:
                raise OSError("witness seal failed")
            return real_append(path, record)

        monkeypatch.setattr("lab.reversible_mandate.append_jsonl", fail_second_witness)
        mandate = execute(parliament())
        assert mandate["status"] == "rolled_back"
        reset_world(original)
        genome = forge(mandate)
        assert genome["outcome"] == "quarantined"
        assert genome["breedable"] is False
        assert len(genome["provenance"]["witness_hashes"]) == 1

    def test_compatible_successes_breed_a_second_generation_child(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        first = forge(execute(parliament()))
        evolved = read_json(state_path("sandbox", "engine.json"))
        reset_world({**evolved, "entropy_budget": 0.86})
        evolved_world = {**read_json(state_path("sandbox", "engine.json")), "entropy_budget": 0.86}
        second = forge(execute(parliament(world=evolved_world)))
        child = breed(first, second)
        assert child["generation"] == 2
        assert child["parent_ids"] == sorted([first["genome_id"], second["genome_id"]])
        assert child["outcome"] == "synthesized"
        assert child["policy"] in {"ration", "stabilize", "expand"}
        assert len(child["provenance"]["parents"]) == 2
        assert len(load_genomes()) == 3

    def test_incompatible_parents_are_refused(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        explorer = forge(execute(parliament()))
        depleted = sandbox_state(entropy=0.16)
        reset_world(depleted)
        conservator = forge(execute(parliament(world=depleted)))
        with pytest.raises(ValueError, match="trait distance exceeds"):
            breed(explorer, conservator)

    def test_tampered_genome_ledger_fails_closed(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        forge(execute(parliament()))
        path = genome_ledger_path()
        lines = path.read_text().splitlines()
        record = json.loads(lines[0])
        record["entry_hash"] = "f" * 64
        path.write_text(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
        with pytest.raises(ValueError, match="genome ledger audit failed"):
            load_genomes()

    def test_cli_lists_and_forges_without_publishing_code(self, tmp_path, monkeypatch, capsys):
        install(tmp_path, monkeypatch)
        source = tmp_path / "mandate.json"
        source.write_text(json.dumps(execute(parliament(), dry_run=True)), encoding="utf-8")
        assert main(["forge", "--report", str(source)]) == 0
        capsys.readouterr()
        assert main(["list"]) == 0
        listing = json.loads(capsys.readouterr().out)
        assert listing["genomes"][0]["outcome"] == "dream"

    def test_parser_requires_an_explicit_ritual(self):
        with pytest.raises(SystemExit):
            build_parser().parse_args([])
