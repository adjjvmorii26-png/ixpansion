"""Regression tests for malformed and tampered Runtime Vault ledger chains."""
import json

import pytest

from lab.runtime_vault import append_jsonl, verify_jsonl


def test_malformed_sequence_is_reported_not_raised(tmp_path):
    ledger = tmp_path / "malformed-sequence.jsonl"
    # Presence of chain fields opts this record into chain validation. A string
    # that cannot be converted to int must be a validation failure, not a crash.
    ledger.write_text(json.dumps({
        "sequence": "not-an-integer",
        "previous_hash": "0" * 64,
        "entry_hash": "0" * 64,
        "event": "probe",
    }) + "\n", encoding="utf-8")

    result = verify_jsonl(ledger)

    assert result["ok"] is False
    assert result["failure"]["kind"] == "invalid_chain_metadata"
    assert result["failure"]["line"] == 1


def test_boolean_sequence_is_not_accepted_as_integer(tmp_path):
    ledger = tmp_path / "boolean-sequence.jsonl"
    ledger.write_text(json.dumps({
        "sequence": True,
        "previous_hash": "0" * 64,
        "entry_hash": "0" * 64,
        "event": "probe",
    }) + "\n", encoding="utf-8")

    result = verify_jsonl(ledger)

    assert result["ok"] is False
    assert result["failure"]["kind"] == "invalid_chain_metadata"


def test_valid_chained_ledger_still_verifies(tmp_path):
    ledger = tmp_path / "valid.jsonl"
    append_jsonl(ledger, {"type": "test", "value": 1})
    append_jsonl(ledger, {"type": "test", "value": 2})

    result = verify_jsonl(ledger)

    assert result["ok"] is True
    assert result["chained_records"] == 2
    assert result["failure"] is None


def test_legacy_records_after_chain_remain_rejected(tmp_path):
    ledger = tmp_path / "legacy-after-chain.jsonl"
    append_jsonl(ledger, {"type": "test", "value": 1})
    with ledger.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"type": "legacy", "value": 2}) + "\n")

    result = verify_jsonl(ledger)

    assert result["ok"] is False
    assert result["failure"]["kind"] == "legacy_after_chain"


@pytest.mark.parametrize("sequence", [0, -1])
def test_append_rejects_non_positive_existing_sequence(tmp_path, sequence):
    ledger = tmp_path / "invalid-tail.jsonl"
    ledger.write_text(json.dumps({
        "sequence": sequence,
        "previous_hash": "0" * 64,
        "entry_hash": "0" * 64,
        "event": "probe",
    }) + "\\n", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid chain metadata"):
        append_jsonl(ledger, {"event": "should-not-append"})


def test_append_rejects_malformed_existing_entry_hash(tmp_path):
    ledger = tmp_path / "invalid-tail-hash.jsonl"
    ledger.write_text(json.dumps({
        "sequence": 1,
        "previous_hash": "0" * 64,
        "entry_hash": "not-a-sha256-digest",
        "event": "probe",
    }) + "\\n", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid chain metadata"):
        append_jsonl(ledger, {"event": "should-not-append"})
