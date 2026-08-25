import json

import pytest

from lab.astral_network_weaver import (
    build_parser,
    discover_peers,
    register_module,
    weave_network,
)


FIXED_CLOCK = lambda: "2026-08-25T05:00:00+00:00"


def test_register_and_discover_by_capability(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    register_module("sentinel", capabilities=["observe", "protect"], clock=FIXED_CLOCK)
    register_module("archivist", capabilities=["observe", "archive"], clock=FIXED_CLOCK)
    peers = discover_peers(providing="archive")
    assert len(peers) == 1
    assert peers[0]["name"] == "archivist"


def test_discover_by_consumer(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    register_module("swarm", capabilities=["pulse"], consumes=["sandbox_state"], clock=FIXED_CLOCK)
    peers = discover_peers(consuming="sandbox_state")
    assert len(peers) == 1
    assert peers[0]["name"] == "swarm"


def test_weave_network_seals_topology(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    register_module("a", capabilities=["x", "y"], consumes=["z"], clock=FIXED_CLOCK)
    register_module("b", capabilities=["z"], clock=FIXED_CLOCK)
    result = weave_network(clock=FIXED_CLOCK)
    assert result["module_count"] == 2
    assert result["unique_capabilities"] == 3
    assert result["execution_enabled"] is False
    a_top = next(t for t in result["topology"] if t["module"] == "a")
    assert "b" in a_top["peer_names"]
    material = {k: v for k, v in result.items() if k != "weave_hash"}
    assert result["weave_hash"] == __import__("hashlib").sha256(
        json.dumps(material, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def test_duplicate_registration_overwrites(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    register_module("x", capabilities=["old"], clock=FIXED_CLOCK)
    register_module("x", capabilities=["new"], clock=FIXED_CLOCK)
    result = weave_network(clock=FIXED_CLOCK)
    assert result["modules"][0]["capabilities"] == ["new"]


def test_parser_exposes_commands():
    args = build_parser().parse_args(["register", "m", "--capabilities", "cap1"])
    assert args.command == "register"
    assert args.capabilities == ["cap1"]
