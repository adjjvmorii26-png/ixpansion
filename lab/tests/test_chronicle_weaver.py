import hashlib
import json
from pathlib import Path

import pytest

from lab.chronicle_weaver import weave_chronicle, build_parser, main
from lab.runtime_vault import append_jsonl, ledger_path


def _hash(result):
    material = {k: v for k, v in result.items() if k not in {"weave_hash", "html", "audit"}}
    return hashlib.sha256(json.dumps(material, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def test_empty_ledger_produces_sealed_chronicle(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    result = weave_chronicle(record=False, clock=lambda: "2026-08-25T07:00:00+00:00")
    assert result["schema"] == "aleph.experiments.chronicle-weaver.v1"
    assert result["total_entries"] == 0
    assert result["execution_enabled"] is False
    assert "<title>Chronicle</title>" in result["html"]
    assert result["weave_hash"] == _hash(result)


def test_entries_grouped_by_type(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    ledger = ledger_path("proof.jsonl")
    append_jsonl(ledger, {"ts": "2026-01-01T00:00:00+00:00", "type": "sandbox_ticks", "ref": "r1"})
    append_jsonl(ledger, {"ts": "2026-01-02T00:00:00+00:00", "type": "swarm_sandbox_cycle", "ref": "r2"})
    append_jsonl(ledger, {"ts": "2026-01-03T00:00:00+00:00", "type": "sandbox_ticks", "ref": "r3"})
    result = weave_chronicle(record=False, clock=lambda: "2026-08-25T07:01:00+00:00")
    assert result["total_entries"] == 3
    assert result["type_summary"]["sandbox_ticks"] == 2
    assert result["type_summary"]["swarm_sandbox_cycle"] == 1
    assert len(result["timeline"]) == 3


def test_deterministic_output(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    clock = lambda: "2026-08-25T07:02:00+00:00"
    assert weave_chronicle(record=False, clock=clock) == weave_chronicle(record=False, clock=clock)


def test_output_writes_html(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    output = tmp_path / "chronicle.html"
    result = weave_chronicle(record=False, output=output)
    assert output.read_text() == result["html"]


def test_cli_default_emits_html(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    capsys.readouterr()
    assert main(["--no-ledger"]) == 0
    assert "<!doctype html>" in capsys.readouterr().out


def test_parser_flags():
    args = build_parser().parse_args(["--ledger", "custom.jsonl", "--no-ledger"])
    assert args.ledger == "custom.jsonl"
