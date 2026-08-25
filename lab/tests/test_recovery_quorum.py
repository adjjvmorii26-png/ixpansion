import json
from pathlib import Path

import pytest

from lab.recovery_quorum import build_parser, convene, main, quorum_is_sealed
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


def test_coherent_sources_remain_dormant_without_packets(tmp_path):
    first = _ledger(tmp_path, "one.jsonl", [{"event_id": "a", "subject_id": "agent", "tick": 1}])
    second = _ledger(tmp_path, "two.jsonl", [{"event_id": "b", "subject_id": "agent", "tick": 2}])
    before = (first.read_bytes(), second.read_bytes())
    result = convene(ledgers=[first, second], record=False)

    assert result["verdict"] == "dormant"
    assert result["scene_count"] == 0
    assert result["consent_packet_count"] == 0
    assert result["execution_enabled"] is False
    assert result["live_mutation_budget"] == 0
    assert (first.read_bytes(), second.read_bytes()) == before
    assert quorum_is_sealed(result) is True


def test_state_fork_reaches_advisory_quorum_and_creates_packet(tmp_path):
    first = _ledger(tmp_path, "alpha.jsonl", [
        {"subject_id": "ghost", "tick": 7, "state_hash": "a" * 64}
    ])
    second = _ledger(tmp_path, "beta.jsonl", [
        {"subject_id": "ghost", "tick": 7, "state_hash": "b" * 64}
    ])
    before = (first.read_bytes(), second.read_bytes())
    result = convene(ledgers=[first, second], record=False)
    scene = result["scenes"][0]

    assert result["verdict"] == "consent_ready"
    assert result["consent_packet_count"] == 1
    assert scene["offices"] == {"archivist": "support", "sentinel": "review", "explorer": "support"}
    assert scene["quorum_met"] is True
    assert scene["recommendation"] == "prepare_consent_packet"
    packet = result["consent_packets"][0]
    assert packet["required_human_signatures"] == 2
    assert packet["executable"] is False
    assert packet["mutation_budget"] == 0
    assert (first.read_bytes(), second.read_bytes()) == before


def test_clock_regression_boundary_does_not_absorb_future_events(tmp_path):
    ledger = _ledger(tmp_path, "clock.jsonl", [
        {"subject_id": "wanderer", "tick": 9},
        {"subject_id": "wanderer", "tick": 3},
        {"subject_id": "wanderer", "tick": 12},
    ])
    result = convene(ledgers=[ledger], record=False)
    scene = result["scenes"][0]

    ticks = [branch["ghost_event"]["tick"] for branch in scene["branches"]]
    assert result["verdict"] == "consent_ready"
    assert sorted(ticks) == [3, 9]
    assert 12 not in ticks


def test_broken_chain_requires_human_tribunal(tmp_path):
    ledger = _ledger(tmp_path, "broken.jsonl", [{"event_id": "intact"}])
    _tamper_last(ledger)
    result = convene(ledgers=[ledger], record=False)

    assert result["source_audits_ok"] is False
    assert result["verdict"] == "tribunal_required"
    assert result["scenes"][0]["blocks"] >= 2
    assert result["consent_packet_count"] == 0


def test_identical_replay_is_preserved_without_mutation_packet(tmp_path):
    first = _ledger(tmp_path, "origin.jsonl", [{"event_id": "same", "value": 4}])
    second = _ledger(tmp_path, "mirror.jsonl", [{"event_id": "same", "value": 4}])
    result = convene(ledgers=[first, second], record=False)

    assert result["verdict"] == "provenance_preserved"
    assert result["consent_packet_count"] == 0
    assert result["scenes"][0]["recommendation"] == "preserve_provenance"


def test_blocked_scene_overrides_any_ready_scene(tmp_path):
    good_a = _ledger(tmp_path, "good-a.jsonl", [
        {"subject_id": "ghost", "tick": 1, "state_hash": "a" * 64}
    ])
    good_b = _ledger(tmp_path, "good-b.jsonl", [
        {"subject_id": "ghost", "tick": 1, "state_hash": "b" * 64}
    ])
    bad = _ledger(tmp_path, "bad.jsonl", [{"subject_id": "ghost", "status": "terminated"}])
    later = _ledger(tmp_path, "later.jsonl", [
        {"subject_id": "ghost", "status": "active"}
    ])
    result = convene(ledgers=[good_a, good_b, bad, later], record=False)

    assert result["verdict"] == "tribunal_required"
    assert any(scene["blocks"] for scene in result["scenes"])
    assert all(packet["executable"] is False for packet in result["consent_packets"])
    assert result["live_mutation_budget"] == 0


def test_recorded_quorum_remains_sealed_after_transport_metadata(tmp_path, monkeypatch):
    first = _ledger(tmp_path, "fork.jsonl", [
        {"subject_id": "ghost", "tick": 3, "state_hash": "a" * 64}
    ])
    second = _ledger(tmp_path, "fork-mirror.jsonl", [
        {"subject_id": "ghost", "tick": 3, "state_hash": "b" * 64}
    ])
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    result = convene(ledgers=[first, second], record=True)

    stored = json.loads((tmp_path / "reports" / "recovery-quorum.json").read_text())
    assert quorum_is_sealed(result) is True
    assert quorum_is_sealed(stored) is True
    assert result["ledger_entry_hash"] == stored["ledger_entry_hash"]
    assert (tmp_path / "ledgers" / "recovery-quorums.jsonl").exists()


def test_cli_writes_nothing_when_disabled(tmp_path, capsys):
    ledger = _ledger(tmp_path, "quiet.jsonl", [{"event_id": "quiet"}])
    capsys.readouterr()
    assert main([str(ledger), "--no-ledger"]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["mode"] == "advisory-consensus"
    assert not (tmp_path / "reports" / "recovery-quorum.json").exists()
    assert not (tmp_path / "ledgers" / "recovery-quorums.jsonl").exists()


def test_missing_ledger_fails_closed():
    with pytest.raises(ValueError, match="does not exist"):
        convene(ledgers=[Path("/tmp/aleph-missing-quorum-ledger.jsonl")], record=False)


def test_limits_and_parser_fail_closed():
    with pytest.raises(ValueError, match="max-operations"):
        convene(max_operations=33, record=False)
    with pytest.raises(SystemExit):
        build_parser().parse_args(["--unknown"])
