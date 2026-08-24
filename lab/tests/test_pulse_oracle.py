import json

import pytest

from lab.pulse_oracle import build_parser, collect, forecast, main


def state(entropy=0.90, energy=0.30, ticks=10):
    history = [{"tick": index, "energy": energy} for index in range(1, 8)]
    return {
        "entropy_budget": entropy,
        "novelty": 1.2,
        "ticks": ticks,
        "phase": 0.4,
        "history": history,
    }


def sources():
    sandbox = state()
    pulse = {"beats": 24, "phase": 0.7}
    flux = {"gen": 5}
    return sandbox, pulse, flux


class TestPulseOracle:
    def test_favorable_state_expands_with_reversible_recommendations(self):
        sandbox, pulse, flux = sources()
        result = forecast(
            sandbox_state=sandbox, pulse_state=pulse, flux_state=flux,
            ledger_records=[{"type": "pinned_run"}],
            audit={"ok": True, "tail_hash": "a" * 64}, horizon=3,
        )
        assert result["verdict"] == "expand"
        assert len(result["forecast"]["projections"]) == 3
        assert result["forecast"]["projected_entropy_budget"] < 0.90
        assert result["oracle_hash"]

    def test_depleted_budget_rations_and_preserves_hard_floor(self):
        sandbox = state(entropy=0.22, energy=0.8)
        result = forecast(
            sandbox_state=sandbox, pulse_state={"beats": 4, "phase": 0},
            flux_state={}, ledger_records=[], audit={"ok": True, "tail_hash": ""},
            horizon=9,
        )
        assert result["verdict"] == "ration"
        assert result["forecast"]["projected_entropy_budget"] >= 0.05
        assert any(item["ritual"] == "entropy_fast" for item in result["recommendations"])

    def test_forecast_is_deterministic_for_identical_evidence(self):
        args = dict(
            sandbox_state=state(), pulse_state={"beats": 8, "phase": 0.2},
            flux_state={"gen": 2}, ledger_records=[{"type": "proof"}],
            audit={"ok": True, "tail_hash": "b" * 64}, horizon=5,
        )
        assert forecast(**args) == forecast(**args)

    def test_rejects_invalid_horizon(self):
        with pytest.raises(ValueError):
            forecast(sandbox_state=state(), pulse_state={}, flux_state={},
                     ledger_records=[], audit={"ok": True}, horizon=0)

    def test_cli_seals_report_and_chains_observation(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
        (tmp_path / "state" / "sandbox").mkdir(parents=True)
        (tmp_path / "state" / "pulse").mkdir()
        (tmp_path / "state" / "worlds").mkdir()
        (tmp_path / "state" / "sandbox" / "engine.json").write_text(json.dumps(state()))
        (tmp_path / "state" / "pulse" / "state.json").write_text(json.dumps({"beats": 2, "phase": 1}))
        (tmp_path / "state" / "worlds" / "flux.json").write_text(json.dumps({"gen": 1}))
        assert main(["--no-ledger"]) == 0
        first = json.loads(capsys.readouterr().out)
        assert first["status"] == "sealed"
        assert (tmp_path / "reports" / "pulse-oracle.json").exists()

        assert main([]) == 0
        second = json.loads(capsys.readouterr().out)
        assert second["status"] == "sealed"
        assert second["signals"]["ledger_records"] == 0
        from lab.runtime_vault import read_jsonl
        assert [item["type"] for item in read_jsonl(tmp_path / "ledgers" / "proof.jsonl")] == ["pulse_oracle"]

    def test_cli_fails_closed_on_tampered_ledger(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
        from lab.runtime_vault import append_jsonl
        ledger = tmp_path / "ledgers" / "proof.jsonl"
        append_jsonl(ledger, {"value": 1})
        lines = ledger.read_text().splitlines()
        record = json.loads(lines[0])
        record["value"] = 999
        record["entry_hash"] = "f" * 64
        ledger.write_text(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
        assert main(["--no-ledger"]) == 1
        result = json.loads(capsys.readouterr().out)
        assert result["status"] == "refused"

    def test_parser_bounds_are_documented(self):
        arguments = build_parser().parse_args(["--horizon", "30"])
        assert arguments.horizon == 30
