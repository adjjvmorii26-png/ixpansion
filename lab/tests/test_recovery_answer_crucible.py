import hashlib
import json

import pytest

from lab.recovery_answer_crucible import (
    build_parser,
    seal_answers,
    verify_sealed_answers,
)
from lab.recovery_dossier import compile_dossier
from lab.recovery_executor_contract import forge_contract
from lab.recovery_manifest_loom import weave_manifest
from lab.recovery_shadow_red_cell import convene_shadow_cell
from lab.recovery_treaty import compile_treaty
from lab.recovery_verdict import record_verdict
from lab.runtime_vault import append_jsonl


TREATY_KEY_ONE = "first-treaty-out-of-band-key"
TREATY_KEY_TWO = "second-treaty-out-of-band-key"
DECISION_KEY_ONE = "first-juror-out-of-band-key"
DECISION_KEY_TWO = "second-juror-out-of-band-key"
REVIEW_KEY_ONE = "first-reviewer-out-of-band-key"
REVIEW_KEY_TWO = "second-reviewer-out-of-band-key"
LOOM_KEY_ONE = "first-loom-author-out-of-band-key"
LOOM_KEY_TWO = "second-loom-author-out-of-band-key"
CRUCIBLE_KEY_ONE = "first-answer-responder-out-of-band-key"
CRUCIBLE_KEY_TWO = "second-answer-responder-out-of-band-key"
FIXED_CLOCK = lambda: "2026-08-25T06:00:00+00:00"


@pytest.fixture()
def woven_manifest(tmp_path):
    first = tmp_path / "alpha.jsonl"
    second = tmp_path / "beta.jsonl"
    append_jsonl(first, {"subject_id": "ghost", "tick": 7, "state_hash": "a" * 64})
    append_jsonl(second, {"subject_id": "ghost", "tick": 7, "state_hash": "b" * 64})
    sources = [first, second]
    common_upstream = {
        "decision_key_one": DECISION_KEY_ONE,
        "decision_key_two": DECISION_KEY_TWO,
        "contract_key_one": REVIEW_KEY_ONE,
        "contract_key_two": REVIEW_KEY_TWO,
        "treaty_key_one": TREATY_KEY_ONE,
        "treaty_key_two": TREATY_KEY_TWO,
    }
    verdict_upstream = {
        key: value for key, value in common_upstream.items()
        if not key.startswith("contract_")
    }
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
        rationale="The operation is ready for independent human manifest review.",
        operator_one="juror-one",
        operator_two="juror-two",
        ledgers=sources,
        nonce="ab" * 16,
        clock=FIXED_CLOCK,
        record=False,
        **verdict_upstream,
    )
    contract = forge_contract(
        verdict,
        ledgers=sources,
        clock=FIXED_CLOCK,
        nonce="11" * 16,
        record=False,
        **common_upstream,
    )
    shadow = convene_shadow_cell(
        contract,
        ledgers=sources,
        clock=FIXED_CLOCK,
        nonce="22" * 16,
        record=False,
        **common_upstream,
    )
    intents = [{
        "thread_id": "witness-alpha",
        "kind": "preserve",
        "title": "Preserve an offline witness of alpha evidence",
        "rationale": "A human should hold an independent copy before any later implementation review.",
        "bound_ledger": "alpha.jsonl",
    }]
    weave = weave_manifest(
        shadow,
        intents=intents,
        operator_one="author-one",
        operator_two="author-two",
        ledgers=sources,
        loom_key_one=LOOM_KEY_ONE,
        loom_key_two=LOOM_KEY_TWO,
        clock=FIXED_CLOCK,
        nonce="33" * 16,
        record=False,
        **common_upstream,
    )
    return sources, weave


@pytest.fixture()
def answers(woven_manifest):
    sources, _ = woven_manifest
    alpha_digest = hashlib.sha256(sources[0].read_bytes()).hexdigest()
    return [{
        "thread_id": "witness-alpha",
        "bound_ledger": "alpha.jsonl",
        "answers": [
            {
                "lens": "provenance",
                "observed_bytes_sha256": alpha_digest,
                "observation_note": "Both responders independently hashed the bound alpha ledger offline.",
            },
            {
                "lens": "consequence",
                "observable_signal": "A sealed copy exists outside the runtime without altering source bytes.",
                "containment_boundary": "Review remains confined to reading and copying the bound evidence.",
                "side_effect_declaration": "none_observed_during_offline_review",
            },
            {
                "lens": "reversibility",
                "preservation_method": "Store the human-held copy with its digest and review receipt.",
                "human_restorer": "offline-archivist",
                "review_window_days": 30,
            },
        ],
    }]


