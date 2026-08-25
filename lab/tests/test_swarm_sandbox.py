import hashlib
import json

import pytest

from lab.experiments import swarm
from lab.experiments.astral_socket import send, tail
from lab.runtime_vault import read_jsonl
from sandbox import sandbox_engine


@pytest.fixture()
def isolated_sandbox(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    sandbox_engine.STATE = tmp_path / "sandbox" / "engine.json"
    return tmp_path


def _hash(result):
    material = {key: value for key, value in result.items() if key != "pulse_hash"}
    return hashlib.sha256(json.dumps(material, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def test_swarm_observes_two_ticks_with_three_inert_agents(isolated_sandbox):
    result = swarm.swarm_sandbox_ticks(
        sandbox_ticks=2,
        agent_count=3,
        bus=False,
        proof=False,
        clock=lambda: "2026-08-25T07:00:00+00:00",
    )

    assert result["status"] == "sealed"
    assert result["mode"] == "data-only-swarm-observations"
    assert result["sandbox_ticks_before"] == 0
    assert result["sandbox_ticks_after"] == 2
    assert len(result["observations"]) == 6
    assert {item["species"] for item in result["observations"]} == set(swarm.SPECIES)
    assert all(item["mutation_enabled"] is False for item in result["observations"])
    assert all(item["permitted_effect"] == "record_observation" for item in result["observations"])
    assert result["authority"]["execution_enabled"] is False
    assert result["consensus"]["dominant"] in {"preserve", "inspect", "drift"}
    assert result["pulse_hash"] == _hash(result)


def test_swarm_persists_one_cycle_per_run(isolated_sandbox):
    first = swarm.swarm_sandbox_ticks(
        sandbox_ticks=1,
        agent_count=2,
        bus=False,
        proof=False,
        clock=lambda: "2026-08-25T07:01:00+00:00",
    )
    second = swarm.swarm_sandbox_ticks(
        sandbox_ticks=1,
        agent_count=2,
        bus=False,
        proof=False,
        clock=lambda: "2026-08-25T07:02:00+00:00",
    )
    state = json.loads((isolated_sandbox / "state" / "swarm" / "pulse.json").read_text())

    assert first["cycle_id"] != second["cycle_id"]
    assert state["latest_cycle_id"] == second["cycle_id"]
    assert len(state["cycles"]) == 2
    assert state["cycles"][-1]["sandbox_ticks_after"] == 2


def test_swarm_routes_to_runtime_astral_bus_and_proof_ledger(isolated_sandbox):
    result = swarm.swarm_sandbox_ticks(
        sandbox_ticks=1,
        agent_count=3,
        clock=lambda: "2026-08-25T07:03:00+00:00",
    )
    channel = isolated_sandbox / "state" / "swarm" / "astral_channel.jsonl"
    ledger = isolated_sandbox / "ledgers" / "proof.jsonl"

    assert result["bus_topic"] == "swarm_sandbox_pulse"
    assert channel.is_file()
    event = json.loads(channel.read_text().splitlines()[-1])
    assert event["payload"]["cycle_id"] == result["cycle_id"]
    assert event["payload"]["execution_enabled"] is False
    assert ledger.is_file()
    proof = read_jsonl(ledger)[-1]
    assert proof["type"] == "swarm_sandbox_cycle"
    assert proof["ref"] == result["cycle_id"]


def test_no_bus_omits_transport_metadata(isolated_sandbox):
    result = swarm.swarm_sandbox_ticks(
        sandbox_ticks=1,
        agent_count=1,
        bus=False,
        proof=False,
        clock=lambda: "2026-08-25T07:04:00+00:00",
    )
    assert "bus_topic" not in result
    assert not (isolated_sandbox / "state" / "swarm" / "astral_channel.jsonl").exists()


@pytest.mark.parametrize("ticks,agents", [(0, 3), (33, 3), (1, 0), (1, 13)])
def test_invalid_tick_or_agent_bounds_fail_closed(isolated_sandbox, ticks, agents):
    with pytest.raises(ValueError):
        swarm.swarm_sandbox_ticks(sandbox_ticks=ticks, agent_count=agents, bus=False, proof=False)


def test_cli_status_reports_latest_cycle(isolated_sandbox, capsys):
    created = swarm.swarm_sandbox_ticks(
        sandbox_ticks=1,
        agent_count=4,
        bus=False,
        proof=False,
        clock=lambda: "2026-08-25T07:05:00+00:00",
    )
    capsys.readouterr()
    assert swarm.main(["--status"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ready"
    assert payload["latest_cycle_id"] == created["cycle_id"]
    assert payload["cycles"] == 1


def test_astral_send_accepts_explicit_path(tmp_path):
    path = tmp_path / "custom" / "channel.jsonl"
    record = send("test-topic", {"value": 7}, path=path)
    assert tail(1, path=path) == [record]
    assert record["payload"] == {"value": 7}


def test_parser_exposes_requested_flag():
    args = swarm.build_parser().parse_args(["--sandbox-ticks", "5"])
    assert args.sandbox_ticks == 5
