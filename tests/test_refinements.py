"""Refinement tests — unified router, orchestrator, analytics, pulse, and knowledge graph."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_unified_router_health():
    from api.unified_router import UnifiedRouter
    router = UnifiedRouter()
    health = router.health()
    assert health["total"] > 100
    assert health["healthy"] > 50


def test_unified_router_route():
    from api.unified_router import UnifiedRouter
    router = UnifiedRouter()
    result = router.route("entropy_currency", {"action": "status"})
    assert "total_wallets" in result or "status" in result


def test_unified_router_modules():
    from api.unified_router import UnifiedRouter
    router = UnifiedRouter()
    modules = router.list_modules()
    assert len(modules) > 100
    assert "entropy_currency" in modules


def test_unified_router_batch():
    from api.unified_router import UnifiedRouter
    router = UnifiedRouter()
    results = router.batch([
        {"module": "entropy_currency", "payload": {"action": "status"}},
        {"module": "soul_forge", "payload": {"action": "status"}},
    ])
    assert len(results) == 2


def test_cross_module_orchestrator_create():
    from api.cross_module_orchestrator import CrossModuleOrchestrator
    orch = CrossModuleOrchestrator()
    result = orch.create_workflow("dream_to_prophecy", "dream triggers prophecy")
    assert result["workflow"]["name"] == "dream_to_prophecy"


def test_cross_module_orchestrator_add_step():
    from api.cross_module_orchestrator import CrossModuleOrchestrator
    orch = CrossModuleOrchestrator()
    wf = orch.create_workflow("test_flow")
    orch.add_step(wf["workflow"]["id"], "soul_forge", "status")
    orch.add_step(wf["workflow"]["id"], "universal_compass", "status")
    assert len(orch.workflows[wf["workflow"]["id"]].steps) == 2


def test_cross_module_orchestrator_execute():
    from api.cross_module_orchestrator import CrossModuleOrchestrator
    orch = CrossModuleOrchestrator()
    wf = orch.create_workflow("simple_flow")
    orch.add_step(wf["workflow"]["id"], "soul_forge", "status")
    result = orch.execute(wf["workflow"]["id"])
    assert result["steps_executed"] == 1


def test_module_analytics_record():
    from api.module_analytics import ModuleAnalytics
    ma = ModuleAnalytics()
    ma.record("test_module", "test_action", 0.01, True)
    report = ma.module_report("test_module")
    assert report["calls"] == 1


def test_module_analytics_top():
    from api.module_analytics import ModuleAnalytics
    ma = ModuleAnalytics()
    for i in range(10):
        ma.record("frequent_module", "action", 0.001, True)
    ma.record("rare_module", "action", 0.001, True)
    top = ma.top_modules("calls", 5)
    assert top[0]["name"] == "frequent_module"


def test_module_analytics_health():
    from api.module_analytics import ModuleAnalytics
    ma = ModuleAnalytics()
    ma.record("a", "x", 0.01, True)
    ma.record("a", "x", 0.01, False)
    health = ma.system_health()
    assert health["total_calls"] == 2


def test_system_pulse_register():
    from api.system_pulse import SystemPulse
    sp = SystemPulse()
    result = sp.register_vital("cpu_usage", (0.2, 0.8))
    assert result["registered"] == "cpu_usage"


def test_system_pulse_tick():
    from api.system_pulse import SystemPulse
    sp = SystemPulse()
    sp.register_vital("mem")
    sp.register_vital("cpu")
    result = sp.tick()
    assert result["tick"] == 1


def test_system_pulse_critical():
    from api.system_pulse import SystemPulse
    sp = SystemPulse()
    sp.register_vital("temp", (0.3, 0.7))
    sp.update_vital("temp", 0.01)
    report = sp.full_report()
    assert report["temp"]["status"] == "critical"


def test_knowledge_graph_add_node():
    from api.knowledge_graph import KnowledgeGraph
    kg = KnowledgeGraph()
    result = kg.add_node("consciousness", "concept")
    assert result["added"]["name"] == "consciousness"


def test_knowledge_graph_add_edge():
    from api.knowledge_graph import KnowledgeGraph
    kg = KnowledgeGraph()
    kg.add_node("dream")
    kg.add_node("subconscious")
    result = kg.add_edge("dream", "subconscious", "part_of")
    assert "edge" in result


def test_knowledge_graph_path():
    from api.knowledge_graph import KnowledgeGraph
    kg = KnowledgeGraph()
    kg.add_edge("a", "b", "connects")
    kg.add_edge("b", "c", "connects")
    result = kg.find_path("a", "c")
    assert result["path"] == ["a", "b", "c"]


def test_knowledge_graph_gaps():
    from api.knowledge_graph import KnowledgeGraph
    kg = KnowledgeGraph()
    kg.add_node("isolated_concept")
    kg.add_node("connected_a")
    kg.add_node("connected_b")
    kg.add_edge("connected_a", "connected_b")
    gaps = kg.knowledge_gaps()
    assert any(g["node"] == "isolated_concept" for g in gaps)