def _seal(weave, sources, answer_set, **overrides):
    arguments = {
        "answers": answer_set,
        "operator_one": "responder-one",
        "operator_two": "responder-two",
        "ledgers": sources,
        "decision_key_one": DECISION_KEY_ONE,
        "decision_key_two": DECISION_KEY_TWO,
        "treaty_key_one": TREATY_KEY_ONE,
        "treaty_key_two": TREATY_KEY_TWO,
        "contract_key_one": REVIEW_KEY_ONE,
        "contract_key_two": REVIEW_KEY_TWO,
        "loom_key_one": LOOM_KEY_ONE,
        "loom_key_two": LOOM_KEY_TWO,
        "crucible_key_one": CRUCIBLE_KEY_ONE,
        "crucible_key_two": CRUCIBLE_KEY_TWO,
        "clock": FIXED_CLOCK,
        "nonce": "44" * 16,
        "record": False,
    }
    arguments.update(overrides)
    return seal_answers(weave, **arguments)


def _verify(report, sources, **overrides):
    arguments = {
        "ledgers": sources,
        "decision_key_one": DECISION_KEY_ONE,
        "decision_key_two": DECISION_KEY_TWO,
        "treaty_key_one": TREATY_KEY_ONE,
        "treaty_key_two": TREATY_KEY_TWO,
        "contract_key_one": REVIEW_KEY_ONE,
        "contract_key_two": REVIEW_KEY_TWO,
        "loom_key_one": LOOM_KEY_ONE,
        "loom_key_two": LOOM_KEY_TWO,
        "crucible_key_one": CRUCIBLE_KEY_ONE,
        "crucible_key_two": CRUCIBLE_KEY_TWO,
    }
    arguments.update(overrides)
    return verify_sealed_answers(report, **arguments)


def test_all_lens_answers_seal_without_execution_authority(woven_manifest, answers):
    sources, weave = woven_manifest
    result = _seal(weave, sources, answers)

    assert result["status"] == "sealed_for_implementation_review"
    assert result["answer_count"] == 3
    assert result["provenance_digest_matches"] == 1
    assert result["open_questions"] == []
    assert result["authority"]["execution_enabled"] is False
    assert result["authority"]["live_mutation_budget"] == 0
    assert result["authority"]["compatible_executors"] == []
    assert result["authorization"]["signature_count"] == 2
    assert set(result["operators"]).isdisjoint(weave["operators"])
    assert _verify(result, sources) is True


def test_wrong_provenance_digest_is_refused(woven_manifest, answers):
    sources, weave = woven_manifest
    forged = [dict(answers[0])]
    forged[0]["answers"] = list(answers[0]["answers"])
    forged[0]["answers"][0] = dict(forged[0]["answers"][0], observed_bytes_sha256="0" * 64)
    with pytest.raises(ValueError, match="provenance answer does not reproduce"):
        _seal(weave, sources, forged)


def test_answer_operator_cannot_be_a_manifest_author(woven_manifest, answers):
    sources, weave = woven_manifest
    with pytest.raises(ValueError, match="independent of manifest authors"):
        _seal(weave, sources, answers, operator_two="author-one")


def test_invalid_consequence_shape_is_refused(woven_manifest, answers):
    sources, weave = woven_manifest
    forged = [dict(answers[0])]
    forged[0]["answers"] = list(answers[0]["answers"])
    forged[0]["answers"][1] = dict(forged[0]["answers"][1], unexpected_command="execute")
    with pytest.raises(ValueError, match="invalid shape"):
        _seal(weave, sources, forged)


def test_modified_answer_breaks_terminal_hash_and_signature(woven_manifest, answers):
    sources, weave = woven_manifest
    result = _seal(weave, sources, answers)
    forged = dict(result)
    forged["answer_set"] = [dict(result["answer_set"][0])]
    forged["answer_set"][0]["answers"] = [dict(item) for item in result["answer_set"][0]["answers"]]
    forged["answer_set"][0]["answers"][1] = dict(
        forged["answer_set"][0]["answers"][1],
        observable_signal="An attacker changed the consequence observation after sealing.",
    )
    assert _verify(forged, sources) is False


def test_recorded_answers_refuse_exact_replay(woven_manifest, answers, tmp_path, monkeypatch):
    sources, weave = woven_manifest
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    first = _seal(weave, sources, answers, record=True)

    stored = json.loads((tmp_path / "reports" / "recovery-answer-crucible.json").read_text())
    assert stored["crucible_hash"] == first["crucible_hash"]
    assert _verify(stored, sources) is True
    with pytest.raises(ValueError, match="already been recorded"):
        _seal(weave, sources, answers, record=True)
    assert (tmp_path / "ledgers" / "recovery-answer-crucibles.jsonl").is_file()


def test_wrong_second_responder_fails_verification(woven_manifest, answers):
    sources, weave = woven_manifest
    result = _seal(weave, sources, answers)
    assert _verify(result, sources, crucible_key_two="a-different-responder!") is False


def test_parser_requires_a_command():
    with pytest.raises(SystemExit):
        build_parser().parse_args([])
