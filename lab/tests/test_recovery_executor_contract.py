import json

import pytest

from lab.recovery_dossier import compile_dossier
from lab.recovery_executor_contract import (
    build_parser,
    forge_contract,
    verify_contract,
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
FIXED_CLOCK = lambda: "2026-08-25T03:00:00+00:00"


@pytest.fixture()
def approved_verdict(tmp_path):
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
        rationale="The bound recovery operation is ready for separate human review.",
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
    return sources, verdict


def _forge(verdict, sources, **overrides):
    arguments = {
        "ledgers": sources,
        "decision_key_one": DECISION_KEY_ONE,
        "decision_key_two": DECISION_KEY_TWO,
        "treaty_key_one": TREATY_KEY_ONE,
        "treaty_key_two": TREATY_KEY_TWO,
        "contract_key_one": REVIEW_KEY_ONE,
        "contract_key_two": REVIEW_KEY_TWO,
        "clock": FIXED_CLOCK,
        "nonce": "11" * 16,
        "record": False,
    }
    arguments.update(overrides)
    return forge_contract(verdict, **arguments)


def _verify(contract, sources, **overrides):
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
    return verify_contract(contract, **arguments)


def test_approved_verdict_becomes_completely_inert_review_draft(approved_verdict):
    sources, verdict = approved_verdict
    contract = _forge(verdict, sources)

    proposal = contract["proposal"]
    assert contract["status"] == "drafted_for_separate_human_review"
    assert contract["mode"] == "zero-authority-handoff"
    assert proposal["lineage_parameters"] == {"max_operations": 5}
    assert contract["authorization"]["execution_enabled"] is False
    assert contract["authorization"]["live_mutation_budget"] == 0
    assert contract["authorization"]["compatible_executors"] == []
    assert "execute_commands" in proposal["prohibited_capabilities"]
    assert len(contract["authorization"]["signatures"]) == 2
    assert _verify(contract, sources) is True


def test_rejected_or_deferred_verdicts_cannot_be_forged(tmp_path):
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
    verdict = record_verdict(
        dossier,
        verdict="reject",
        rationale="The operation should remain archived without execution.",
        operator_one="juror-one",
        operator_two="juror-two",
        ledgers=sources,
        decision_key_one=DECISION_KEY_ONE,
        decision_key_two=DECISION_KEY_TWO,
        treaty_key_one=TREATY_KEY_ONE,
        treaty_key_two=TREATY_KEY_TWO,
        clock=FIXED_CLOCK,
        record=False,
    )

    with pytest.raises(ValueError, match="only an approved verdict"):
        _forge(verdict, sources)


def test_modified_proposal_breaks_terminal_seal(approved_verdict):
    sources, verdict = approved_verdict
    contract = _forge(verdict, sources)
    forged = dict(contract)
    forged["proposal"] = dict(contract["proposal"])
    forged["proposal"]["candidate_capabilities"] = ["execute_commands"]
    assert _verify(forged, sources) is False


def test_wrong_second_reviewer_fails_verification(approved_verdict):
    sources, verdict = approved_verdict
    contract = _forge(verdict, sources)
    assert _verify(contract, sources, contract_key_two="a-different-reviewer-key!") is False


def test_recorded_contract_survives_ledger_metadata(
    approved_verdict, tmp_path, monkeypatch
):
    sources, verdict = approved_verdict
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    contract = _forge(verdict, sources, record=True)

    stored_path = tmp_path / "reports" / "recovery-executor-contract.json"
    stored = json.loads(stored_path.read_text())
    assert stored["contract_hash"] == contract["contract_hash"]
    assert _verify(stored, sources) is True
    assert (tmp_path / "ledgers" / "recovery-executor-contracts.jsonl").is_file()


def test_parser_requires_a_command():
    with pytest.raises(SystemExit):
        build_parser().parse_args([])
