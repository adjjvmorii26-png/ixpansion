import json

import pytest

from lab.pulse_oracle import forecast, seal_oracle
from lab.ritual_parliament import build_parser, deliberate, main, oracle_is_sealed
from lab.runtime_vault import read_jsonl


def state(entropy=0.90, energy=0.30):
    return {
        "entropy_budget": entropy,
        "novelty": 1.1,
        "ticks": 10,
        "phase": 0.4,
        "history": [{"tick": index, "energy": energy} for index in range(1, 8)],
    }


def oracle(entropy=0.90, energy=0.30):
    return seal_oracle(forecast(
        sandbox_state=state(entropy, energy),
        pulse_state={"beats": 8, "phase": 0.2},
        flux_state={"gen": 2},
        ledger_records=[{"type": "proof"} for _ in range(3)],
        audit={"ok": True, "tail_hash": "a" * 64, "chained_records": 3},
        horizon=5,
    ))


class TestRitualParliament:
    def test_sealed_oracle_is_accepted_and_modified_oracle_rejected(self):
        sealed = oracle()
        assert oracle_is_sealed(sealed) is True
        modified = dict(sealed)
        modified["signals"] = dict(modified["signals"])
        modified["signals"]["entropy_budget"] = 0.01
        assert oracle_is_sealed(modified) is False

    def test_favorable_regime_expands_with_first_choice_quorum(self):
        result = deliberate(oracle())
        assert result["chosen_policy"] == "expand"
        assert result["quorum_met"] is True
        assert set(result["coalition"]) == {"stabilizer", "explorer"}
        assert result["directive"]["rollback_trigger"] == "entropy_budget < 0.20"

    def test_pressure_regime_stabilizes_without_claiming_quorum(self):
        result = deliberate(oracle(entropy=0.55, energy=0.85))
        assert result["chosen_policy"] == "stabilize"
        assert result["verdict"] == "stabilize"
        assert result["quorum_met"] is False

    def test_depleted_regime_triggers_emergency_ration_veto(self):
        result = deliberate(oracle(entropy=0.18, energy=0.75))
        assert result["chosen_policy"] == "ration"
        assert result["quorum_met"] is True
        assert len(result["coalition"]) == 3
        assert result["simulations"]["expand"]["projected_budget"] < 0.20

    def test_ballots_are_bounded_deterministic_borda_votes(self):
        first = deliberate(oracle())
        second = deliberate(oracle())
        assert first == second
        assert len(first["ballots"]) == 3
        for ballot in first["ballots"]:
            assert len(ballot["scores"]) == 3
            assert all(0 <= score <= 1 for score in ballot["scores"].values())

    def test_cli_seals_directive_and_chains_observation(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
        source = tmp_path / "oracle.json"
        source.write_text(json.dumps(oracle()), encoding="utf-8")
        assert main(["--report", str(source), "--no-ledger"]) == 0
        first = json.loads(capsys.readouterr().out)
        assert first["status"] == "sealed"

        source.write_text(json.dumps(oracle()), encoding="utf-8")
        assert main(["--report", str(source)]) == 0
        second = json.loads(capsys.readouterr().out)
        records = read_jsonl(tmp_path / "ledgers" / "proof.jsonl")
        assert [record["type"] for record in records] == ["ritual_parliament"]
        assert second["parliament_hash"] == records[0]["parliament_hash"]

    def test_cli_refuses_modified_oracle(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
        source = tmp_path / "modified-oracle.json"
        modified = oracle()
        modified["verdict"] = "ration"
        source.write_text(json.dumps(modified), encoding="utf-8")
        assert main(["--report", str(source), "--no-ledger"]) == 1
        failure = json.loads(capsys.readouterr().out)
        assert failure["status"] == "refused"

    def test_pinned_manifest_contains_parliament_after_oracle(self):
        manifest = json.loads(__import__("pathlib").Path("lab/pinned_projects.json").read_text())
        ids = [item["id"] for item in manifest["projects"]]
        assert ids.index("pulse_oracle") < ids.index("ritual_parliament")

    def test_parses_custom_report(self):
        arguments = build_parser().parse_args(["--report", "/tmp/oracle.json", "--no-ledger"])
        assert arguments.no_ledger is True
