import json
from pathlib import Path

import pytest

from lab.recovery_dossier import (
    _glyph_matrix,
    build_parser,
    compile_dossier,
    dossier_is_sealed,
    main,
)
from lab.recovery_treaty import compile_treaty
from lab.runtime_vault import append_jsonl


KEY_ONE = "first-independent-out-of-band-key"
KEY_TWO = "second-independent-outbound-key"
FIXED_CLOCK = lambda: "2026-08-25T01:00:00+00:00"


@pytest.fixture()
def signed_treaty(tmp_path):
    first = tmp_path / "alpha.jsonl"
    second = tmp_path / "beta.jsonl"
    append_jsonl(first, {"subject_id": "ghost", "tick": 7, "state_hash": "a" * 64})
    append_jsonl(second, {"subject_id": "ghost", "tick": 7, "state_hash": "b" * 64})
    sources = [first, second]
    return sources, compile_treaty(
        ledgers=sources,
        operator_one="archivist",
        operator_two="sentinel",
        key_one=KEY_ONE,
        key_two=KEY_TWO,
        nonce="cd" * 16,
        clock=FIXED_CLOCK,
        record=False,
    )


def test_verified_treaty_becomes_zero_authority_tribunal_dossier(signed_treaty):
    sources, treaty = signed_treaty
    before = tuple(path.read_bytes() for path in sources)
    result = compile_dossier(
        treaty,
        ledgers=sources,
        key_one=KEY_ONE,
        key_two=KEY_TWO,
        clock=FIXED_CLOCK,
        record=False,
    )

    assert result["status"] == "sealed"
    assert result["verdict"] == "ready_for_tribunal"
    assert result["mode"] == "offline-human-handoff"
    assert result["authority"]["execution_enabled"] is False
    assert result["authority"]["compatible_executors"] == []
    assert result["authority"]["live_mutation_budget"] == 0
    assert result["authority"]["next_permitted_action"] == "offline_human_deliberation"
    assert len(result["treaty"]["authorization"]["signatures"]) == 2
    assert "<title>ALEPH Recovery Tribunal Dossier</title>" in result["html"]
    assert "Execution is forbidden." in result["html"]
    assert tuple(path.read_bytes() for path in sources) == before
    assert dossier_is_sealed(result) is True


def test_invalid_or_modified_treaty_cannot_compile(signed_treaty):
    sources, treaty = signed_treaty
    forged = dict(treaty)
    forged["operators"] = ["attacker-one", "attacker-two"]
    with pytest.raises(ValueError, match="invalid, modified, expired"):
        compile_dossier(
            forged,
            ledgers=sources,
            key_one=KEY_ONE,
            key_two=KEY_TWO,
            record=False,
        )


def test_dossier_compilation_is_deterministic(signed_treaty):
    sources, treaty = signed_treaty
    first = compile_dossier(
        treaty,
        ledgers=sources,
        key_one=KEY_ONE,
        key_two=KEY_TWO,
        clock=FIXED_CLOCK,
        record=False,
    )
    second = compile_dossier(
        treaty,
        ledgers=sources,
        key_one=KEY_ONE,
        key_two=KEY_TWO,
        clock=FIXED_CLOCK,
        record=False,
    )
    assert first == second
    assert first["schema"] == "aleph.chronoforge.recovery-dossier.v1"


def test_source_change_after_signing_prevents_dossier_compilation(signed_treaty):
    sources, treaty = signed_treaty
    append_jsonl(sources[0], {"subject_id": "ghost", "tick": 8, "state_hash": "c" * 64})
    with pytest.raises(ValueError, match="invalid, modified, expired"):
        compile_dossier(
            treaty,
            ledgers=sources,
            key_one=KEY_ONE,
            key_two=KEY_TWO,
            record=False,
        )


def test_witness_glyph_is_exactly_sixteen_square_and_stable():
    matrix = _glyph_matrix("fixed-dossier-seed")
    assert len(matrix) == 16
    assert all(len(row) == 16 for row in matrix)
    assert all(value in (True, False) for row in matrix for value in row)
    assert matrix == _glyph_matrix("fixed-dossier-seed")
    assert matrix != _glyph_matrix("different-dossier-seed")


def test_recorded_dossier_remains_sealed_after_transport_metadata(
    signed_treaty, tmp_path, monkeypatch
):
    sources, treaty = signed_treaty
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    result = compile_dossier(
        treaty,
        ledgers=sources,
        key_one=KEY_ONE,
        key_two=KEY_TWO,
        clock=FIXED_CLOCK,
        record=True,
    )

    stored = json.loads((tmp_path / "reports" / "recovery-dossier.json").read_text())
    assert dossier_is_sealed(result) is True
    assert dossier_is_sealed(stored) is True
    assert result["ledger_entry_hash"] == stored["ledger_entry_hash"]
    assert (tmp_path / "reports" / "recovery-dossier.html").is_file()
    assert (tmp_path / "ledgers" / "recovery-dossiers.jsonl").is_file()


def test_explicit_output_writes_without_ledger_side_effects(signed_treaty, tmp_path):
    sources, treaty = signed_treaty
    output = tmp_path / "dossier.html"
    result = compile_dossier(
        treaty,
        ledgers=sources,
        key_one=KEY_ONE,
        key_two=KEY_TWO,
        output=output,
        record=False,
    )

    assert output.read_text() == result["html"]
    assert result["html_output"] == str(output)
    assert not (tmp_path / "reports").exists()
    assert not (tmp_path / "ledgers").exists()


def test_tampered_dossier_fails_terminal_hash(signed_treaty):
    sources, treaty = signed_treaty
    result = compile_dossier(
        treaty,
        ledgers=sources,
        key_one=KEY_ONE,
        key_two=KEY_TWO,
        record=False,
    )
    forged = dict(result)
    forged["verdict"] = "approved_for_execution"
    assert dossier_is_sealed(forged) is False


def test_cli_compile_and_verify_use_environment_keys(
    signed_treaty, tmp_path, monkeypatch, capsys
):
    sources, treaty = signed_treaty
    treaty_report = tmp_path / "input-treaty.json"
    treaty_report.write_text(json.dumps(treaty), encoding="utf-8")
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path / "runtime"))
    monkeypatch.setenv("ALEPH_TREATY_KEY_ONE", KEY_ONE)
    monkeypatch.setenv("ALEPH_TREATY_KEY_TWO", KEY_TWO)
    source_args = [str(path) for path in sources]

    assert main([
        "compile", "--report", str(treaty_report), *source_args
    ]) == 0
    compiled = json.loads(capsys.readouterr().out)
    assert compiled["authority"]["execution_enabled"] is False

    dossier_report = tmp_path / "runtime" / "reports" / "recovery-dossier.json"
    assert main(["verify", "--report", str(dossier_report)]) == 0
    verified = json.loads(capsys.readouterr().out)
    assert verified["ok"] is True


def test_parser_requires_a_command():
    with pytest.raises(SystemExit):
        build_parser().parse_args([])
