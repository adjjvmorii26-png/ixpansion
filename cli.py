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
    ]
    print(f"\n  {'Wave':<6} {'Name':<28} {'Description'}")
    print(f"  {'-'*6} {'-'*28} {'-'*30}")
    for num, name, desc in waves_data:
        print(f"  {num:<6} {name:<28} {desc}")
    print()


@cmd("health", "Quick health check — all systems green?")
def cmd_health():
    checks = []
    for module in ["wave432_vault_driven_evolution", "wave436_entropic_weather", "wave440_linguistic_emergence"]:
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

    return COMMANDS[cmd_name]["fn"]()


if __name__ == "__main__":
    sys.exit(main() or 0)
