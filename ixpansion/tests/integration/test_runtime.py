import pytest

from core.runtime import IxpansionRuntime
from dashboard.layout import render_dashboard
from interfaces.api import run_scene
from tools.inspectors.structure_inspector import inspect
from tools.inspectors.mutation_inspector import summarize


@pytest.mark.parametrize("scene,topology", [
    ("hex_storm", "star"),
    ("mesh_fracture", "ring"),
    ("overgrowth_field", "chaotic"),
])
def test_runtime_runs_all_scenes(scene, topology):
    timeline = IxpansionRuntime(scene, topology).run(3)
    assert [item["tick"] for item in timeline] == [1, 2, 3]
    assert all(item["perception"]["scene"] == scene for item in timeline)
    assert any(item["fingerprint"] for item in timeline)


def test_architect_grows_graph_and_mutator_changes_state():
    runtime = IxpansionRuntime()
    first = runtime.tick()
    assert any(result["agent"] == "architect" for result in first["results"])
    assert runtime.graph.nodes["origin"].state["energy"] > 10


def test_api_and_dashboard_render_snapshot():
    timeline = run_scene(ticks=2)
    rendered = render_dashboard(timeline)
    assert rendered.startswith("TIMELINE 1 -> 2")


def test_inspectors_summarize_workspace():
    structure = inspect("ixpansion/src")
    results = IxpansionRuntime().run(1)[0]["results"]
    summary = summarize(results)
    assert structure["python_files"] > 10
    assert summary["actions"] >= 3


def test_every_accepted_action_has_mesh_delivery_and_witness():
    runtime = IxpansionRuntime()
    timeline = runtime.run(3)

    for tick_result in timeline:
        assert tick_result["mesh_delivered"] == len(tick_result["results"])
        assert len(tick_result["witnesses"]) == len(tick_result["results"])
        assert all(result["delivered"] > 0 for result in tick_result["results"])

    assert len(runtime.witnesses) == sum(len(item["witnesses"]) for item in timeline)


def test_witness_receipts_are_deterministic():
    first = IxpansionRuntime().run(2)
    second = IxpansionRuntime().run(2)
    keys = ("tick", "agent", "evidence_hash", "program")

    assert [
        {key: item[key] for key in keys}
        for item in first[0]["witnesses"]
    ] == [
        {key: item[key] for key in keys}
        for item in second[0]["witnesses"]
    ]


def test_mutation_actions_use_shared_applier_contract():
    runtime = IxpansionRuntime()
    before = runtime.graph.nodes["origin"].state["energy"]
    outcome = runtime._apply_action({"type": "mutate", "node": "origin", "operation": "multiply", "field": "energy", "value": 2})

    assert outcome == {"applied": True}
    assert runtime.graph.nodes["origin"].state["energy"] == before * 2
