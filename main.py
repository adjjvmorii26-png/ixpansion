"""IXpansion CLI — command-line interface for the entire platform.

Usage:
    python main.py status          — system status overview
    python main.py experiments     — list all experiments
    python main.py run <name>      — run an experiment
    python main.py agents          — list available agents
    python main.py rent <agent>    — rent an agent
    python main.py gateway         — gateway stats
    python main.py neural          — neural fabric stats
    python main.py dreams          — generate a dream
    python main.py entropy         — entropy auction
    python main.py serve           — start local dev server
"""
from __future__ import annotations

import sys
import os
import json
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)


def cmd_status():
    from api.telemetry import collect_telemetry
    from api.api_gateway import APIGateway
    from api.neural_fabric import NeuralFabric
    from api.event_stream import EventStream

    print("╔══════════════════════════════════════════════╗")
    print("║         IXPANSION — SYSTEM STATUS           ║")
    print("╚══════════════════════════════════════════════╝")
    print()

    gw = APIGateway()
    gw_stats = gw.get_stats()
    print(f"  API Gateway:     {gw_stats['modules']} modules, {gw_stats['total_routed']} requests routed")

    nf = NeuralFabric()
    nf_stats = nf.stats()
    print(f"  Neural Fabric:   {nf_stats['neurons']} neurons, {nf_stats['connections']} connections")

    es = EventStream()
    print(f"  Event Stream:    {len(es.subscriptions)} subscriptions, {len(es.events)} events")

    from api.quantum_entanglement import QuantumEntanglement
    qe = QuantumEntanglement()
    qe_stats = qe.stats()
    print(f"  Entanglement:    {qe_stats['entangled']} pairs, {qe_stats['total_measurements']} measurements")

    from api.plugin_loader import PluginLoader
    pl = PluginLoader()
    pl_stats = pl.health()
    print(f"  Plugins:         {pl_stats['loaded']} loaded, {pl_stats['registered']} registered")

    from api.memory_palace import MemoryPalace
    mp = MemoryPalace()
    print(f"  Memory Palaces:  {len(mp.palaces)} palaces")

    from api.speciation_engine import SpeciationEngine
    se = SpeciationEngine()
    print(f"  Species:         {len(se.species)} evolved")

    print()
    print(f"  Total API modules: 313")
    print(f"  Total routes:      320")
    print(f"  Total regions:     3 (iad1, sfo1, lhr1)")
    print()


def cmd_experiments():
    exp_dir = os.path.join(ROOT, "lab", "experiments")
    if not os.path.exists(exp_dir):
        print("No experiments directory found")
        return
    exps = sorted([os.path.splitext(f)[0] for f in os.listdir(exp_dir) if f.endswith(".py") and not f.startswith("_")])
    print(f"\n  {len(exps)} experiments available:\n")
    for i, exp in enumerate(exps, 1):
        print(f"    {i:3d}. {exp}")
    print()


def cmd_run(name: str):
    exp_path = os.path.join(ROOT, "lab", "experiments", f"{name}.py")
    if not os.path.exists(exp_path):
        print(f"  Experiment '{name}' not found. Use 'experiments' to list available.")
        return
    print(f"  Running {name}...")
    start = time.time()
    import subprocess
    result = subprocess.run(
        [sys.executable, exp_path],
        capture_output=True, text=True, timeout=30, cwd=ROOT
    )
    elapsed = time.time() - start
    if result.stdout:
        print(result.stdout)
    if result.returncode != 0 and result.stderr:
        print(f"  Error: {result.stderr[:200]}")
    print(f"  Completed in {elapsed:.2f}s")


def cmd_agents():
    from api.agent_rental import AGENT_CATALOG
    print("\n  Available Agents:\n")
    for agent in AGENT_CATALOG:
        avail = "●" if agent["availability"] != "unavailable" else "○"
        print(f"    {avail} {agent['name']:<20} ${agent['hourly_rate_usd']:.2f}/hr  ★{agent['rating']}")
        print(f"      {agent['description'][:60]}")
    print()


def cmd_rent(agent_id: str):
    from api.agent_rental import AgentRentalSystem
    sys_ = AgentRentalSystem()
    result = sys_.rent(agent_id, "cli_user", 1)
    if "error" in result:
        print(f"  Error: {result['error']}")
    else:
        print(f"  Rented {result['agent']} for 1 hour — ${result['total_cost']}")
        print(f"  Rental ID: {result['rental_id']}")
    print()


def cmd_gateway():
    from api.api_gateway import APIGateway
    gw = APIGateway()
    stats = gw.get_stats()
    print(f"\n  Gateway Stats:")
    print(f"    Modules:      {stats['modules']}")
    print(f"    Routed:       {stats['total_routed']}")
    print(f"    Cache hits:   {stats['cached_hits']}")
    print(f"    Circuits:     {stats['open_circuits']} open")
    print()


def cmd_neural():
    from api.neural_fabric import NeuralFabric
    nf = NeuralFabric()
    stats = nf.stats()
    print(f"\n  Neural Fabric:")
    print(f"    Neurons:      {stats['neurons']}")
    print(f"    Connections:  {stats['connections']}")
    print(f"    Density:      {stats['density']}")
    print(f"    Firings:      {stats['total_firings']}")
    print()


def cmd_dreams():
    from api.dream_synthesis import DreamSynthesis
    from api.dream_interpreter import DreamInterpreter
    ds = DreamSynthesis()
    di = DreamInterpreter()
    dream = ds.generate("cli_user")
    print(f"\n  {dream['title']}")
    print(f"  Mood: {dream['mood']}, Coherence: {dream['coherence']}")
    print(f"\n  \"{dream['narrative']}\"\n")
    interp = di.analyze(dream)
    print(f"  Insights: {len(interp['insights'])}")
    for insight in interp["insights"][:3]:
        print(f"    [{insight['type']}] {insight['message']}")
    print()


def cmd_entropy():
    from api.entropy_auction import EntropyAuction
    ea = EntropyAuction()
    active = ea.list_active()
    print(f"\n  Active auctions: {len(active)}")
    for auc in active[:5]:
        print(f"    {auc['subsystem']}: {len(auc.get('bids', []))} bids")
    print()


def cmd_serve():
    print("  Starting IXpansion dev server on http://localhost:3000")
    print("  Dashboard: http://localhost:3000/dashboard/")
    print("  API docs:  http://localhost:3000/docs.py")
    print()
    import http.server
    import functools

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=ROOT, **kwargs)

    server = http.server.HTTPServer(("0.0.0.0", 3000), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")


COMMANDS = {
    "status": cmd_status,
    "experiments": cmd_experiments,
    "agents": cmd_agents,
    "gateway": cmd_gateway,
    "neural": cmd_neural,
    "dreams": cmd_dreams,
    "entropy": cmd_entropy,
    "serve": cmd_serve,
}

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)

    cmd = args[0]
    if cmd == "run" and len(args) > 1:
        cmd_run(args[1])
    elif cmd == "rent" and len(args) > 1:
        cmd_rent(args[1])
    elif cmd in COMMANDS:
        COMMANDS[cmd]()
    else:
        print(f"  Unknown command: {cmd}")
        print(f"  Available: {', '.join(COMMANDS.keys())}, run <name>, rent <agent>")
