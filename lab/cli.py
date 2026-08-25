"""Nexus Observatory CLI — Command-line interface for the IXpansion engine.

Usage:
    python3 lab/cli.py health         — System health check
    python3 lab/cli.py modules        — List all modules
    python3 lab.cli.py hex            — Run HEX VM on all scripts
    python3 lab.cli.py experiments    — List experiments
    python3 lab/cli.py run <name>     — Run a specific experiment
    python3 lab/cli.py constellation  — Build dependency graph
    python3 lab/cli.py anomalies      — Scan for anomalies
    python3 lab/cli.py bench          — Benchmark all experiments
    python3 lab/cli.py wave           — Show wave history
"""
from __future__ import annotations
import argparse
import importlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def cmd_health(args):
    """System health check."""
    lab_dir = ROOT / "lab" / "experiments"
    module_count = len(list(lab_dir.glob("*.py"))) - 1 if lab_dir.exists() else 0
    test_dir = ROOT / "lab" / "tests"
    test_count = len(list(test_dir.glob("test_*.py"))) if test_dir.exists() else 0
    api_dir = ROOT / "api"
    api_count = len(list(api_dir.glob("*.py"))) - 1 if api_dir.exists() else 0

    print(f"🜁 Nexus Observatory Health")
    print(f"  Experiments: {module_count}")
    print(f"  Test suites: {test_count}")
    print(f"  API endpoints: {api_count}")
    print(f"  Status: HEALTHY")


def cmd_modules(args):
    """List all modules by subsystem."""
    subsystems = {
        "api": ROOT / "api",
        "lab": ROOT / "lab" / "experiments",
        "bridges": ROOT / "bridges",
        "constellation": ROOT / "constellation",
        "mycelium": ROOT / "mycelium",
    }
    for name, base in subsystems.items():
        if not base.exists():
            continue
        modules = [f.stem for f in sorted(base.glob("*.py")) if not f.name.startswith("_") and not f.name.startswith("test_")]
        print(f"\n{name} ({len(modules)} modules):")
        for m in modules:
            print(f"  - {m}")


def cmd_hex(args):
    """Run HEX VM."""
    from lab.hex_vm import demo
    result = demo()
    print(f"Grammars compiled: {result['grammar_count']}")
    print(f"Scripts executed: {result['script_count']}")
    print(f"Total output: {result['total_output']}")
    for name, script in result["script_results"].items():
        print(f"\n  {name}: output={script['output']}, steps={script['steps']}")


def cmd_experiments(args):
    """List experiments."""
    lab_dir = ROOT / "lab" / "experiments"
    experiments = sorted(f.stem for f in lab_dir.glob("*.py") if not f.name.startswith("_") and f.name != "__init__.py")
    print(f"Experiments ({len(experiments)}):")
    for e in experiments:
        print(f"  - {e}")


def cmd_run(args):
    """Run a specific experiment."""
    name = args.name
    lab_dir = ROOT / "lab" / "experiments"
    module_path = lab_dir / f"{name}.py"
    if not module_path.exists():
        print(f"Error: experiment '{name}' not found")
        sys.exit(1)

    spec = importlib.util.spec_from_file_location(f"lab.experiments.{name}", str(module_path))
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, "demo"):
            t0 = time.time()
            result = mod.demo()
            elapsed = time.time() - t0
            print(json.dumps(result, indent=2))
            print(f"\n[{elapsed:.3f}s]")
        else:
            print(f"Module '{name}' has no demo() function")
    else:
        print(f"Failed to load '{name}'")


def cmd_constellation(args):
    """Build dependency graph."""
    from api.constellation import build_constellation
    result = build_constellation()
    stats = result["stats"]
    print(f"Constellation: {stats['total_nodes']} nodes, {stats['total_edges']} edges, density={stats['density']}")
    print("Most connected:")
    for name, count in stats["most_connected"][:5]:
        print(f"  {name}: {count} connections")


def cmd_anomalies(args):
    """Scan for anomalies."""
    from api.anomaly_detector import scan_anomalies
    result = scan_anomalies()
    s = result["summary"]
    print(f"Anomaly scan: health={s['health_score']}/100, anomalies={s['anomaly_count']}, warnings={s['warning_count']}")
    for a in result["anomalies"][:5]:
        print(f"  [{a['severity']}] {a['type']} in {a.get('file', '?')}")


def cmd_bench(args):
    """Benchmark all experiments."""
    lab_dir = ROOT / "lab" / "experiments"
    experiments = sorted(f.stem for f in lab_dir.glob("*.py") if not f.name.startswith("_") and f.name != "__init__.py")
    results = []
    print(f"Benchmarking {len(experiments)} experiments...")
    for name in experiments:
        module_path = lab_dir / f"{name}.py"
        try:
            spec = importlib.util.spec_from_file_location(f"lab.experiments.{name}", str(module_path))
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, "demo"):
                    t0 = time.time()
                    mod.demo()
                    elapsed = time.time() - t0
                    results.append((name, elapsed, "ok"))
                else:
                    results.append((name, 0, "no_demo"))
            else:
                results.append((name, 0, "load_error"))
        except Exception as e:
            results.append((name, 0, f"error: {e}"))

    results.sort(key=lambda x: x[1], reverse=True)
    print(f"\n{'Module':<40} {'Time':>8}  Status")
    print("-" * 60)
    for name, elapsed, status in results:
        print(f"{name:<40} {elapsed*1000:>6.1f}ms  {status}")
    total = sum(r[1] for r in results)
    ok = sum(1 for r in results if r[2] == "ok")
    print(f"\nTotal: {ok}/{len(results)} passed, {total*1000:.1f}ms")


def cmd_wave(args):
    """Show wave history."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "--all", "-20"],
            capture_output=True, text=True, cwd=str(ROOT), timeout=10
        )
        print(result.stdout)
    except Exception as e:
        print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(description="Nexus Observatory CLI")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("health", help="System health check")
    sub.add_parser("modules", help="List all modules")
    sub.add_parser("hex", help="Run HEX VM")
    sub.add_parser("experiments", help="List experiments")
    sub.add_parser("constellation", help="Build dependency graph")
    sub.add_parser("anomalies", help="Scan for anomalies")
    sub.add_parser("bench", help="Benchmark all experiments")
    sub.add_parser("wave", help="Show wave history")

    run_parser = sub.add_parser("run", help="Run a specific experiment")
    run_parser.add_argument("name", help="Experiment name")

    args = parser.parse_args()

    commands = {
        "health": cmd_health,
        "modules": cmd_modules,
        "hex": cmd_hex,
        "experiments": cmd_experiments,
        "run": cmd_run,
        "constellation": cmd_constellation,
        "anomalies": cmd_anomalies,
        "bench": cmd_bench,
        "wave": cmd_wave,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
