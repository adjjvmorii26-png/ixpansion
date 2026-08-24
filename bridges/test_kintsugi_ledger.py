import json

from bridges.astral_braid import AstralBraidConservatory
from bridges.kintsugi_ledger import KintsugiLedgerRepairer, main
from bridges.chrono_mycelium import AstralTranscript
from bridges.proof_garden import ProofGarden
from mycelium.cognition.dream_compiler import DreamCompiler, build_demo_network


def clock():
    return "2026-08-24T00:00:00+00:00"


def report(tmp_path, seed):
    dream = DreamCompiler().compile(build_demo_network(seed, steps=12))
    return AstralBraidConservatory(
        AstralTranscript(tmp_path / f"bus-{seed}.jsonl"), clock=clock
    ).braid(dream)


def garden_with(ledger, tmp_path, seeds):
    garden = ProofGarden(ledger, clock=clock)
    for seed in seeds:
        garden.plant(report(tmp_path, seed))
    return garden


class TestKintsugiLedger:
    def test_golden_ledger_needs_no_repair(self, tmp_path):
        ledger = tmp_path / "garden.jsonl"
        garden_with(ledger, tmp_path, [29])
        diagnosis = KintsugiLedgerRepairer(clock=clock).diagnose(ledger)

        assert diagnosis["integrity"] == "golden"
        assert diagnosis["valid_events"] == 1
        assert diagnosis["fracture_count"] == 0

    def test_detects_first_fracture_and_dependent_suffix(self, tmp_path):
        ledger = tmp_path / "garden.jsonl"
        garden_with(ledger, tmp_path, [29, 31])
        with ledger.open("a") as stream:
            stream.write('{"kind":"braid.promoted"}\n')
        diagnosis = KintsugiLedgerRepairer(clock=clock).diagnose(ledger)

        assert diagnosis["integrity"] == "fractured"
        assert diagnosis["valid_events"] == 2
        assert diagnosis["first_fracture_line"] == 3
        assert diagnosis["fracture_count"] == 1
        assert diagnosis["fractures"][0]["classification"] == "incomplete_record"

    def test_malformed_json_is_classified_separately(self, tmp_path):
        ledger = tmp_path / "garden.jsonl"
        garden_with(ledger, tmp_path, [37])
        ledger.write_text(ledger.read_text() + "{broken\n")
        diagnosis = KintsugiLedgerRepairer(clock=clock).diagnose(ledger)

        assert diagnosis["fractures"][0]["classification"] == "malformed_json"

    def test_repair_preserves_valid_prefix_and_scars(self, tmp_path):
        ledger = tmp_path / "garden.jsonl"
        original = garden_with(ledger, tmp_path, [29, 31])
        damaged_line = '{"kind":"braid.promoted"}\n'
        with ledger.open("a") as stream:
            stream.write(damaged_line)
        result = KintsugiLedgerRepairer(clock=clock).repair(ledger)

        assert result["repaired"] is True
        assert result["preserved_events"] == 2
        assert result["quarantined_fractures"] == 1
        assert original.audit()["events"] == 2
        scar_path = tmp_path / "garden.jsonl.kintsugi.jsonl"
        scars = json.loads(scar_path.read_text().splitlines()[0])["scars"]
        assert scars[0]["raw"] == damaged_line.rstrip("\n")

    def test_repaired_garden_accepts_new_growth(self, tmp_path):
        ledger = tmp_path / "garden.jsonl"
        garden_with(ledger, tmp_path, [29])
        ledger.write_text(ledger.read_text() + "{broken\n")
        KintsugiLedgerRepairer(clock=clock).repair(ledger)
        garden = ProofGarden(ledger, clock=clock)
        garden.plant(report(tmp_path, 31))

        assert garden.audit()["events"] == 2

    def test_cli_can_diagnose_without_rewriting(self, tmp_path, capsys):
        ledger = tmp_path / "garden.jsonl"
        garden_with(ledger, tmp_path, [29])
        before = ledger.read_text()

        assert main(["--ledger", str(ledger), "diagnose"]) == 0
        parsed = json.loads(capsys.readouterr().out)
        assert parsed["integrity"] == "golden"
        assert ledger.read_text() == before

    def test_cli_repairs_fractured_ledger(self, tmp_path, capsys):
        ledger = tmp_path / "garden.jsonl"
        garden_with(ledger, tmp_path, [29])
        ledger.write_text(ledger.read_text() + "{broken\n")

        assert main(["--ledger", str(ledger), "repair"]) == 0
        assert json.loads(capsys.readouterr().out)["repaired"] is True
