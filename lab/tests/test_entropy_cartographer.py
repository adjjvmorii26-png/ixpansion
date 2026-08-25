import hashlib
import json

import pytest

from lab.entropy_cartographer import cartograph, build_parser, main
from sandbox import sandbox_engine


@pytest.fixture()
def isolated(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    sandbox_engine.STATE = tmp_path / "sandbox" / "engine.json"
    return tmp_path


def _hash(result):
    material = {k: v for k, v in result.items() if k not in {"cartograph_hash", "html"}}
    return hashlib.sha256(json.dumps(material, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def test_cartograph_seals_heatmap(isolated):
    result = cartograph(ticks=5, record=False, clock=lambda: "2026-08-25T06:00:00+00:00")
    assert result["tick_count"] == 5
    assert len(result["cells"]) == 5
    assert result["execution_enabled"] is False
    assert "<title>Entropy Cartograph</title>" in result["html"]
    assert result["cartograph_hash"] == _hash(result)


def test_recorded_cartograph_persists(isolated):
    result = cartograph(ticks=3, record=True, clock=lambda: "2026-08-25T06:01:00+00:00")
    latest = json.loads((isolated / "state" / "cartographer" / "latest.json").read_text())
    assert latest["cartograph_hash"] == result["cartograph_hash"]


@pytest.mark.parametrize("ticks", [0, 201])
def test_bounds_fail(isolated, ticks):
    with pytest.raises(ValueError):
        cartograph(ticks=ticks, record=False)


def test_cli_emits_html(isolated, capsys):
    capsys.readouterr()
    assert main(["--ticks", "2", "--no-ledger"]) == 0
    html = capsys.readouterr().out
    assert "<!doctype html>" in html


def test_parser_flags():
    args = build_parser().parse_args(["--ticks", "5", "--no-ledger"])
    assert args.ticks == 5
