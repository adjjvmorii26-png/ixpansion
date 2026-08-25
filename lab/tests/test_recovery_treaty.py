import json
from pathlib import Path

import pytest

from lab.recovery_treaty import (
    build_parser,
    compile_treaty,
    main,
    verify_treaty,
)
from lab.runtime_vault import append_jsonl


KEY_ONE = "first-independent-out-of-band-key"
KEY_TWO = "second-independent-outbound-key"


@pytest.fixture()
def fork_sources(tmp_path):
    first = tmp_path / "alpha.jsonl"
    second = tmp_path / "beta.jsonl"
    append_jsonl(first, {"subject_id": "ghost", "tick": 7, "state_hash": "a" * 64})
    append_jsonl(second, {"subject_id": "ghost", "tick": 7, "state_hash": "b" * 64})
    return [first, second]


def _sign(sources, **overrides):
    arguments = {
        "ledgers": sources,
        "operator_one": "archivist-one",
        "operator_two": "sentinel-two",
        "nonce": "ab" * 16,
        "clock": lambda: "2026-08-25T00:00:00+00:00",
        "record": False,
    }
    arguments.update(overrides)
    return compile_treaty(**arguments)


def test_dual_key_treaty_binds_packet_without_execution_authority(fork_sources, monkeypatch):
    monkeypatch.setenv("ALEPH_TREATY_KEY_ONE", KEY_ONE)
    monkeypatch.setenv("ALEPH_TREATY_KEY_TWO", KEY_TWO)
    before = tuple(path.read_bytes() for path in fork_sources)
    result = _sign(fork_sources)

    assert result["status"] == "authorized_for_human_tribunal"
    assert result["authorization"]["signature_count"] == 2
    assert result["authorization"]["granted_authority"] == "present_to_human_tribunal"
    assert result["authorization"]["execution_enabled"] is False
    assert result["authorization"]["live_mutation_budget"] == 0
    assert result["packet"]["executable"] is False
    assert len(result["binding"]["sources"]) == 2
    assert {item["role"] for item in result["authorization"]["signatures"]} == {"steward_one", "steward_two"}
    assert tuple(path.read_bytes() for path in fork_sources) == before
    assert verify_treaty(result, ledgers=fork_sources, key_one=KEY_ONE, key_two=KEY_TWO) is True


def test_identical_keys_are_refused(fork_sources, monkeypatch):
    monkeypatch.setenv("ALEPH_TREATY_KEY_ONE", KEY_ONE)
    monkeypatch.setenv("ALEPH_TREATY_KEY_TWO", KEY_ONE)
    with pytest.raises(ValueError, match="independent"):
        _sign(fork_sources)


def test_wrong_second_key_fails_verification(fork_sources, monkeypatch):
    monkeypatch.setenv("ALEPH_TREATY_KEY_ONE", KEY_ONE)
    monkeypatch.setenv("ALEPH_TREATY_KEY_TWO", KEY_TWO)
    result = _sign(fork_sources)
    assert verify_treaty(
        result, ledgers=fork_sources, key_one=KEY_ONE, key_two="a-different-second-key!"
    ) is False


def test_any_bound_source_byte_change_voids_treaty(fork_sources, monkeypatch):
    monkeypatch.setenv("ALEPH_TREATY_KEY_ONE", KEY_ONE)
    monkeypatch.setenv("ALEPH_TREATY_KEY_TWO", KEY_TWO)
    result = _sign(fork_sources)
    append_jsonl(fork_sources[0], {"subject_id": "ghost", "tick": 8, "state_hash": "c" * 64})
    assert verify_treaty(
        result, ledgers=fork_sources, key_one=KEY_ONE, key_two=KEY_TWO
    ) is False


def test_tampered_treaty_body_fails_terminal_hash(fork_sources, monkeypatch):
    monkeypatch.setenv("ALEPH_TREATY_KEY_ONE", KEY_ONE)
    monkeypatch.setenv("ALEPH_TREATY_KEY_TWO", KEY_TWO)
    result = _sign(fork_sources)
    forged = dict(result)
    forged["operators"] = ["attacker-one", "attacker-two"]
    assert verify_treaty(
        forged, ledgers=fork_sources, key_one=KEY_ONE, key_two=KEY_TWO
    ) is False


def test_duplicate_operator_labels_are_refused(fork_sources):
    with pytest.raises(ValueError, match="distinct operator labels"):
        _sign(fork_sources, operator_one="same", operator_two="same")


def test_signed_operation_budget_survives_verification_roundtrip(fork_sources, monkeypatch):
    monkeypatch.setenv("ALEPH_TREATY_KEY_ONE", KEY_ONE)
    monkeypatch.setenv("ALEPH_TREATY_KEY_TWO", KEY_TWO)
    result = _sign(fork_sources, max_operations=5)

    assert result["binding"]["lineage_parameters"] == {"max_operations": 5}
    assert verify_treaty(result, ledgers=fork_sources, key_one=KEY_ONE, key_two=KEY_TWO)
    assert verify_treaty(
        result,
        ledgers=fork_sources,
        key_one=KEY_ONE,
        key_two=KEY_TWO,
        max_operations=5,
    )
    assert verify_treaty(
        result,
        ledgers=fork_sources,
        key_one=KEY_ONE,
        key_two=KEY_TWO,
        max_operations=6,
    ) is False


def test_broken_journey_cannot_be_signed(tmp_path, monkeypatch):
    monkeypatch.setenv("ALEPH_TREATY_KEY_ONE", KEY_ONE)
    monkeypatch.setenv("ALEPH_TREATY_KEY_TWO", KEY_TWO)
    ledger = tmp_path / "broken.jsonl"
    append_jsonl(ledger, {"event_id": "intact"})
    lines = ledger.read_text().splitlines()
    record = json.loads(lines[0])
    record["payload"] = "changed"
    record["entry_hash"] = "f" * 64
    lines[0] = json.dumps(record, sort_keys=True, separators=(",", ":"))
    ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="consent_ready"):
        _sign([ledger])


def test_recorded_treaty_remains_verifiable_after_ledger_metadata(
    fork_sources, tmp_path, monkeypatch
):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    monkeypatch.setenv("ALEPH_TREATY_KEY_ONE", KEY_ONE)
    monkeypatch.setenv("ALEPH_TREATY_KEY_TWO", KEY_TWO)
    result = _sign(fork_sources, record=True)

    stored = json.loads((tmp_path / "reports" / "recovery-treaty.json").read_text())
    assert result["treaty_hash"] == stored["treaty_hash"]
    assert verify_treaty(
        stored, ledgers=fork_sources, key_one=KEY_ONE, key_two=KEY_TWO
    ) is True
    assert (tmp_path / "ledgers" / "recovery-treaties.jsonl").is_file()


def test_cli_sign_and_verify_use_environment_keys(fork_sources, tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    monkeypatch.setenv("ALEPH_TREATY_KEY_ONE", KEY_ONE)
    monkeypatch.setenv("ALEPH_TREATY_KEY_TWO", KEY_TWO)
    source_args = [str(path) for path in fork_sources]
    assert main(["sign", *source_args, "--operator-one", "one", "--operator-two", "two"]) == 0
    signed = json.loads(capsys.readouterr().out)
    assert signed["authorization"]["execution_enabled"] is False

    assert main(["verify", *source_args]) == 0
    verified = json.loads(capsys.readouterr().out)
    assert verified["ok"] is True


def test_parser_requires_a_command():
    with pytest.raises(SystemExit):
        build_parser().parse_args([])
