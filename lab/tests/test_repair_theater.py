import json
from pathlib import Path

import pytest

from lab.repair_theater import build_parser, main, rehearse, theater_is_sealed
from lab.runtime_vault import append_jsonl


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


def test_coherent_ledgers_leave_an_empty_forbidden_stage(tmp_path):
    first = _ledger(tmp_path, "one.jsonl", [{"event_id": "a", "subject_id": "agent", "tick": 1}])
    second = _ledger(tmp_path, "two.jsonl", [{"event_id": "b", "subject_id": "agent", "tick": 2}])
    before = (first.read_bytes(), second.read_bytes())
    result = rehearse(ledgers=[first, second], record=False)

    assert result["verdict"] == "empty_stage"
    assert result["stage_count"] == 0
    assert result["branch_count"] == 0
    assert result["average_stability"] == 1.0
    assert result["execution_enabled"] is False
    assert result["live_mutation_budget"] == 0
    assert result["source_audits_ok"] is True
    assert (first.read_bytes(), second.read_bytes()) == before
    assert theater_is_sealed(result) is True


def test_state_fork_stages_every_conflicting_ghost_branch(tmp_path):
    first = _ledger(tmp_path, "alpha.jsonl", [
        {"subject_id": "ghost", "tick": 7, "state_hash": "a" * 64}
    ])
    second = _ledger(tmp_path, "beta.jsonl", [
        {"subject_id": "ghost", "tick": 7, "state_hash": "b" * 64}
    ])
    before = (first.read_bytes(), second.read_bytes())
    result = rehearse(ledgers=[first, second], record=False)

    assert result["verdict"] == "branches_staged"
    scene = result["scenes"][0]
    assert scene["kind"] == "state_fork"
    assert scene["status"] == "staged"
    assert scene["consent_required"] is True
    assert scene["execution_enabled"] is False
    assert len(scene["branches"]) == 2
    assert {branch["ghost_event"]["state_hash"] for branch in scene["branches"]} == {"a" * 64, "b" * 64}
    assert scene["stability"] == 0.82
    assert (first.read_bytes(), second.read_bytes()) == before


def test_clock_regression_splits_anchor_and_side_timeline(tmp_path):
    ledger = _ledger(tmp_path, "clock.jsonl", [
        {"subject_id": "wanderer", "tick": 9},
        {"subject_id": "wanderer", "tick": 3},
    ])
    result = rehearse(ledgers=[ledger], record=False)
    scene = result["scenes"][0]

    labels = {branch["label"] for branch in scene["branches"]}
    assert scene["kind"] == "causal_regression"
    assert labels == {"anchor", "side-timeline"}
    assert scene["stability"] == 0.78
    assert all(branch["ghost_event"]["subject_id"] == "wanderer" for branch in scene["branches"])


def test_identity_collision_partitions_incompatible_variants(tmp_path):
    first = _ledger(tmp_path, "origin.jsonl", [
        {"event_id": "genesis", "shape": "circle"}
    ])
    second = _ledger(tmp_path, "mirror.jsonl", [
        {"event_id": "genesis", "shape": "square"}
    ])
    result = rehearse(ledgers=[first, second], record=False)
    scene = result["scenes"][0]

    assert scene["kind"] == "identity_collision"
    assert len(scene["branches"]) == 2
    assert len({branch["label"] for branch in scene["branches"]}) == 2
    assert {branch["ghost_event"]["shape"] for branch in scene["branches"]} == {"circle", "square"}
    assert scene["stability"] == 0.76


def test_identical_replay_is_retained_without_branch_mutation(tmp_path):
    first = _ledger(tmp_path, "origin.jsonl", [{"event_id": "same", "value": 4}])
    second = _ledger(tmp_path, "mirror.jsonl", [{"event_id": "same", "value": 4}])
    result = rehearse(ledgers=[first, second], record=False)

    assert result["verdict"] == "provenance_retained"
    assert result["scenes"][0]["status"] == "retained"
    assert len(result["scenes"][0]["branches"]) == 2
    assert result["live_mutation_budget"] == 0


def test_broken_chain_is_quarantined_not_repaired(tmp_path):
    ledger = _ledger(tmp_path, "broken.jsonl", [{"event_id": "intact"}])
    _tamper_last(ledger)
    result = rehearse(ledgers=[ledger], record=False)

    assert result["source_audits_ok"] is False
    assert result["verdict"] == "quarantined_stage"
    assert result["scenes"][0]["status"] == "quarantined"
    assert result["scenes"][0]["branches"] == []


def test_recorded_theater_remains_sealed_after_transport_metadata(tmp_path, monkeypatch):
    ledger = _ledger(tmp_path, "fork.jsonl", [
        {"subject_id": "ghost", "tick": 1, "state_hash": "a" * 64}
    ])
    mirror = _ledger(tmp_path, "fork-mirror.jsonl", [
        {"subject_id": "ghost", "tick": 1, "state_hash": "b" * 64}
    ])
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    result = rehearse(ledgers=[ledger, mirror], record=True)

    stored = json.loads((tmp_path / "reports" / "repair-theater.json").read_text())
    assert theater_is_sealed(result) is True
    assert theater_is_sealed(stored) is True
    assert result["ledger_entry_hash"] == stored["ledger_entry_hash"]
    assert (tmp_path / "ledgers" / "repair-theater.jsonl").exists()


def test_cli_explicit_rehearsal_writes_nothing_when_disabled(tmp_path, capsys):
    ledger = _ledger(tmp_path, "quiet.jsonl", [{"event_id": "quiet"}])
    capsys.readouterr()
    assert main([str(ledger), "--no-ledger"]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["mode"] == "synthetic-rehearsal"
    assert not (tmp_path / "reports" / "repair-theater.json").exists()
    assert not (tmp_path / "ledgers" / "repair-theater.jsonl").exists()


def test_missing_ledger_fails_closed():
    with pytest.raises(ValueError, match="does not exist"):
        rehearse(ledgers=[Path("/tmp/aleph-missing-ledger.jsonl")], record=False)


def test_operation_ceiling_is_bounded():
    with pytest.raises(ValueError, match="max-operations"):
        rehearse(max_operations=33, record=False)


def test_parser_rejects_unknown_arguments():
    with pytest.raises(SystemExit):
        build_parser().parse_args(["--unknown"])
