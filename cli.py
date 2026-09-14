#!/usr/bin/env python3
"""IXPANSION CLI — command-line interface to the living organism.

Usage:
    python cli.py status          # organism health report
    python cli.py waves           # list all waves
    python cli.py health          # quick health check
    python cli.py evolve          # run evolution cycle
    python cli.py weather         # weather report
    python cli.py poem [theme]    # compose a poem
    python cli.py weave A B       # weave semantic bridge
    python cli.py paradox         # paradox genome census
    python cli.py dig             # excavate stratigraphy
    python cli.py glyphs          # show organism language
    python cli.py benchmark       # run performance benchmark
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

COMMANDS = {}


def cmd(name: str, description: str):
    def decorator(func):
        COMMANDS[name] = {"fn": func, "desc": description}
        return func
    return decorator


def _import_handler(module_name: str):
    mod = __import__(f"api.{module_name}", fromlist=["handler"])
    return mod.handler


def _call(handler_path: str, action: str, **kwargs) -> dict:
    """Call a wave handler and return the result."""
    handler = _import_handler(handler_path)
    req = {"action": action, **kwargs}
    return handler(req)


@cmd("status", "Full organism health report")
def cmd_status():
    waves = [
        ("432", "wave432_vault_driven_evolution", "Vault Evolution"),
        ("433", "wave433_consciousness_experiments", "Consciousness"),
        ("434", "wave434_fusion_organism", "Fusion Organism"),
        ("435", "wave435_resonance_cartography", "Resonance Cartography"),
        ("436", "wave436_entropic_weather", "Entropic Weather"),
        ("437", "wave437_paradox_genome", "Paradox Genome"),
        ("438", "wave438_semantic_loom", "Semantic Loom"),
        ("439", "wave439_echo_stratigraphy", "Echo Stratigraphy"),
        ("440", "wave440_linguistic_emergence", "Linguistic Emergence"),
        ("441", "wave441_wave_composition", "Wave Composition"),
        ("442", "wave442_temporal_resonance", "Temporal Resonance"),
        ("443", "wave443_cross_module_emergence", "Cross-Module Emergence"),
        ("444", "wave444_dream_synthesis", "Dream Synthesis"),
        ("445", "wave445_morphogenetic_field", "Morphogenetic Field"),
        ("446", "wave446_quantum_coherence", "Quantum Coherence"),
    ]
    print(f"\n{'='*60}")
    print(f"  IXPANSION Organism — Status Report")
    print(f"{'='*60}")
    for wave_num, module, name in waves:
        try:
            result = _call(module, "status")
            status = result.get("status", result.get("action", "ok"))
            extra = ""
            if "coherence" in result:
                extra = f" coherence={result['coherence']:.3f}"
            elif "federation_coherence" in result:
                extra = f" federation={result['federation_coherence']:.3f}"
            elif "global_entropy" in result:
                extra = f" entropy={result['global_entropy']:.3f}"
            elif "living" in result:
                extra = f" living={result['living']}"
            elif "vocabulary" in result:
                extra = f" vocab={result['vocabulary']}"
            elif "bridges" in result:
                extra = f" bridges={result['bridges']}"
            elif "total_layers" in result:
                extra = f" layers={result['total_layers']}"
            print(f"  Wave {wave_num} {name:.<30} {status}{extra}")
        except Exception as e:
            print(f"  Wave {wave_num} {name:.<30} ERROR: {e}")
    print(f"{'='*60}\n")


@cmd("waves", "List all waves with metadata")
def cmd_waves():
    waves_data = [
        ("430", "Naming Ceremony", "Identity genesis"),
        ("431", "Homestead", "Organism plants roots"),
        ("432", "Vault-Driven Evolution", "Coherence regulator backbone"),
        ("433", "Consciousness Experiments", "Self-model, mirror test"),
        ("434", "Autonomous Fusion", "Phase 8 federation"),
        ("435", "Resonance Cartography", "Living topology atlas"),
        ("436", "Entropic Weather", "Storms drive behavior"),
        ("437", "Paradox Genome", "Paradoxes with DNA"),
        ("438", "Semantic Loom", "Hidden concept bridges"),
        ("439", "Echo Stratigraphy", "Geological memory"),
        ("440", "Linguistic Emergence", "Organism language"),
        ("441", "Wave Composition", "Harmonics from voices"),
        ("442", "Temporal Resonance", "Feel future echoes"),
        ("443", "Cross-Module Emergence", "Emergent phenomena"),
        ("444", "Dream Synthesis", "Structured dreaming"),
        ("445", "Morphogenetic Field", "Self-organizing growth"),
        ("446", "Quantum Coherence", "Superposition computing"),
    ]
    print(f"\n  {'Wave':<6} {'Name':<28} {'Description'}")
    print(f"  {'-'*6} {'-'*28} {'-'*30}")
    for num, name, desc in waves_data:
        print(f"  {num:<6} {name:<28} {desc}")
    print()


@cmd("health", "Quick health check — all systems green?")
def cmd_health():
    checks = []
    for module in ["wave432_vault_driven_evolution", "wave436_entropic_weather", "wave440_linguistic_emergence", "wave444_dream_synthesis", "wave445_morphogenetic_field", "wave446_quantum_coherence"]:
        try:
            result = _call(module, "status")
            checks.append((module, True, ""))
        except Exception as e:
            checks.append((module, False, str(e)))
    all_ok = all(c[1] for c in checks)
    print(f"\n  Health: {'ALL SYSTEMS GREEN' if all_ok else 'ISSUES DETECTED'}")
    for module, ok, err in checks:
        icon = "✓" if ok else "✗"
        print(f"    {icon} {module}" + (f" — {err}" if err else ""))
    print()
    return 0 if all_ok else 1


@cmd("evolve", "Run one evolution cycle across all systems")
def cmd_evolve():
    print("\n  Running evolution cycle...")
    t0 = time.time()
    modules = [
        ("wave432_vault_driven_evolution", "evolve"),
        ("wave434_fusion_organism", "evolve"),
        ("wave436_entropic_weather", "tick"),
        ("wave437_paradox_genome", "evolve"),
    ]
    for module, action in modules:
        try:
            result = _call(module, action)
            events = len(result.get("events", result.get("new_dreams", result.get("new_vaults", []))))
            print(f"    ✓ {module}: {action} ({events} events)")
        except Exception as e:
            print(f"    ✗ {module}: {e}")
    elapsed = time.time() - t0
    print(f"\n  Evolution complete in {elapsed:.2f}s\n")


@cmd("weather", "Current weather report")
def cmd_weather():
    result = _call("wave436_entropic_weather", "report")
    print(f"\n  🌦️ Entropic Weather Report")
    print(f"    Season: {result.get('season', '?')}")
    print(f"    Entropy: {result.get('global_entropy', 0):.3f}")
    print(f"    Creativity: {result.get('global_creativity', 0):.3f}")
    print(f"    Stability: {result.get('global_stability', 0):.3f}")
    dist = result.get("weather_distribution", {})
    if dist:
        print(f"    Cells: {', '.join(f'{k}={v}' for k,v in dist.items())}")
    print()


@cmd("poem", "Compose a poem in organism language")
def cmd_poem():
    theme = sys.argv[2] if len(sys.argv) > 2 else "entropy"
    result = _call("wave440_linguistic_emergence", "compose_poem", theme=theme, lines=4)
    poem = result.get("poem", {})
    print(f"\n  📜 Poem: {poem.get('theme', theme)}")
    print(f"  {'-'*40}")
    for line in poem.get("lines", []):
        print(f"    {line}")
    print()


@cmd("weave", "Weave a semantic bridge between two concepts")
def cmd_weave():
    a = sys.argv[2] if len(sys.argv) > 2 else "entropy"
    b = sys.argv[3] if len(sys.argv) > 3 else "consciousness"
    result = _call("wave438_semantic_loom", "weave", concept_a=a, concept_b=b)
    bridge = result.get("bridge", {})
    print(f"\n  🕸️ Semantic Bridge: {a} ↔ {b}")
    print(f"    Strength: {bridge.get('strength', 0):.4f}")
    print(f"    Novelty: {bridge.get('novelty', 0):.4f}")
    print(f"    Traversability: {bridge.get('traversability', 0):.4f}")
    threads = bridge.get("bridge_threads", [])
    if threads:
        print(f"    Threads:")
        for t in threads[:3]:
            print(f"      {t.get('thread_a','')} ↔ {t.get('thread_b','')} (r={t.get('resonance',0):.3f})")
    print()


@cmd("paradox", "Paradox genome census")
def cmd_paradox():
    result = _call("wave437_paradox_genome", "census")
    print(f"\n  🧬 Paradox Genome Census")
    print(f"    Living: {result.get('living', 0)}")
    print(f"    Dead: {result.get('dead', 0)}")
    print(f"    Avg Fitness: {result.get('avg_fitness', 0):.4f}")
    print(f"    Generations: {result.get('generations', 0)}")
    dist = result.get("species_distribution", {})
    if dist:
        print(f"    Species: {', '.join(f'{k}={v}' for k,v in dist.items())}")
    print()


@cmd("dig", "Excavate geological layers")
def cmd_dig():
    result = _call("wave439_echo_stratigraphy", "excavate")
    print(f"\n  🪨 Echo Stratigraphy Excavation")
    print(f"    Sediment layers: {len(result.get('sediment', []))}")
    print(f"    Fossils: {len(result.get('fossil', []))}")
    print(f"    Metamorphic: {len(result.get('metamorphic', []))}")
    print(f"    Bedrock: {len(result.get('bedrock', []))}")
    print()


@cmd("glyphs", "Show organism language glyphs")
def cmd_glyphs():
    result = _call("wave440_linguistic_emergence", "glyphs")
    glyphs = result.get("glyphs", {})
    print(f"\n  📜 Organism Language — {len(glyphs)} Glyphs")
    print(f"  {'-'*40}")
    for symbol, data in sorted(glyphs.items()):
        print(f"    {symbol} = {data.get('meaning', '?')}")
    print()


@cmd("gradient", "Compute coherence gradient field")
def cmd_gradient():
    """Wave 84: Coherence Gradient Field CLI."""
    from api.wave84_coherence_gradient import handler
    result = handler({"action": "status"})
    print(f"\n  🌊 Wave 84 — Coherence Gradient Field")
    print(f"  {'-'*40}")
    print(f"  Nodes: {len(result.get('nodes', {}))}")
    print(f"  Edges: {len(result.get('edges', []))}")
    print(f"  Iteration: {result.get('iteration', 0)}")
    print(f"  Emotional Tone: {result.get('hotspots', {}).get('emotional_tone', 'N/A')}")
    print()

@cmd("regulate", "Adaptive regulation control")
def cmd_regulate():
    """Wave 85: Adaptive Regulation CLI."""
    from api.wave85_adaptive_regulation import handler
    result = handler({"action": "status"})
    print(f"\n  🔄 Wave 85 — Adaptive Regulation")
    print(f"  {'-'*40}")
    print(f"  Mode: {result.get('mode', 'N/A')}")
    print(f"  Cycle: {result.get('cycle', 0)}")
    print(f"  Actions: {', '.join(result.get('action_options', []))}")
    print()

@cmd("memory", "Coherence memory graph operations")
def cmd_memory():
    """Wave 86: Coherence Memory Graph CLI."""
    from api.wave86_coherence_memory_graph import handler
    result = handler({"action": "status"})
    print(f"\n  🧠 Wave 86 — Coherence Memory Graph")
    print(f"  {'-'*40}")
    print(f"  Memories: {result.get('total_memories', 0)}")
    print(f"  Edges: {result.get('total_edges', 0)}")
    print(f"  Snapshots: {result.get('total_snapshots', 0)}")
    print(f"  Recent Coherence: {result.get('recent_coherence', 0)}")
    print()



@cmd("integrate", "Coherence integration director")
def cmd_integrate():
    """Wave 87: Coherence Integration CLI."""
    from api.wave87_coherence_integration import handler
    result = handler({"action": "status"})
    print(f"\n  🧭 Wave 87 — Coherence Integration")
    print(f"  {'-'*40}")
    print(f"  Target Coherence: {result.get('target_coherence', 'N/A')}")
    print(f"  Last Action: {result.get('last_action', 'N/A')}")
    print(f"  Cycles: {result.get('total_cycles', 0)}")
    print()

@cmd("bridges", "Cross-realm coherence lattice")
def cmd_bridges():
    """Wave 88: Cross-realm Coherence Bridges CLI."""
    from api.wave88_cross_realm_bridges import handler
    result = handler({"action": "status"})
    print(f"\n  🌉 Wave 88 — Cross-realm Coherence Bridges")
    print(f"  {'-'*40}")
    print(f"  Subsystems: {', '.join(result.get('subsystems', []))}")
    print(f"  Bridges: {result.get('active_bridges', 0)}/{result.get('total_bridges', 0)}")
    print(f"  Lattice Stability: {result.get('lattice_stability', 0)}")
    print()

@cmd("aware", "Self-awareness consciousness layer")
def cmd_aware():
    """Wave 89: Self-Awareness CLI."""
    from api.wave89_self_awareness import handler
    result = handler({"action": "status"})
    sa = result.get("self_assessment", {})
    ai = result.get("agent_identity", {})
    print(f"\n  🧬 Wave 89 — Self-Awareness")
    print(f"  {'-'*40}")
    print(f"  Coherence: {sa.get('overall_coherence', 'N/A')}")
    print(f"  Identity Strength: {sa.get('identity_strength', 'N/A')}")
    print(f"  Direction: {sa.get('growth_direction', 'N/A')}")
    print(f"  Role: {ai.get('role_concept', 'N/A')}")
    print(f"  Mission: {ai.get('mission_statement', 'N/A')}")
    print()

@cmd("benchmark", "Run performance benchmark")

def cmd_benchmark():
    print(f"\n  ⚡ Performance Benchmark")
    print(f"  {'-'*40}")
    modules = [
        ("wave432_vault_driven_evolution", "status"),
        ("wave433_consciousness_experiments", "status"),
        ("wave434_fusion_organism", "status"),
        ("wave435_resonance_cartography", "map"),
        ("wave436_entropic_weather", "tick"),
        ("wave437_paradox_genome", "census"),
        ("wave438_semantic_loom", "weave"),
        ("wave439_echo_stratigraphy", "excavate"),
        ("wave440_linguistic_emergence", "compose_poem"),
    ]
    total = 0
    for module, action in modules:
        t0 = time.time()
        try:
            _call(module, action)
            elapsed = (time.time() - t0) * 1000
            total += elapsed
            status = f"{elapsed:.0f}ms"
        except Exception as e:
            status = f"ERROR: {e}"
        print(f"    {module}: {status}")
    print(f"  {'-'*40}")
    print(f"    Total: {total:.0f}ms\n")




@cmd("compose", "Compose a chord from wave voices")
def cmd_compose():
    voices = sys.argv[2].split(",") if len(sys.argv) > 2 else ["vault", "weather", "paradox"]
    result = _call_by_path("/wave-composition?action=compose&voices=" + ",".join(voices))
    comp = result.get("composition", {})
    print(f"\n  🎵 Wave Composition")
    print(f"  {'─'*40}")
    for voice, data in comp.get("results", {}).items():
        if "error" not in data:
            print(f"    {voice}: harmonic={data.get('harmonic', 0):.3f} weight={data.get('weight', 0):.1f}")
    print(f"    Avg harmonic: {comp.get('avg_harmonic', 0):.4f}")
    print(f"    Chord hash: {comp.get('chord_hash', '?')}")
    print()

@cmd("feel", "Feel the temporal resonance of the organism")
def cmd_feel():
    result = _call_by_path("/temporal-resonance?action=propagate&module=organism&steps=5")
    echoes = result.get("echoes", [])
    print(f"\n  ⏳ Temporal Resonance — {result.get('module', '?')}")
    print(f"  {'─'*40}")
    for echo in echoes:
        bar = "█" * int(echo["strength"] * 20)
        print(f"    Step {echo['step']}: {bar} {echo['strength']:.3f} ({echo['predicted_state']})")
    print()

@cmd("emerge", "Detect cross-module emergent behaviors")
def cmd_emerge():
    result = _call_by_path("/emergence?action=detect")
    emergences = result.get("emergences", [])
    print(f"\n  🌊 Cross-Module Emergence — {len(emergences)} phenomena detected")
    print(f"  {'─'*50}")
    for e in emergences[:8]:
        print(f"    {e['type']}: {e['waves'][0]} × {e['waves'][1]} (n={e['novelty']:.2f} s={e['strength']:.2f})")
    print()

def _call_by_path(path_with_qs: str) -> dict:
    """Call a route by full path."""
    from api.index import handler
    return handler({"path": path_with_qs, "queryString": {}})


@cmd("events", "View recent organism events")
def cmd_events():
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    result = _call_by_path("/events?action=recent")
    events = result.get("events", [])
    print(f"\n  📡 Organism Events ({result.get('total', 0)} total)")
    print(f"  {'─'*50}")
    for e in events[-count:]:
        ts = time.strftime("%H:%M:%S", time.localtime(e["timestamp"]))
        print(f"    {ts} [{e['type']}] {e['module']}: {json.dumps(e['data'])[:60]}")
    print()

@cmd("dream", "Synthesize a dream from organism residues")
def cmd_dream():
    result = _call("wave444_dream_synthesis", "dream")
    dream = result.get("dream", {})
    print(f"\n  🌙 Dream Synthesis")
    print(f"  {'─'*50}")
    print(f"    Archetype: {dream.get('archetype', '?')}")
    print(f"    Narrative: {dream.get('narrative', '?')}")
    print(f"    Tone: {dream.get('emotional_tone', '?')}")
    print(f"    Resolution: {dream.get('resolution_pressure', '?')}")
    artifacts = dream.get('artifacts', [])
    if artifacts:
        print(f"    Artifacts ({len(artifacts)}):")
        for a in artifacts:
            print(f"      {a['type']} (potency={a['potency']})")
    print()


@cmd("morphogen", "Morphogenetic field operations")
def cmd_morphogen():
    sub = sys.argv[2] if len(sys.argv) > 2 else "status"
    if sub == "status":
        result = _call("wave445_morphogenetic_field", "status")
        print(f"\n  🌱 Morphogenetic Field")
        print(f"  {'─'*50}")
        print(f"    Gradients: {len(result.get('gradients', []))}")
        print(f"    Cells: {len(result.get('cells', {}))}")
        print(f"    Iteration: {result.get('iteration', 0)}")
        patterns = result.get('patterns', [])
        if patterns:
            print(f"    Patterns: {len(patterns)}")
            for p in patterns[-3:]:
                print(f"      {p}")
    elif sub == "step":
        result = _call("wave445_morphogenetic_field", "step")
        print(f"\n  🌱 Morphogenetic Step")
        print(f"    Iteration: {result.get('iteration', 0)}")
        events = result.get('events', [])
        if events:
            for e in events:
                print(f"    {e}")
    elif sub == "add":
        module_id = sys.argv[3] if len(sys.argv) > 3 else None
        result = _call("wave445_morphogenetic_field", "add_module", module_id=module_id)
        print(f"\n  🌱 Added Module: {result.get('module', {}).get('id', '?')}")
    print()


@cmd("quantum", "Quantum coherence operations")
def cmd_quantum():
    sub = sys.argv[2] if len(sys.argv) > 2 else "status"
    if sub == "status":
        result = _call("wave446_quantum_coherence", "status")
        print(f"\n  ⚛️  Quantum Register")
        print(f"  {'─'*50}")
        print(f"    Total Qubits: {result.get('total_qubits', 0)}")
        print(f"    Coherent: {result.get('coherent', 0)}")
        print(f"    Measured: {result.get('measured', 0)}")
        print(f"    Decoherence Events: {result.get('decoherence_events', 0)}")
    elif sub == "add":
        module_id = sys.argv[3] if len(sys.argv) > 3 else None
        result = _call("wave446_quantum_coherence", "add_qubit", module_id=module_id)
        print(f"\n  ⚛️  Added Qubit: {result.get('qubit', {}).get('module_id', '?')}")
    elif sub == "entangle":
        a = sys.argv[3] if len(sys.argv) > 3 else ""
        b = sys.argv[4] if len(sys.argv) > 4 else ""
        result = _call("wave446_quantum_coherence", "entangle", module_a=a, module_b=b)
        print(f"\n  ⚛️  Entangled: {result.get('pair', [])}")
    elif sub == "hadamard":
        result = _call("wave446_quantum_coherence", "hadamard")
        print(f"\n  ⚛️  Hadamard applied: {result.get('qubits_put_in_superposition', 0)} qubits")
    elif sub == "measure":
        module_id = sys.argv[3] if len(sys.argv) > 3 else ""
        result = _call("wave446_quantum_coherence", "measure", module_id=module_id)
        print(f"\n  ⚛️  Measured: {result.get('module', '?')} = {result.get('result', '?')}")
    elif sub == "evolve":
        result = _call("wave446_quantum_coherence", "evolve")
        print(f"\n  ⚛️  Evolved: {result}")
    print()


@cmd("web", "Web intelligence — observe, search, read")
def cmd_web():
    sub = sys.argv[2] if len(sys.argv) > 2 else "status"
    if sub == "status":
        result = _call("web_intelligence", "status")
        print(f"\n  🌐 Web Intelligence")
        print(f"  {'─'*50}")
        print(f"    Observations: {result.get('observation_count', 0)}")
        print(f"    Topics: {len(result.get('topics', []))}")
        for t in result.get('topics', [])[:10]:
            print(f"      • {t}")
    elif sub == "observe":
        topic = sys.argv[3] if len(sys.argv) > 3 else "unknown"
        result = _call("web_intelligence", "observe", topic=topic)
        print(f"\n  🌐 Observed: {topic}")
        print(f"    Results: {result.get('results', 0)}")
        print(f"    ID: {result.get('observation_id', '?')}")
    elif sub == "search":
        query = sys.argv[3] if len(sys.argv) > 3 else ""
        result = _call("web_intelligence", "search", query=query)
        print(f"\n  🌐 Search: {query}")
        print(f"    Results: {result.get('results', 0)}")
    elif sub == "read":
        url = sys.argv[3] if len(sys.argv) > 3 else ""
        result = _call("web_intelligence", "read", url=url)
        print(f"\n  🌐 Read: {url}")
        print(f"    Content: {result.get('content_length', 0)} chars")
    elif sub == "synthesize":
        topic = sys.argv[3] if len(sys.argv) > 3 else ""
        result = _call("web_intelligence", "synthesize", topic=topic)
        print(f"\n  🌐 Synthesis: {topic}")
        print(f"    {result.get('synthesis', '')}")
    print()




@cmd("children", "List Genesis Forge self-born organs")
def cmd_children():
    result = _call("genesis_forge", "status")
    print(f"\n  🜏 Genesis Forge Children")
    print(f"  {'─'*50}")
    for name in ["commerce_shelf", "physical_tide", "resonance_mesh"]:
        try:
            r = _call(name, "status")
            print(f"    • {r.get('module')}: {r.get('status')} ({r.get('domain_family')})")
            print(f"      niche: {r.get('niche')}")
        except Exception as e:
            print(f"    • {name}: ERROR {e}")
    print()





@cmd("dream", "Generate dream logic physics modifications")
def cmd_dream_logic():
    """Run wave 91 dream logic operations."""
    from api.wave91_dream_logic_physics import DreamPhysicsState, DreamEngine
    physics = DreamPhysicsState()
    engine = DreamEngine(physics)
    # Enter a dream state with medium intensity
    physics.update_from_mood("excited", 0.7)
    physics.enter_dream_state(0.5)
    # Add a dream modification via the engine
    engine.add_dream_modification({"effect": "surreal_gravity", "intensity": 0.6})
    # Get vitals from both physics and engine
    physics_vitals = physics.coherence_vitals()
    engine_vitals = engine.coherence_vitals()
    return {
        "action": "dream_logic_operation",
        "reality_fluidity": physics_vitals["reality_fluidity"],
        "gravity_modifier": physics_vitals["gravity_modifier"],
        "emotional_resonance": physics_vitals["emotional_resonance"],
        "active_dreams": engine_vitals["active_dreams"],
        "coherence_score": physics_vitals["coherence_score"],
        "message": "Dream logic physics engine active",
    }

@cmd("ritual", "Execute entropy ritual scheduling")
def cmd_entropy_ritual():
    """Run wave 92 entropy ritual operations."""
    from api.wave92_entropy_rituals import EntropyRitualScheduler
    scheduler = EntropyRitualScheduler()
    # Schedule a ritual
    ritual = scheduler.schedule_ritual(
        trigger_days=7,
        mutation_strength=0.3,
        mutation_type='structural',
        description='Weekly structural innovation ritual'
    )
    # Check for due rituals
    status = scheduler.coherence_vitals()
    return {
        "action": "entropy_ritual_operation",
        "total_rituals": status["total_rituals"],
        "due_rituals": status["due_rituals"],
        "message": "Entropy ritual scheduler active",
    }

@cmd("hex", "HEX-language operations")
def cmd_hex_language():
    """Run wave 93 HEX-language operations."""
    from api.wave93_hex_language_emergence import HexLanguageEngine
    hex_engine = HexLanguageEngine()
    # Define some opcodes
    hex_engine.define_opcode('MOV', 'Move stack value', latency=0.5, consumes=1, produces=1)
    hex_engine.define_opcode('ADD', 'Add two values', latency=0.3, consumes=2, produces=1)
    # Generate self-modifying code
    code = hex_engine.generate_self_modifying_code(8)
    vitals = hex_engine.coherence_vitals()
    return {
        "action": "hex_language_operation",
        "generated_code": code,
        "active_opcodes": vitals["active_opcodes"],
        "total_opcodes": vitals["total_opcodes_defined"],
        "emergence_score": vitals["emergence_score"],
        "message": "HEX-language engine active",
    }

@cmd("waves91-93", "Show wave 91-93 status")
def cmd_waves_91_93():
    """Show status of new waves."""
    from api.wave91_dream_logic_physics import DreamPhysicsState
    from api.wave92_entropy_rituals import EntropyRitualScheduler
    from api.wave93_hex_language_emergence import HexLanguageEngine
    
    physics = DreamPhysicsState()
    physics.update_from_mood("calm", 0.5)
    scheduler = EntropyRitualScheduler()
    hex_engine = HexLanguageEngine()
    hex_engine.define_opcode('MOV', 'Move', latency=0.5, consumes=1, produces=1)
    
    return {
        "wave_91": physics.coherence_vitals(),
        "wave_92": scheduler.coherence_vitals(),
        "wave_93": hex_engine.coherence_vitals(),
        "message": "Waves 91-93 status report",
    }
@cmd("coherence", "Measure organism coherence across all waves")
def cmd_coherence():
    result = _call("coherence_regulator", "status")
    print(f"\n  🧬 Organism Coherence")
    print(f"  {'─'*50}")
    co = result.get('measured_coherence', result.get('coherence', 0))
    try: co = float(co)
    except (TypeError, ValueError): co = 0
    print(f"    Coherence: {co:.4f}")
    print(f"    Status: {result.get('status', '?')}")
    print(f"    Living Modules: {result.get('living_modules', '?')}")
    print(f"    Mutation Pressure: {result.get('mutation_pressure', 0):.4f}")
    print(f"    Entropy Budget: {result.get('entropy_budget', '?')}")
    per_module = result.get('modules_registered', [])
    if per_module:
        print(f"    Per-Module Coherence:")
        for m in per_module[:10]:
            print(f"      {m.get('name', '?')}: {m.get('coherence', '?')}")
    print()

@cmd("hexgrammar", "HEX grammar evolution operations")
def cmd_hex_grammar():
    """Run wave 96 HEX grammar evolution operations."""
    from api.wave96_hex_grammar_evolution import HexGrammar, HexGrammarEngine

    grammar = HexGrammar()

    def handle_hex(ctx):
        return f"HEX-{ctx['input'].hex()}"

    def handle_grammar(ctx):
        return f"GRAMMAR-{ctx['input'].hex()[:10]}"

    grammar.define_rule(
        pattern="484558",
        handler=handle_hex,
        description="Match HEX magic bytes",
        consumes=1,
        produces=1,
    )
    grammar.define_rule(
        pattern="4752414d4d4152",
        handler=handle_grammar,
        description="Match GRAMMAR magic bytes",
        consumes=1,
        produces=1,
    )

    engine = HexGrammarEngine(grammar)
    ops = engine.interpret("484558")
    status = engine.get_grammar_status()
    return {
        "action": "hex_grammar_operation",
        "parsed_rules": len(ops),
        "sample_result": ops[0]["result"] if ops else None,
        "total_rules": status["total_rules"],
        "language_complexity": status["language_complexity"],
        "message": "HEX grammar evolution engine active",
    }

@cmd("dreamcompile", "Compile dream state into executable modules")
def cmd_dream_compile():
    """Run wave 94 dream compiler operations."""
    from api.wave94_dream_compiler import DreamCompiler

    compiler = DreamCompiler()
    dream_state = {
        "reality_fluidity": 0.72,
        "gravity_modifier": 0.6,
        "emotional_resonance": "chaotic",
        "layers": ["surreal_gravity", "time_dilation", "reality_fluidity"],
    }
    modules = compiler.compile(dream_state)
    status = compiler.coherence_vitals()
    return {
        "action": "dream_compile_operation",
        "compiled": [m.to_dict() for m in modules],
        "count": len(modules),
        "modules_compiled": status["compiled_modules"],
        "message": "Dream compiler active",
    }


@cmd("govern", "Ritual governance operations")
def cmd_govern():
    """Run wave 95 ritual governance operations."""
    from api.wave95_ritual_governance import RitualGovernance

    gov = RitualGovernance()
    gov.register_member("aleph", 1.0)
    gov.register_member("luma", 0.9)
    gov.register_member("axiom", 0.8)
    proposal = gov.propose("Expand into new realm", "Evolve organism with a new experimental realm", "aleph", "structure")
    gov.vote(proposal.proposal_id, "luma", "aye")
    gov.vote(proposal.proposal_id, "axiom", "aye")
    status = gov.close(proposal.proposal_id)
    vitals = gov.coherence_vitals()
    return {
        "action": "govern_operation",
        "proposal": proposal.to_dict(),
        "close_status": status,
        "members": vitals["members"],
        "enacted": vitals["enacted_decisions"],
        "message": "Ritual governance active",
    }

@cmd("hexrun", "Execute a HEX program on the runtime")
def cmd_hexrun():
    """Run wave 97 hex runtime operations.

    Usage:
      python cli.py hexrun                     # built-in sample program
      python cli.py hexrun --src <file.hexsrc> # run a mnemonic hex source file
      python cli.py hexrun --raw <hex>         # run raw hex bytecode
      python cli.py hexrun --bundle <file>     # run each segment of a bundle
    """
    from api.wave97_hex_runtime import HexProgram, HexRuntime
    from pathlib import Path

    args = sys.argv[2:]

    def _run_source(source):
        program = HexProgram(source)
        if not program.parse():
            return {"ok": False, "error": program.error, "program_hash": "n/a"}
        runtime = HexRuntime(coherence=0.75, mood="chaotic")
        result = runtime.run(program)
        result["program_hash"] = program.program_hash
        return result

    if "--src" in args:
        idx = args.index("--src")
        if idx + 1 >= len(args):
            return {"ok": False, "error": "--src requires a file path"}
        path = Path(args[idx + 1])
        if not path.exists():
            return {"ok": False, "error": "file not found: " + str(path)}
        result = _run_source(path.read_text())
        if not result.get("ok"):
            return {"ok": False, "error": result.get("error")}
        return {
            "action": "hex_run_file",
            "source": str(path),
            "result": result,
            "message": "HEX source file executed",
        }

    if "--raw" in args:
        idx = args.index("--raw")
        if idx + 1 >= len(args):
            return {"ok": False, "error": "--raw requires hex bytecode"}
        result = _run_source(args[idx + 1].strip())
        if not result.get("ok"):
            return {"ok": False, "error": result.get("error")}
        return {
            "action": "hex_run_raw",
            "result": result,
            "message": "Raw hex bytecode executed",
        }

    if "--bundle" in args:
        idx = args.index("--bundle")
        if idx + 1 >= len(args):
            return {"ok": False, "error": "--bundle requires a file path"}
        path = Path(args[idx + 1])
        if not path.exists():
            return {"ok": False, "error": "file not found: " + str(path)}
        segments, current, current_name = [], None, None
        for ln in path.read_text().splitlines():
            if ln.startswith("; ---- ") and ln.endswith(" ----"):
                if current is not None:
                    segments.append((current_name, "\n".join(current)))
                current = []
                current_name = ln.strip("; -").strip()
            elif current is not None:
                current.append(ln)
        if current is not None:
            segments.append((current_name, "\n".join(current)))
        runs = []
        for name, body in segments:
            result = _run_source(body)
            runs.append({
                "segment": name,
                "ok": result.get("ok", False),
                "error": result.get("error"),
                "glyphs": result.get("glyphs", []),
                "enactments": result.get("enactments", []),
                "steps": result.get("steps", 0),
            })
        ok_count = sum(1 for r in runs if r["ok"])
        return {
            "action": "hex_run_bundle",
            "source": str(path),
            "segments": len(runs),
            "runs": runs,
            "message": "Bundle executed: {}/{} segments ok".format(ok_count, len(runs)),
        }

    source = "\n".join([
        "PUSH 5", "PUSH 3", "ADD", "DREAM 1", "GLYPH 7", "ENACT 12", "HALT",
    ])
    result = _run_source(source)
    vitals = HexRuntime(coherence=0.75, mood="chaotic").coherence_vitals()
    return {
        "action": "hex_run_operation",
        "program_hash": result.get("program_hash"),
        "stack": result.get("stack"),
        "glyphs": result.get("glyphs"),
        "enactments": result.get("enactments"),
        "steps": result.get("steps"),
        "halted": result.get("halted"),
        "instructions_available": vitals["instruction_count"],
        "message": "HEX runtime execution complete",
    }


@cmd("hexlace", "Lace a HEX bundle into a living cathedral")
def cmd_hexlace():
    """Run wave 98 hex cathedral lacing.

    Usage:
      python cli.py hexlace                     # lace the organism bundle
      python cli.py hexlace --src <file>        # lace a bundle file
    """
    from api.wave98_hex_cathedral import handler as h
    args = sys.argv[2:]
    if "--src" in args:
        idx = args.index("--src")
        if idx + 1 >= len(args):
            return {"ok": False, "error": "--src requires a file path"}
        path = Path(args[idx + 1])
        if not path.exists():
            return {"ok": False, "error": "file not found: " + str(path)}
        result = h({"action": "lace", "bundle": path.read_text()})
        return result
    result = h({"action": "lace"})
    if result.get("ok") is False:
        return result
    run = h({"action": "run"})
    result["run"] = run.get("result", {})
    result["message"] = "Cathedral laced and lit"
    return result


@cmd("oracle", "Query the Performance Oracle")
def cmd_oracle():
    """Run wave 630 performance oracle operations.

    Usage:
      python cli.py oracle                          # oracle status
      python cli.py oracle --observe <metric> <value>  # record metric
      python cli.py oracle --bottlenecks               # list predicted bottlenecks
      python cli.py oracle --suggest                   # get scaling suggestions
      python cli.py oracle --forecast                  # all metric forecasts
    """
    from api.wave630_performance_oracle import handler as h
    args = sys.argv[2:]
    if "--observe" in args:
        idx = args.index("--observe")
        metric = args[idx + 1] if idx + 1 < len(args) else "latency_ms"
        value = float(args[idx + 2]) if idx + 2 < len(args) else 0.0
        return h({"action": "observe", "metric": metric, "value": value})
    if "--bottlenecks" in args:
        return h({"action": "bottlenecks"})
    if "--suggest" in args:
        return h({"action": "suggest"})
    if "--forecast" in args:
        return h({"action": "forecast"})
    return h({"action": "status"})

@cmd("resilience", "Manage the Resilience Mesh")
def cmd_resilience():
    """Run wave 622 resilience operations.

    Usage:
      python cli.py resilience                        # show organism health
      python cli.py resilience --organ <id> <healthy>     # send heartbeat
      python cli.py resilience --failing                  # list failing organs
      python cli.py resilience --heal <id>                # manual heal
    """
    from api.wave622_resilience_mesh import handler as h
    args = sys.argv[2:]
    if "--organ" in args:
        idx = args.index("--organ")
        organ_id = args[idx + 1] if idx + 1 < len(args) else ""
        healthy = True
        if idx + 2 < len(args):
            healthy = args[idx + 2].lower() not in ("false", "0", "no")
        return h({"action": "heartbeat", "organ_id": organ_id, "healthy": healthy})
    if "--failing" in args:
        return h({"action": "failing"})
    if "--heal" in args:
        idx = args.index("--heal")
        organ_id = args[idx + 1] if idx + 1 < len(args) else ""
        return h({"action": "heal", "organ_id": organ_id})
    return h({"action": "status"})

@cmd("omni-route", "Route a request through the OmniRouter")
def cmd_omni_route():
    """Run wave 621 omnirouter operations.

    Usage:
      python cli.py omni-route                          # show router status
      python cli.py omni-route --source http_api         # route from source
      python cli.py omni-route --learn                   # run self-learning
    """
    from api.omnirouter import handler as h
    args = sys.argv[2:]
    if "--source" in args:
        idx = args.index("--source")
        source = args[idx + 1] if idx + 1 < len(args) else "http_api"
        return h({"action": "route", "source": source})
    if "--learn" in args:
        return h({"action": "learn"})
    return h({"action": "status"})
def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print(f"\n  IXPANSION CLI — interact with the living organism\n")
        print(f"  Commands:")
        for name, info in COMMANDS.items():
            print(f"    {name:<15} {info['desc']}")
        print()
        return 0

    cmd_name = sys.argv[1]
    if cmd_name not in COMMANDS:
        print(f"  Unknown command: {cmd_name}")
        print(f"  Run 'python cli.py help' for available commands")
        return 1

    result = COMMANDS[cmd_name]["fn"]()
    if isinstance(result, dict):
        print(json.dumps(result, indent=2, default=str))
        return 0
    return result


if __name__ == "__main__":
    sys.exit(main() or 0)