from __future__ import annotations
"""Wave 105 — More Experimental Unique Innovations Tests."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── Fractal Growth ────────────────────────────────────────────────

def test_plant_seed():
    from api.fractal_growth import FractalGrowth
    fg = FractalGrowth()
    result = fg.plant_seed("quantum")
    assert "organism_id" in result
    assert result["name"] == "quantum"

def test_grow():
    from api.fractal_growth import FractalGrowth
    fg = FractalGrowth()
    seed = fg.plant_seed("test")
    result = fg.grow(seed["organism_id"])
    assert len(result["children"]) >= 1

def test_tree():
    from api.fractal_growth import FractalGrowth
    fg = FractalGrowth()
    seed = fg.plant_seed("tree_test")
    fg.grow(seed["organism_id"])
    tree = fg.tree(seed["organism_id"], 1)
    assert tree["name"] == "tree_test"


# ── Consciousness Simulator ───────────────────────────────────────

def test_process_input():
    from api.consciousness_simulator import ConsciousnessSimulator
    cs = ConsciousnessSimulator()
    result = cs.process_input("novelty")
    assert "level" in result
    assert result["level"] in ["unaware", "reactive", "attentive", "aware", "self_aware", "meta_cognitive"]

def test_consciousness_evolution():
    from api.consciousness_simulator import ConsciousnessSimulator
    cs = ConsciousnessSimulator()
    levels = set()
    for inp in ["novelty", "reflection", "interaction", "error", "data"]:
        result = cs.process_input(inp)
        levels.add(result["level"])
    assert len(levels) >= 1


# ── Dream Logic Compiler ──────────────────────────────────────────

def test_compile_dream():
    from api.dream_logic_compiler import DreamLogicCompiler
    dlc = DreamLogicCompiler()
    result = dlc.compile(["fragment a", "fragment b", "fragment c"])
    assert "compilation_id" in result
    assert result["node_count"] == 3

def test_compile_with_mood():
    from api.dream_logic_compiler import DreamLogicCompiler
    dlc = DreamLogicCompiler()
    result = dlc.compile(["test"], mood="ominous")
    assert result["tree"]["mood"] == "ominous"


# ── Reality Distortion ────────────────────────────────────────────

def test_create_field():
    from api.reality_distortion import RealityDistortion
    rd = RealityDistortion()
    result = rd.create("Test Zone", intensity=0.5)
    assert "field_id" in result
    assert result["intensity"] == 0.5

def test_distort():
    from api.reality_distortion import RealityDistortion
    rd = RealityDistortion()
    field = rd.create("Chaos Zone")
    result = rd.distort(field["field_id"], "price", 10.0)
    assert "distorted" in result
    assert result["original"] == 10.0

def test_deactivate():
    from api.reality_distortion import RealityDistortion
    rd = RealityDistortion()
    field = rd.create("Temp Zone")
    result = rd.deactivate(field["field_id"])
    assert result["status"] == "deactivated"


# ── Collective Memory ─────────────────────────────────────────────

def test_remember():
    from api.collective_memory import CollectiveMemory
    cm = CollectiveMemory()
    result = cm.remember("test_agent", "test memory", ["tag1"])
    assert "memory_id" in result

def test_recall():
    from api.collective_memory import CollectiveMemory
    cm = CollectiveMemory()
    cm.remember("agent", "quantum discovery", ["quantum"])
    results = cm.recall("quantum")
    assert len(results) >= 1


# ── Evolution Simulator ───────────────────────────────────────────

def test_spawn_species():
    from api.evolution_simulator import EvolutionSimulator
    es = EvolutionSimulator()
    result = es.spawn_species("Alpha")
    assert result["name"] == "Alpha"
    assert result["fitness"] > 0

def test_evolve():
    from api.evolution_simulator import EvolutionSimulator
    es = EvolutionSimulator()
    es.spawn_species("A")
    es.spawn_species("B")
    result = es.evolve()
    assert result["generation"] >= 1
    assert result["species_count"] >= 2


# ── Chaos Orchestration ──────────────────────────────────────────

def test_inject():
    from api.chaos_orchestration import ChaosOrchestration
    co = ChaosOrchestration()
    result = co.inject("neural_fabric")
    assert "effect" in result
    assert "chaos_level" in result

def test_chaos_status():
    from api.chaos_orchestration import ChaosOrchestration
    co = ChaosOrchestration()
    co.inject()
    status = co.status()
    assert "chaos_level" in status
    assert status["total_injections"] >= 1


# ── Narrative Generator ───────────────────────────────────────────

def test_generate_story():
    from api.narrative_generator import NarrativeGenerator
    ng = NarrativeGenerator()
    story = ng.generate("discovery")
    assert "story_id" in story
    assert "narrative" in story
    assert story["word_count"] > 0

def test_library():
    from api.narrative_generator import NarrativeGenerator
    ng = NarrativeGenerator()
    ng.generate("test")
    lib = ng.library()
    assert len(lib) >= 1


# ── Handler smoke tests ───────────────────────────────────────────

def test_all_handlers():
    from api.fractal_growth import handler as h1
    from api.consciousness_simulator import handler as h2
    from api.dream_logic_compiler import handler as h3
    from api.reality_distortion import handler as h4
    from api.collective_memory import handler as h5
    from api.evolution_simulator import handler as h6
    from api.chaos_orchestration import handler as h7
    from api.narrative_generator import handler as h8
    for h in [h1, h2, h3, h4, h5, h6, h7, h8]:
        result = h({}, {})
        assert isinstance(result, (dict, list))
