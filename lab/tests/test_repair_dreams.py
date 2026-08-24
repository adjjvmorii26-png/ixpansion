import json
from pathlib import Path

import pytest

from lab.repair_dreams import build_parser, dream_is_sealed, main, weave
from lab.runtime_vault import append_jsonl


def _ledger(tmp_path: Path, name: str, records: list[dict]) -> Path:
    path = tmp_path / name
    for record in records:
        append_jsonl(path, record)
    return path


def _tamper_last(path: Path) -> None:
    lines = path.read_text().splitlines()
    record = json.loads(lines[-1])
    record["payload"] = "tampered"
    record["entry_hash"] = "f" * 64
    lines[-1] = json.dumps(record, sort_keys=True, separators=(",", ":"))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_coherent_ledger_produces_a_lucid_zero_budget_dream(tmp_path):
    ledger = _ledger(tmp_path, "source.jsonl", [
        {"event_id": "stable", "subject_id": "agent", "tick": 1}
    ])
    before = ledger.read_bytes()
    result = weave(ledgers=[ledger], record=False)

    assert result["verdict"] == "lucid"
    assert result["operation_count"] == 0
    assert result["operations"] == []
    assert result["mutation_budget"] == 0
    assert result["execution_enabled"] is False
    assert result["risk_before"]["index"] == 0
    assert result["projected_risk_after_human_execution"]["index"] == 0
    assert ledger.read_bytes() == before
    assert dream_is_sealed(result) is True


def test_state_fork_becomes_a_consent_gated_branch_dream(tmp_path):
    first = _ledger(tmp_path, "alpha.jsonl", [
        {"subject_id": "ghost", "tick": 7, "state_hash": "a" * 64}
    ])
    second = _ledger(tmp_path, "beta.jsonl", [
        {"subject_id": "ghost", "tick": 7, "state_hash": "b" * 64}
    ])
    before = (first.read_bytes(), second.read_bytes())
    result = weave(ledgers=[first, second], record=False)

    assert result["verdict"] == "quarantined_dream"
    assert result["operation_count"] == 1
    operation = result["operations"][0]
    assert operation["kind"] == "state_fork"
    assert operation["executable"] is False
    assert operation["mutation_budget"] == 0
    assert operation["consent_required"] is True
    assert operation["blueprint"]["action"] == "branch_states"
    assert operation["blueprint"]["preserved_state_hashes"] == ["a" * 64, "b" * 64]
    assert (first.read_bytes(), second.read_bytes()) == before


def test_broken_chain_is_preserved_for_backup_restore(tmp_path):
    ledger = _ledger(tmp_path, "broken.jsonl", [{"event_id": "intact"}])
    _tamper_last(ledger)
    result = weave(ledgers=[ledger], record=False)

    operation = result["operations"][0]
    assert result["verdict"] == "quarantined_dream"
    assert operation["kind"] == "broken_chain"
    assert operation["blueprint"]["action"] == "restore_from_checksummed_backup"
    assert operation["executable"] is False


def test_operation_ceiling_marks_fragmented_dream(tmp_path):
    ledger = _ledger(tmp_path, "timeline.jsonl", [
        {"event_id": "one", "subject_id": "wanderer", "tick": 9},
        {"event_id": "two", "subject_id": "wanderer", "tick": 3},
    ])
    mirror = _ledger(tmp_path, "collision.jsonl", [
        {"event_id": "one", "subject_id": "wanderer", "tick": 4}
    ])
    result = weave(ledgers=[ledger, mirror], max_operations=1, record=False)

    assert result["truncated"] is True
    assert result["verdict"] == "fragmented"
    assert result["operation_count"] == 1


def test_recorded_dream_remains_sealed_after_ledger_metadata(tmp_path, monkeypatch):
    ledger = _ledger(tmp_path, "source.jsonl", [
        {"event_id": "same", "value": 4},
    ])
    mirror = _ledger(tmp_path, "mirror.jsonl", [
        {"event_id": "same", "value": 4},
    ])
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    result = weave(ledgers=[ledger, mirror], record=True)

    stored = json.loads((tmp_path / "reports" / "repair-dreams.json").read_text())
    assert result["verdict"] == "provenance_dream"
    assert dream_is_sealed(result) is True
    assert dream_is_sealed(stored) is True
    assert result["ledger_entry_hash"] == stored["ledger_entry_hash"]
    assert (tmp_path / "ledgers" / "repair-dreams.jsonl").exists()


def test_cli_rejects_missing_ledgers_without_output(tmp_path, capsys):
    missing = tmp_path / "missing.jsonl"
    assert main([str(missing), "--no-ledger"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert "does not exist" in payload["error"]


def test_cli_writes_nothing_when_disabled(tmp_path, capsys):
    ledger = _ledger(tmp_path, "quiet.jsonl", [{"event_id": "quiet"}])
    capsys.readouterr()
    assert main([str(ledger), "--no-ledger"]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["mode"] == "data-only"
    assert not (tmp_path / "reports" / "repair-dreams.json").exists()
    assert not (tmp_path / "ledgers" / "repair-dreams.jsonl").exists()


def test_operation_limits_are_bounded():
    with pytest.raises(ValueError, match="max-operations"):
        weave(max_operations=0, record=False)


def test_parser_rejects_unknown_arguments():
    with pytest.raises(SystemExit):
        build_parser().parse_args(["--unknown"])
