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
