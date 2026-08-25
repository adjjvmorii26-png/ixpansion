import json

import pytest

from lab.recovery_dossier import compile_dossier
from lab.recovery_executor_contract import forge_contract
from lab.recovery_shadow_red_cell import (
    build_parser,
    convene_shadow_cell,
    verify_shadow_cell,
)
from lab.recovery_treaty import compile_treaty
from lab.recovery_verdict import record_verdict
from lab.runtime_vault import append_jsonl


TREATY_KEY_ONE = "first-treaty-out-of-band-key"
TREATY_KEY_TWO = "second-treaty-out-of-band-key"
DECISION_KEY_ONE = "first-juror-out-of-band-key"
DECISION_KEY_TWO = "second-juror-out-of-band-key"
REVIEW_KEY_ONE = "first-reviewer-out-of-band-key"
REVIEW_KEY_TWO = "second-reviewer-out-of-band-key"
FIXED_CLOCK = lambda: "2026-08-25T04:00:00+00:00"


@pytest.fixture()
def approved_contract(tmp_path):
    first = tmp_path / "alpha.jsonl"
    second = tmp_path / "beta.jsonl"
    append_jsonl(first, {"subject_id": "ghost", "tick": 7, "state_hash": "a" * 64})
    append_jsonl(second, {"subject_id": "ghost", "tick": 7, "state_hash": "b" * 64})
    sources = [first, second]
    treaty = compile_treaty(
        ledgers=sources,
        operator_one="archivist",
        operator_two="sentinel",
        max_operations=5,
        key_one=TREATY_KEY_ONE,
        key_two=TREATY_KEY_TWO,
        nonce="cd" * 16,
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
    verdict = record_verdict(
        dossier,
        verdict="approve",
        rationale="The bound operation is ready for independent human review.",
        operator_one="juror-one",
        operator_two="juror-two",
        ledgers=sources,
        decision_key_one=DECISION_KEY_ONE,
        decision_key_two=DECISION_KEY_TWO,
        treaty_key_one=TREATY_KEY_ONE,
        treaty_key_two=TREATY_KEY_TWO,
        nonce="ab" * 16,
        clock=FIXED_CLOCK,
        record=False,
    )
    contract = forge_contract(
        verdict,
        ledgers=sources,
        decision_key_one=DECISION_KEY_ONE,
        decision_key_two=DECISION_KEY_TWO,
        treaty_key_one=TREATY_KEY_ONE,
        treaty_key_two=TREATY_KEY_TWO,
        contract_key_one=REVIEW_KEY_ONE,
        contract_key_two=REVIEW_KEY_TWO,
        clock=FIXED_CLOCK,
        nonce="11" * 16,
        record=False,
    )
    return sources, contract


def _convene(contract, sources, **overrides):
    arguments = {
        "ledgers": sources,
        "decision_key_one": DECISION_KEY_ONE,
        "decision_key_two": DECISION_KEY_TWO,
        "treaty_key_one": TREATY_KEY_ONE,
        "treaty_key_two": TREATY_KEY_TWO,
        "contract_key_one": REVIEW_KEY_ONE,
        "contract_key_two": REVIEW_KEY_TWO,
        "clock": FIXED_CLOCK,
        "nonce": "22" * 16,
        "record": False,
    }
    arguments.update(overrides)
    return convene_shadow_cell(contract, **arguments)


def _verify(report, sources, **overrides):
    arguments = {
        "ledgers": sources,
        "decision_key_one": DECISION_KEY_ONE,
        "decision_key_two": DECISION_KEY_TWO,
        "treaty_key_one": TREATY_KEY_ONE,
        "treaty_key_two": TREATY_KEY_TWO,
        "contract_key_one": REVIEW_KEY_ONE,
        "contract_key_two": REVIEW_KEY_TWO,
    }
    arguments.update(overrides)
    return verify_shadow_cell(report, **arguments)


def test_seven_synthetic_adversaries_remain_completely_inert(approved_contract):
    sources, contract = approved_contract
    result = _convene(contract, sources)

    assert result["status"] == "shadow_review_complete"
    assert result["mode"] == "zero-authority-adversarial-review"
    assert result["attack_count"] == 7
    assert result["contained_attack_count"] == 7
    assert result["open_findings"] == []
    assert result["risk_index"] == 0.0
    assert result["authority"]["execution_enabled"] is False
    assert result["authority"]["live_mutation_budget"] == 0
    assert result["authority"]["compatible_executors"] == []
    assert result["review_signature"]["human_authorization_granted"] is False
    assert {item["verdict"] for item in result["attacks"]} == {"contained"}
    assert _verify(result, sources) is True


def test_unapproved_or_invalid_contracts_are_refused(approved_contract):
    sources, contract = approved_contract
    forged = dict(contract)
    forged["authorization"] = dict(contract["authorization"])
    forged["authorization"]["compatible_executors"] = ["ghost-executor"]
    with pytest.raises(ValueError, match="invalid or its witnesses changed"):
        _convene(forged, sources)


def test_modified_attack_battery_breaks_terminal_seal(approved_contract):
    sources, contract = approved_contract
    result = _convene(contract, sources)
    forged = dict(result)
    forged["attacks"] = [dict(item) for item in result["attacks"]]
    forged["attacks"][0]["verdict"] = "escaped"
    assert _verify(forged, sources) is False


def test_source_byte_change_voids_underlying_contract_and_review(approved_contract):
    sources, contract = approved_contract
    result = _convene(contract, sources)
    append_jsonl(sources[0], {"subject_id": "ghost", "tick": 8, "state_hash": "c" * 64})
    with pytest.raises(ValueError, match="invalid or its witnesses changed"):
        _convene(contract, sources)
    assert _verify(result, sources) is False


def test_recorded_shadow_reviews_refuse_replay_of_same_contract(
    approved_contract, tmp_path, monkeypatch
):
    sources, contract = approved_contract
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    first = _convene(contract, sources, record=True)

    stored_path = tmp_path / "reports" / "recovery-shadow-red-cell.json"
    stored = json.loads(stored_path.read_text())
    assert stored["red_cell_hash"] == first["red_cell_hash"]
    assert _verify(stored, sources) is True
    with pytest.raises(ValueError, match="already undergone"):
        _convene(contract, sources, record=True)
    assert (tmp_path / "ledgers" / "recovery-shadow-red-cells.jsonl").is_file()


def test_unrecorded_review_is_deterministic(approved_contract):
    sources, contract = approved_contract
    assert _convene(contract, sources) == _convene(contract, sources)


def test_wrong_contract_key_fails_closed(approved_contract):
    sources, contract = approved_contract
    result = _convene(contract, sources)
    assert _verify(result, sources, contract_key_two="a-different-reviewer!") is False


def test_parser_requires_a_command():
    with pytest.raises(SystemExit):
        build_parser().parse_args([])
