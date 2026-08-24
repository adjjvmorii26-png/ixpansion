import copy
import json

import pytest

from lab.reversible_mandate import (
    HARD_TICK_CAP,
    build_parser,
    execute,
    main,
    parliament_is_sealed,
    rehearse,
)
from lab.runtime_vault import append_jsonl, ledger_path, read_json, read_jsonl, state_path
from lab.ritual_parliament import deliberate
from lab.pulse_oracle import forecast, seal_oracle


def sandbox_state(entropy=0.90, energy=0.30, ticks=10):
    return {
        "entropy_budget": entropy,
        "novelty": 1.1,
        "ticks": ticks,
        "phase": 0.4,
        "status": "idle",
        "history": [{"tick": index, "energy": energy} for index in range(1, 8)],
    }


def parliament(entropy=0.90, energy=0.30):
    sealed_oracle = seal_oracle(forecast(
        sandbox_state=sandbox_state(entropy, energy),
        pulse_state={"beats": 8, "phase": 0.2},
        flux_state={"gen": 2},
        ledger_records=[{"type": "proof"}],
        audit={"ok": True, "tail_hash": "a" * 64, "chained_records": 3},
        horizon=5,
    ))
    return deliberate(sealed_oracle)


def install_world(tmp_path, monkeypatch, state=None):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    path = state_path("sandbox", "engine.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    world = state or sandbox_state()
    path.write_text(json.dumps(world), encoding="utf-8")
    return world


class TestReversibleMandate:
    def test_rehearsal_is_bounded_and_does_not_mutate_live_state(self, tmp_path, monkeypatch):
        original = install_world(tmp_path, monkeypatch)
        ghost, ticks = rehearse(original, parliament(), max_ticks=HARD_TICK_CAP)
        assert ticks == 3
        assert ghost["ticks"] == original["ticks"] + 3
        assert original == sandbox_state()

    def test_dry_run_preserves_world_and_omits_ledger_witnesses(self, tmp_path, monkeypatch):
        install_world(tmp_path, monkeypatch)
        result = execute(parliament(), dry_run=True)
        assert result["status"] == "rehearsed"
        assert result["planned_ticks"] == 3
        assert result["execution_certificate"]
        assert read_json(state_path("sandbox", "engine.json")) == sandbox_state()
        assert ledger_path().exists() is False

    def test_execution_seals_each_tick_and_a_completion_record(self, tmp_path, monkeypatch):
        install_world(tmp_path, monkeypatch)
        result = execute(parliament())
        records = read_jsonl(ledger_path())
        assert result["status"] == "sealed"
        assert result["planned_ticks"] == 3
        assert len(result["witnesses"]) == 3
        assert [item["type"] for item in records] == ["mandate_tick"] * 3 + ["mandate_complete"]
        assert all(record["entry_hash"] for record in records)
        live = read_json(state_path("sandbox", "engine.json"))
        assert live["ticks"] == 13
        assert live["entropy_budget"] == result["final_entropy_budget"]
        report = read_json(tmp_path / "reports" / "reversible-mandate.json")
        assert report["execution_certificate"] == result["execution_certificate"]

    def test_modified_parliament_fails_closed(self, tmp_path, monkeypatch):
        install_world(tmp_path, monkeypatch)
        mandate = parliament()
        mandate["chosen_policy"] = "ration"
        result = execute(mandate)
        assert result == {
            "schema": "aleph.chronoforge.reversible-mandate.v1",
            "experiment": "reversible-mandate",
            "status": "refused",
            "reason": "missing, unsealed, or modified parliament",
        }
        assert ledger_path().exists() is False

    def test_stale_sandbox_tick_fails_closed(self, tmp_path, monkeypatch):
        install_world(tmp_path, monkeypatch, sandbox_state(ticks=11))
        result = execute(parliament())
        assert result["status"] == "refused"
        assert result["reason"] == "mandate is stale relative to sandbox ticks"
        assert ledger_path().exists() is False

    def test_witness_failure_restores_pre_mandate_world(self, tmp_path, monkeypatch):
        original = install_world(tmp_path, monkeypatch)
        real_append = append_jsonl

        def fail_after_first(path, record):
            if record.get("type") == "mandate_tick" and record.get("tick") == 12:
                raise OSError("witness seal failed")
            return real_append(path, record)

        monkeypatch.setattr("lab.reversible_mandate.append_jsonl", fail_after_first)
        result = execute(parliament())
        assert result["status"] == "rolled_back"
        assert result["executed_witnesses"] == 1
        assert result["restored_entropy_budget"] == original["entropy_budget"]
        assert read_json(state_path("sandbox", "engine.json")) == original
        types = [record["type"] for record in read_jsonl(ledger_path())]
        assert types == ["mandate_tick", "mandate_rollback"]

    def test_cli_supports_report_input_and_bounded_ticks(self, tmp_path, monkeypatch, capsys):
        install_world(tmp_path, monkeypatch)
        source = tmp_path / "parliament.json"
        source.write_text(json.dumps(parliament()), encoding="utf-8")
        assert main(["--report", str(source), "--max-ticks", "2"]) == 0
        result = json.loads(capsys.readouterr().out)
        assert result["status"] == "sealed"
        assert result["planned_ticks"] == 2
        assert read_json(state_path("sandbox", "engine.json"))["ticks"] == 12

    def test_sealed_checker_and_cli_bounds_are_explicit(self):
        mandate = parliament()
        assert parliament_is_sealed(mandate) is True
        assert build_parser().parse_args(["--max-ticks", str(HARD_TICK_CAP)]).max_ticks == HARD_TICK_CAP
