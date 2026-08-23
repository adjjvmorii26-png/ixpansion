import pytest

from core.state_graph import StateGraph
from expansion.models.mutation import Mutation
from expansion.mutation_applier import MutationApplier
from expansion.rule_engine import RuleEngine
from expansion.models.rule import Rule
from expansion.seeds_loader import load_seeds


def test_mutations_modify_existing_nodes_only():
    graph = StateGraph()
    graph.add_node("origin", energy=5)
    applier = MutationApplier()
    assert applier.apply(graph, Mutation("origin", "energy", "multiply", 2)) is True
    assert graph.nodes["origin"].state["energy"] == 10
    assert applier.apply(graph, Mutation("missing", "energy", "add", 1)) is False


def test_rule_engine_cools_hot_nodes():
    graph = StateGraph()
    graph.add_node("origin", heat=100)
    engine = RuleEngine()
    engine.add(Rule("cool", "heat", ">", 50, "cool"))
    assert engine.evaluate(graph) == ["cool"]
    assert graph.nodes["origin"].state["heat"] == 90


def test_seed_loader_reads_json(tmp_path):
    path = tmp_path / "seeds.json"
    path.write_text('{"seeds":[{"id":"one","rules":[],"mutations":[]}]}', encoding="utf-8")
    seeds = load_seeds(path)
    assert [seed.id for seed in seeds] == ["one"]


def test_mutation_validates_operations():
    with pytest.raises(ValueError):
        Mutation("origin", "energy", "explode", 1)
