import json
from pathlib import Path

import pytest

from lab.recovery_atlas import (
    atlas_is_sealed,
    build_parser,
    compile_atlas,
    main,
)
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


def test_coherent_sources_compile_a_dormant_sealed_atlas(tmp_path):
    first = _ledger(tmp_path, "one.jsonl", [{"event_id": "a", "subject_id": "agent", "tick": 1}])
    second = _ledger(tmp_path, "two.jsonl", [{"event_id": "b", "subject_id": "agent", "tick": 2}])
    before = (first.read_bytes(), second.read_bytes())

    result = compile_atlas(ledgers=[first, second], record=False)

    assert result["verdict"] == "dormant"
    assert result["source_audits_ok"] is True
    assert result["execution_enabled"] is False
    assert result["live_mutation_budget"] == 0
    assert set(result["upstream"]) == {"paradox", "dreams", "theater", "quorum"}
    assert "<title>ALEPH Recovery Atlas</title>" in result["html"]
    assert "execution forbidden" in result["html"]
    assert (first.read_bytes(), second.read_bytes()) == before
    assert atlas_is_sealed(result) is True


def test_state_fork_reaches_the_atlas_as_a_consent_packet(tmp_path):
    first = _ledger(tmp_path, "alpha.jsonl", [
        {"subject_id": "ghost", "tick": 7, "state_hash": "a" * 64}
    ])
    second = _ledger(tmp_path, "beta.jsonl", [
        {"subject_id": "ghost", "tick": 7, "state_hash": "b" * 64}
    ])
    result = compile_atlas(ledgers=[first, second], record=False)

    assert result["verdict"] == "consent_ready"
    assert result["journey"]["quorum"]["consent_packet_count"] == 1
    assert "Consent Packets" in result["html"]
    assert "two human signatures required" in result["html"]
    assert result["journey"]["theater"]["scenes"][0]["branches"]


def test_broken_chain_is_rendered_as_tribunal_evidence(tmp_path):
    ledger = _ledger(tmp_path, "broken.jsonl", [{"event_id": "intact"}])
    _tamper_last(ledger)
    result = compile_atlas(ledgers=[ledger], record=False)

    assert result["source_audits_ok"] is False
    assert result["verdict"] == "tribunal_required"
    assert "quarantined" in result["html"]
    assert result["live_mutation_budget"] == 0


def test_recorded_atlas_remains_sealed_after_transport_metadata(tmp_path, monkeypatch):
    ledger = _ledger(tmp_path, "source.jsonl", [{"event_id": "stable"}])
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    result = compile_atlas(ledgers=[ledger], record=True)

    stored = json.loads((tmp_path / "reports" / "recovery-atlas.json").read_text())
    assert atlas_is_sealed(result) is True
    assert atlas_is_sealed(stored) is True
    assert result["ledger_entry_hash"] == stored["ledger_entry_hash"]
    assert (tmp_path / "reports" / "recovery-atlas.html").is_file()
    assert len(list((tmp_path / "ledgers").glob("recovery-atlases.jsonl"))) == 1


def test_explicit_output_writes_without_ledger_side_effects(tmp_path):
    ledger = _ledger(tmp_path, "source.jsonl", [{"event_id": "quiet"}])
    output = tmp_path / "atlas.html"
    result = compile_atlas(ledgers=[ledger], output=output, record=False)

    assert output.read_text() == result["html"]
    assert result["html_output"] == str(output)
    assert not (tmp_path / "reports").exists()
    assert not (tmp_path / "ledgers").exists()


def test_compilation_is_deterministic_for_identical_inputs(tmp_path):
    ledger = _ledger(tmp_path, "same.jsonl", [
        {"event_id": "stable", "subject_id": "agent", "tick": 4}
    ])
    first = compile_atlas(ledgers=[ledger], record=False)
    second = compile_atlas(ledgers=[ledger], record=False)
    assert first == second
    assert first["schema"] == "aleph.chronoforge.recovery-atlas.v1"


def test_cli_stdout_prints_html_without_runtime_artifacts(tmp_path, capsys):
    ledger = _ledger(tmp_path, "cli.jsonl", [{"event_id": "visual"}])
    capsys.readouterr()
    assert main([str(ledger), "--stdout", "--no-ledger"]) == 0

    rendered = capsys.readouterr().out
    assert "<!doctype html>" in rendered
    assert "Recovery Atlas" in rendered
    assert not (tmp_path / "reports").exists()
    assert not (tmp_path / "ledgers").exists()


def test_missing_ledger_fails_closed():
    with pytest.raises(ValueError, match="does not exist"):
        compile_atlas(ledgers=[Path("/tmp/aleph-missing-atlas-ledger.jsonl")], record=False)


def test_limits_and_parser_fail_closed():
    with pytest.raises(ValueError, match="max-operations"):
        compile_atlas(max_operations=33, record=False)
    with pytest.raises(SystemExit):
        build_parser().parse_args(["--unknown"])
