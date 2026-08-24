import json
from pathlib import Path

import pytest

from lab.runtime_vault import append_jsonl, read_jsonl
from lab.temporal_paradox import build_parser, main, resolve, resolver_is_sealed


def _ledger(tmp_path: Path, name: str, records: list[dict]) -> Path:
    path = tmp_path / name
    for record in records:
        append_jsonl(path, record)
    return path


def _tamper_last(path: Path) -> None:
    lines = path.read_text().splitlines()
    record = json.loads(lines[-1])
    record["payload"] = "changed"
    record["entry_hash"] = "f" * 64
    lines[-1] = json.dumps(record, sort_keys=True, separators=(",", ":"))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_coherent_ledgers_are_preserved_and_declared_clean(tmp_path):
    first = _ledger(tmp_path, "first.jsonl", [
        {"event_id": "pulse-a", "subject_id": "sentinel", "tick": 1, "status": "active"},
        {"event_id": "pulse-b", "subject_id": "sentinel", "tick": 2, "status": "active"},
    ])
    second = _ledger(tmp_path, "second.jsonl", [
        {"event_id": "pulse-c", "subject_id": "architect", "tick": 4, "status": "active"},
    ])
    before = {path: path.read_bytes() for path in (first, second)}

    result = resolve(ledgers=[first, second], record=False)

    assert result["verdict"] == "coherent"
    assert result["mutation_budget"] == 0
    assert result["paradox_count"] == 0
    assert result["sources"]["ledger_count"] == 2
    assert all(audit["ok"] for audit in result["sources"]["audits"].values())
    assert {path.read_bytes() for path in (first, second)} == set(before.values())
    assert resolver_is_sealed(result) is True


def test_cross_ledger_event_collision_is_critical(tmp_path):
    first = _ledger(tmp_path, "alpha.jsonl", [
        {"event_id": "genesis", "state_hash": "a" * 64},
    ])
    second = _ledger(tmp_path, "beta.jsonl", [
        {"event_id": "genesis", "state_hash": "b" * 64},
    ])
    result = resolve(ledgers=[first, second], record=False)

    kinds = {item["kind"] for item in result["paradoxes"]}
    assert result["verdict"] == "paradox"
    assert "identity_collision" in kinds
    assert any(item["severity"] == "critical" for item in result["paradoxes"])
    assert "split each fork" in result["resolutions"][0]


def test_identical_cross_ledger_repeat_is_only_replay_evidence(tmp_path):
    first = _ledger(tmp_path, "origin.jsonl", [{"event_id": "same", "value": 7}])
    second = _ledger(tmp_path, "mirror.jsonl", [{"event_id": "same", "value": 7}])
    result = resolve(ledgers=[first, second], record=False)

    assert result["verdict"] == "unstable"
    assert [item["kind"] for item in result["paradoxes"]] == ["replay_echo"]
    assert result["paradoxes"][0]["severity"] == "warning"


def test_clock_regression_is_unstable_but_not_corruption(tmp_path):
    ledger = _ledger(tmp_path, "clock.jsonl", [
        {"subject_id": "wanderer", "tick": 9},
        {"subject_id": "wanderer", "tick": 3},
    ])
    result = resolve(ledgers=[ledger], record=False)

    assert result["verdict"] == "unstable"
    assert result["paradoxes"][0]["kind"] == "causal_regression"
    assert result["paradoxes"][0]["evidence"]["prior_tick"] == 9


def test_state_fork_and_broken_chain_fail_closed(tmp_path):
    first = _ledger(tmp_path, "fork.jsonl", [
        {"event_id": "one", "subject_id": "ghost", "tick": 1, "state_hash": "a" * 64},
    ])
    second = _ledger(tmp_path, "fork-mirror.jsonl", [
        {"event_id": "two", "subject_id": "ghost", "tick": 1, "state_hash": "b" * 64},
    ])
    third = _ledger(tmp_path, "broken.jsonl", [{"event_id": "intact"}])
    _tamper_last(third)
    result = resolve(ledgers=[first, second, third], record=False)

    kinds = {item["kind"] for item in result["paradoxes"]}
    assert {"state_fork", "broken_chain"} <= kinds
    assert result["sources"]["corrupt_ledger_count"] == 1
    assert "quarantine the affected ledger" in result["resolutions"][0]


def test_recorded_report_survives_ledger_metadata(tmp_path, monkeypatch):
    ledger = _ledger(tmp_path, "source.jsonl", [{"event_id": "stable", "value": 1}])
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    result = resolve(ledgers=[ledger], record=True)

    stored = json.loads((tmp_path / "reports" / "temporal-paradox.json").read_text())
    assert resolver_is_sealed(result) is True
    assert resolver_is_sealed(stored) is True
    assert result["ledger_entry_hash"] == stored["ledger_entry_hash"]
    assert len(read_jsonl(tmp_path / "ledgers" / "paradox-resolutions.jsonl")) == 1


def test_cli_explicit_ledgers_write_nothing_when_disabled(tmp_path, capsys):
    ledger = _ledger(tmp_path, "cli.jsonl", [{"event_id": "quiet", "value": 1}])
    capsys.readouterr()
    assert main([str(ledger), "--no-ledger"]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["mode"] == "read-only"
    assert not (tmp_path / "reports" / "temporal-paradox.json").exists()
    assert not (tmp_path / "ledgers" / "paradox-resolutions.jsonl").exists()


def test_parser_rejects_unknown_arguments():
    with pytest.raises(SystemExit):
        build_parser().parse_args(["--unknown"])
