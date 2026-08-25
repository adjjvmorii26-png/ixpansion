import json
from pathlib import Path

import pytest

from lab.recovery_dossier import compile_dossier
from lab.recovery_treaty import compile_treaty
from lab.recovery_verdict import build_parser, main, record_verdict, verify_verdict
from lab.runtime_vault import append_jsonl


TREATY_KEY_ONE = "first-treaty-out-of-band-key"
TREATY_KEY_TWO = "second-treaty-out-of-band-key"
VERDICT_KEY_ONE = "first-juror-out-of-band-key"
VERDICT_KEY_TWO = "second-juror-out-of-band-key"
FIXED_CLOCK = lambda: "2026-08-25T02:00:00+00:00"


@pytest.fixture()
def sealed_dossier(tmp_path):
    first = tmp_path / "alpha.jsonl"
    second = tmp_path / "beta.jsonl"
    append_jsonl(first, {"subject_id": "ghost", "tick": 7, "state_hash": "a" * 64})
    append_jsonl(second, {"subject_id": "ghost", "tick": 7, "state_hash": "b" * 64})
    sources = [first, second]
    treaty = compile_treaty(
        ledgers=sources,
        operator_one="archivist",
        operator_two="sentinel",
        key_one=TREATY_KEY_ONE,
        key_two=TREATY_KEY_TWO,
        nonce="ef" * 16,
        clock=FIXED_CLOCK,
        record=False,
    )
    dossier = compile_dossier(
        treaty,
        ledgers=sources,
        key_one=TREATY_KEY_ONE,
        key_two=TREATY_KEY_TWO,
        clock=FIXED_CLOCK,
        record=False,
    )
    return sources, dossier


def _record(dossier, sources, verdict="approve", **overrides):
    arguments = {
        "ledgers": sources,
        "rationale": "The ghost branches preserve every conflicting witness safely.",
        "operator_one": "juror-one",
        "operator_two": "juror-two",
        "decision_key_one": VERDICT_KEY_ONE,
        "decision_key_two": VERDICT_KEY_TWO,
        "treaty_key_one": TREATY_KEY_ONE,
        "treaty_key_two": TREATY_KEY_TWO,
        "nonce": "ab" * 16,
        "clock": FIXED_CLOCK,
        "record": False,
    }
    arguments.update(overrides)
    return record_verdict(dossier, verdict=verdict, **arguments)


def test_approved_verdict_remains_completely_non_executable(sealed_dossier):
    sources, dossier = sealed_dossier
    before = tuple(path.read_bytes() for path in sources)
    result = _record(dossier, sources)

    assert result["status"] == "approved_for_separate_executor_contract"
    assert result["authorization"]["execution_enabled"] is False
    assert result["authorization"]["compatible_executors"] == []
    assert result["authorization"]["live_mutation_budget"] == 0
    assert result["authorization"]["executor_contract_required"] is True
    assert result["authorization"]["next_permitted_action"] == "draft_independent_executor_contract_for_review"
    assert len(result["authorization"]["signatures"]) == 2
    assert tuple(path.read_bytes() for path in sources) == before
    assert verify_verdict(
        result,
        ledgers=sources,
        decision_key_one=VERDICT_KEY_ONE,
        decision_key_two=VERDICT_KEY_TWO,
        treaty_key_one=TREATY_KEY_ONE,
        treaty_key_two=TREATY_KEY_TWO,
    ) is True


@pytest.mark.parametrize("verdict,status,next_action", [
    ("approve", "approved_for_separate_executor_contract", "draft_independent_executor_contract_for_review"),
    ("reject", "rejected", "archive_without_execution"),
    ("defer", "deferred", "retain_dossier_for_future_tribunal"),
])
def test_all_verdicts_map_to_safe_next_actions(sealed_dossier, verdict, status, next_action):
    sources, dossier = sealed_dossier
    result = _record(dossier, sources, verdict=verdict)
    assert result["status"] == status
    assert result["authorization"]["next_permitted_action"] == next_action
    assert result["authorization"]["execution_enabled"] is False


def test_identical_juror_keys_are_refused(sealed_dossier):
    sources, dossier = sealed_dossier
    with pytest.raises(ValueError, match="independent"):
        _record(dossier, sources, decision_key_two=VERDICT_KEY_ONE)


