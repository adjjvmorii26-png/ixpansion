import json

import pytest

from lab.recovery_dossier import compile_dossier
from lab.recovery_executor_contract import forge_contract
from lab.recovery_manifest_loom import build_parser, weave_manifest, verify_weave
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
FIXED_CLOCK = lambda: "2026-08-25T05:00:00+00:00"


@pytest.fixture()
def shadow_review(tmp_path):
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
        rationale="The operation is ready for independent human manifest review.",
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
    shadow = convene_shadow_cell(
        contract,
        ledgers=sources,
        decision_key_one=DECISION_KEY_ONE,
        decision_key_two=DECISION_KEY_TWO,
        treaty_key_one=TREATY_KEY_ONE,
        treaty_key_two=TREATY_KEY_TWO,
        contract_key_one=REVIEW_KEY_ONE,
        contract_key_two=REVIEW_KEY_TWO,
        clock=FIXED_CLOCK,
        nonce="22" * 16,
        record=False,
    )
    return sources, shadow


@pytest.fixture()
def intents():
    return [{
        "thread_id": "witness-alpha",
        "kind": "preserve",
        "title": "Preserve an offline witness of alpha evidence",
        "rationale": "A human should hold an independent copy before any later implementation review.",
        "bound_ledger": "alpha.jsonl",
    }]


def _weave(shadow, sources, threads, **overrides):
    arguments = {
        "intents": threads,
        "operator_one": "author-one",
        "operator_two": "author-two",
        "ledgers": sources,
        "decision_key_one": DECISION_KEY_ONE,
        "decision_key_two": DECISION_KEY_TWO,
        "treaty_key_one": TREATY_KEY_ONE,
        "treaty_key_two": TREATY_KEY_TWO,
        "contract_key_one": REVIEW_KEY_ONE,
        "contract_key_two": REVIEW_KEY_TWO,
        "loom_key_one": LOOM_KEY_ONE,
        "loom_key_two": LOOM_KEY_TWO,
        "clock": FIXED_CLOCK,
        "nonce": "33" * 16,
        "record": False,
    }
    arguments.update(overrides)
    return weave_manifest(shadow, **arguments)


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
    }
    arguments.update(overrides)
    return verify_weave(report, **arguments)


def test_human_intents_are_woven_without_execution_authority(shadow_review, intents):
    sources, shadow = shadow_review
    result = _weave(shadow, sources, intents)

    assert result["status"] == "sealed_for_human_manifest_review"
    assert result["mode"] == "zero-authority-intent-weaving"
    assert result["threads"][0]["mutation_enabled"] is False
    assert len(result["threads"][0]["review_lenses"]) == 3
    assert all(
        lens["status"] == "awaiting_independent_human_answer"
        for lens in result["threads"][0]["review_lenses"]
    )
    assert result["authority"]["execution_enabled"] is False
    assert result["authority"]["live_mutation_budget"] == 0
    assert result["authority"]["compatible_executors"] == []
    assert result["authorization"]["signature_count"] == 2
    assert _verify(result, sources) is True


def test_forbidden_intent_kind_is_refused(shadow_review, intents):
    sources, shadow = shadow_review
    forged = [dict(intents[0], thread_id="mutate-alpha", kind="execute")]
    with pytest.raises(ValueError, match="unsupported intent kind"):
        _weave(shadow, sources, forged)


def test_unbound_target_is_refused(shadow_review, intents):
    sources, shadow = shadow_review
    forged = [dict(intents[0], bound_ledger="unreviewed.jsonl")]
    with pytest.raises(ValueError, match="must bind one reviewed ledger"):
        _weave(shadow, sources, forged)


def test_modified_lens_breaks_terminal_hash_and_signature(shadow_review, intents):
    sources, shadow = shadow_review
    result = _weave(shadow, sources, intents)
    forged = dict(result)
    forged["threads"] = [dict(result["threads"][0])]
    forged["threads"][0]["review_lenses"] = list(result["threads"][0]["review_lenses"])
    forged["threads"][0]["review_lenses"][0] = dict(
        forged["threads"][0]["review_lenses"][0],
        status="answered_by_automation",
    )
    assert _verify(forged, sources) is False


def test_recorded_manifest_refuses_exact_replay(
    shadow_review, intents, tmp_path, monkeypatch
):
    sources, shadow = shadow_review
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    first = _weave(shadow, sources, intents, record=True)

    stored = json.loads(
        (tmp_path / "reports" / "recovery-manifest-loom.json").read_text()
    )
    assert stored["loom_hash"] == first["loom_hash"]
    assert _verify(stored, sources) is True
    with pytest.raises(ValueError, match="already been recorded"):
        _weave(shadow, sources, intents, record=True)
    assert (tmp_path / "ledgers" / "recovery-manifest-looms.jsonl").is_file()


def test_wrong_second_author_fails_verification(shadow_review, intents):
    sources, shadow = shadow_review
    result = _weave(shadow, sources, intents)
    assert _verify(result, sources, loom_key_two="a-different-author-key!") is False


def test_parser_requires_a_command():
    with pytest.raises(SystemExit):
        build_parser().parse_args([])
