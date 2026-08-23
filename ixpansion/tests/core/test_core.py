import json

import pytest

from core.config_loader import load_config
from core.events import EventBus
from core.registry import Registry
from core.state_graph import StateGraph


def test_event_bus_routes_and_records():
    bus = EventBus()
    seen = []
    bus.subscribe("tick", seen.append)
    assert bus.publish("tick", {"n": 1}) == 1
    assert seen == [{"n": 1}]
    assert bus.tail(1)[0]["payload"]["n"] == 1


def test_state_graph_tracks_growth_and_fingerprint():
    graph = StateGraph()
    graph.add_node("origin", stability=1)
    graph.add_node("alpha")
    graph.connect("origin", "alpha", "growth")
    before = graph.fingerprint()
    graph.nodes["alpha"].state["energy"] = 2
    assert graph.neighbors("origin") == ["alpha"]
    assert before != graph.fingerprint()


def test_registry_prevents_collision_and_creates_items():
    registry = Registry()
    registry.register("factory", lambda value=1: {"value": value})
    assert registry.names() == ["factory"]
    assert registry.create("factory", value=3)["value"] == 3
    with pytest.raises(KeyError):
        registry.register("factory", lambda: {})


def test_load_config_supports_json_and_simple_yaml(tmp_path):
    json_path = tmp_path / "a.json"
    json_path.write_text(json.dumps({"ticks": 4}), encoding="utf-8")
    yaml_path = tmp_path / "b.yaml"
    yaml_path.write_text("# profile\nname: hex\nticks: 7\nflags: [one, two]\n", encoding="utf-8")
    assert load_config(json_path)["ticks"] == 4
    loaded = load_config(yaml_path)
    assert loaded["name"] == "hex"
    assert loaded["flags"] == ["one", "two"]