def test_wrong_second_juror_fails_verification(sealed_dossier):
    sources, dossier = sealed_dossier
    result = _record(dossier, sources)
    assert verify_verdict(
        result,
        ledgers=sources,
        decision_key_one=VERDICT_KEY_ONE,
        decision_key_two="a-different-second-juror!",
        treaty_key_one=TREATY_KEY_ONE,
        treaty_key_two=TREATY_KEY_TWO,
    ) is False


def test_modified_rationale_breaks_terminal_hash(sealed_dossier):
    sources, dossier = sealed_dossier
    result = _record(dossier, sources)
    forged = dict(result)
    forged["rationale"] = "An attacker changed the tribunal reasoning after sealing."
    assert verify_verdict(
        forged,
        ledgers=sources,
        decision_key_one=VERDICT_KEY_ONE,
        decision_key_two=VERDICT_KEY_TWO,
        treaty_key_one=TREATY_KEY_ONE,
        treaty_key_two=TREATY_KEY_TWO,
    ) is False


def test_source_change_voids_the_underlying_treaty_and_verdict(sealed_dossier):
    sources, dossier = sealed_dossier
    result = _record(dossier, sources)
    append_jsonl(sources[0], {"subject_id": "ghost", "tick": 8, "state_hash": "c" * 64})
    assert verify_verdict(
        result,
        ledgers=sources,
        decision_key_one=VERDICT_KEY_ONE,
        decision_key_two=VERDICT_KEY_TWO,
        treaty_key_one=TREATY_KEY_ONE,
        treaty_key_two=TREATY_KEY_TWO,
    ) is False


def test_invalid_dossier_or_rationale_fail_closed(sealed_dossier):
    sources, dossier = sealed_dossier
    forged = dict(dossier)
    forged["verdict"] = "approved_by_attacker"
    with pytest.raises(ValueError, match="invalid, modified, or unsealed"):
        _record(forged, sources)
    with pytest.raises(ValueError, match="rationale"):
        _record(dossier, sources, rationale="too short")


def test_recorded_verdict_survives_ledger_metadata(
    sealed_dossier, tmp_path, monkeypatch
):
    sources, dossier = sealed_dossier
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    result = _record(dossier, sources, record=True)

    stored = json.loads((tmp_path / "reports" / "recovery-verdict.json").read_text())
    assert result["verdict_hash"] == stored["verdict_hash"]
    assert verify_verdict(
        stored,
        ledgers=sources,
        decision_key_one=VERDICT_KEY_ONE,
        decision_key_two=VERDICT_KEY_TWO,
        treaty_key_one=TREATY_KEY_ONE,
        treaty_key_two=TREATY_KEY_TWO,
    ) is True
    assert (tmp_path / "ledgers" / "recovery-verdicts.jsonl").is_file()


def test_cli_record_and_verify_use_environment_keys(
    sealed_dossier, tmp_path, monkeypatch, capsys
):
    sources, dossier = sealed_dossier
    dossier_report = tmp_path / "input-dossier.json"
    dossier_report.write_text(json.dumps(dossier), encoding="utf-8")
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path / "runtime"))
    monkeypatch.setenv("ALEPH_TREATY_KEY_ONE", TREATY_KEY_ONE)
    monkeypatch.setenv("ALEPH_TREATY_KEY_TWO", TREATY_KEY_TWO)
    monkeypatch.setenv("ALEPH_VERDICT_KEY_ONE", VERDICT_KEY_ONE)
    monkeypatch.setenv("ALEPH_VERDICT_KEY_TWO", VERDICT_KEY_TWO)
    args = [str(path) for path in sources]

    assert main([
        "record", "--report", str(dossier_report), "--verdict", "reject",
        "--rationale", "The operation should remain preserved without execution.",
        "--operator-one", "juror-one", "--operator-two", "juror-two", *args,
    ]) == 0
    recorded = json.loads(capsys.readouterr().out)
    assert recorded["verdict"] == "reject"

    verdict_report = tmp_path / "runtime" / "reports" / "recovery-verdict.json"
    assert main(["verify", "--report", str(verdict_report), *args]) == 0
    verified = json.loads(capsys.readouterr().out)
    assert verified["ok"] is True


def test_parser_requires_a_command():
    with pytest.raises(SystemExit):
        build_parser().parse_args([])
