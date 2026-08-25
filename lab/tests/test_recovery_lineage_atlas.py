import json
from pathlib import Path

import pytest

from lab.recovery_lineage_atlas import (
    atlas_is_sealed,
    build_parser,
    compile_lineage_atlas,
    main,
)


FIXED_CLOCK = lambda: "2026-08-25T04:30:00+00:00"


def test_empty_runtime_produces_all_missing_sealed_atlas(tmp_path):
    result = compile_lineage_atlas(runtime_root=tmp_path, record=False, clock=FIXED_CLOCK)

    assert result["schema"] == "aleph.chronoforge.recovery-lineage-atlas.v1"
    assert result["present_stages"] == 0
    assert result["stage_count"] == 8
    assert all(s["status"] == "missing" for s in result["stages"])
    assert result["execution_enabled"] is False
    assert "<title>ALEPH Recovery Lineage Atlas</title>" in result["html"]
    assert atlas_is_sealed(result) is True


def test_present_stages_appear_in_constellation(tmp_path):
    (tmp_path / "reports").mkdir(parents=True, exist_ok=True)
    (tmp_path / "reports" / "recovery-treaty.json").write_text(json.dumps({"treaty_hash": "a" * 64}))
    (tmp_path / "reports" / "recovery-verdict.json").write_text(json.dumps({"verdict_hash": "b" * 64}))
    result = compile_lineage_atlas(runtime_root=tmp_path, record=False, clock=FIXED_CLOCK)

    assert result["present_stages"] == 2
    statuses = {s["stage"]: s["status"] for s in result["stages"]}
    assert statuses["treaty"] == "present"
    assert statuses["verdict"] == "present"
    assert statuses["crucible"] == "missing"


def test_atlas_is_deterministic(tmp_path):
    first = compile_lineage_atlas(runtime_root=tmp_path, record=False, clock=FIXED_CLOCK)
    second = compile_lineage_atlas(runtime_root=tmp_path, record=False, clock=FIXED_CLOCK)
    assert first == second


def test_recorded_atlas_persists_and_verifies(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    result = compile_lineage_atlas(runtime_root=tmp_path, record=True, clock=FIXED_CLOCK)
    stored = json.loads((tmp_path / "reports" / "recovery-lineage-atlas.json").read_text())
    assert stored["atlas_hash"] == result["atlas_hash"]
    assert atlas_is_sealed(stored) is True
    assert result["ledger_entry_hash"] == stored["ledger_entry_hash"]


def test_explicit_output_writes_html(tmp_path):
    output = tmp_path / "lineage.html"
    result = compile_lineage_atlas(runtime_root=tmp_path, record=False, output=output, clock=FIXED_CLOCK)
    assert output.read_text() == result["html"]
    assert result["html_output"] == str(output)


def test_cli_stdout_emits_html(tmp_path, capsys):
    capsys.readouterr()
    assert main(["--runtime-root", str(tmp_path), "--stdout", "--no-ledger"]) == 0
    rendered = capsys.readouterr().out
    assert "<!doctype html>" in rendered


def test_cli_default_emits_json(tmp_path, capsys):
    capsys.readouterr()
    assert main(["--runtime-root", str(tmp_path), "--no-ledger"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema"] == "aleph.chronoforge.recovery-lineage-atlas.v1"


def test_parser_flags():
    args = build_parser().parse_args(["--no-ledger"])
    assert args.no_ledger is True
