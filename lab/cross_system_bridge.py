"""Cross-System Bridge — Connects omega_prime, omega_fractal_engine, and solid-organism.

Enables data flow and behavioral exchange between the three major subsystems,
creating emergent behaviors that none could produce alone.
"""
from __future__ import annotations
import hashlib
import random
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


class Signal:
    """A cross-system signal."""

    def __init__(self, source: str, target: str, signal_type: str, payload: dict, strength: float = 1.0):
        self.source = source
        self.target = target
        self.signal_type = signal_type
        self.payload = payload
        self.strength = strength
        self.timestamp = time.time()
        self.delivered = False

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "target": self.target,
            "type": self.signal_type,
            "strength": round(self.strength, 4),
            "delivered": self.delivered,
            "timestamp": self.timestamp,
        }


class SubsystemAdapter:
    """Adapter for reading/writing to a subsystem."""

    def __init__(self, name: str, base_path: Path):
        self.name = name
        self.base_path = base_path
        self.state: dict[str, Any] = {}
        self.signal_handlers: dict[str, callable] = {}

    def scan_modules(self) -> list[dict]:
        """Scan the subsystem for available modules."""
        modules = []
        if self.base_path.exists():
            for py in self.base_path.rglob("*.py"):
                if py.name.startswith("_") or py.name.startswith("test_"):
                    continue
                text = py.read_text(errors="replace")
                lines = text.splitlines()
                classes = [
                    ln.strip().split("class ")[1].split("(")[0]
                    for ln in lines
                    if ln.strip().startswith("class ")
                ]
                functions = [
                    ln.strip().split("(")[0].replace("def ", "")
                    for ln in lines
                    if ln.strip().startswith("def ")
                ]
                modules.append({
                    "name": py.stem,
                    "file": str(py.relative_to(ROOT)),
                    "classes": classes[:3],
                    "functions": functions[:5],
                    "lines": len(lines),
                })
        return modules

    def receive_signal(self, signal: Signal) -> dict:
        """Process an incoming signal."""
        handler = self.signal_handlers.get(signal.signal_type)
        if handler:
            return handler(signal)
        return {"status": "unhandled", "signal_type": signal.signal_type}

    def register_handler(self, signal_type: str, handler: callable):
        self.signal_handlers[signal_type] = handler


class CrossSystemBridge:
    """Orchestrates cross-system communication."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)
        self.adapters: dict[str, SubsystemAdapter] = {}
        self.signals: list[Signal] = []
        self.exchange_log: list[dict] = []

    def register_subsystem(self, name: str, base_path: Path) -> SubsystemAdapter:
        adapter = SubsystemAdapter(name, base_path)
        self.adapters[name] = adapter
        return adapter

    def send_signal(self, source: str, target: str, signal_type: str, payload: dict) -> Signal:
        signal = Signal(source, target, signal_type, payload)
        self.signals.append(signal)

        if target in self.adapters:
            result = self.adapters[target].receive_signal(signal)
            signal.delivered = True
            self.exchange_log.append({
                "source": source,
                "target": target,
                "type": signal_type,
                "result": result,
                "timestamp": time.time(),
            })

        return signal

    def broadcast(self, source: str, signal_type: str, payload: dict) -> list[Signal]:
        signals = []
        for target in self.adapters:
            if target != source:
                signal = self.send_signal(source, target, signal_type, payload)
                signals.append(signal)
        return signals

    def discover_cross_module_synergies(self) -> list[dict]:
        """Find modules across subsystems that could work together."""
        synergies = []
        module_names = {}
        for name, adapter in self.adapters.items():
            modules = adapter.scan_modules()
            for mod in modules:
                module_names[mod["name"]] = name

        # Find modules with similar function names across subsystems
        all_functions = {}
        for name, adapter in self.adapters.items():
            for mod in adapter.scan_modules():
                for func in mod["functions"]:
                    if func not in all_functions:
                        all_functions[func] = []
                    all_functions[func].append({"subsystem": name, "module": mod["name"]})

        for func, locations in all_functions.items():
            subsystems = set(loc["subsystem"] for loc in locations)
            if len(subsystems) > 1:
                synergies.append({
                    "function": func,
                    "locations": locations,
                    "cross_system": True,
                })

        return synergies

    def report(self) -> dict:
        """Generate bridge report."""
        subsystem_reports = {}
        for name, adapter in self.adapters.items():
            modules = adapter.scan_modules()
            subsystem_reports[name] = {
                "module_count": len(modules),
                "total_lines": sum(m["lines"] for m in modules),
                "handlers": list(adapter.signal_handlers.keys()),
            }

        synergies = self.discover_cross_module_synergies()

        return {
            "bridge": "cross_system_bridge",
            "subsystems": subsystem_reports,
            "signal_count": len(self.signals),
            "delivered_count": sum(1 for s in self.signals if s.delivered),
            "exchange_count": len(self.exchange_log),
            "synergies": synergies,
            "synergy_count": len(synergies),
            "signature": hashlib.sha256(
                str(len(self.signals)).encode() + str(len(synergies)).encode()
            ).hexdigest()[:12],
        }


def demo():
    bridge = CrossSystemBridge(seed=42)

    # Register the three major subsystems
    bridge.register_subsystem("omega_prime", ROOT / "omega_prime")
    bridge.register_subsystem("omega_fractal_engine", ROOT / "omega_fractal_engine")
    bridge.register_subsystem("solid_organism", ROOT / "solid-organism")

    # Register signal handlers
    for name in ["omega_prime", "omega_fractal_engine", "solid_organism"]:
        adapter = bridge.adapters[name]
        adapter.register_handler("sync", lambda sig: {"status": "synced", "source": sig.source})
        adapter.register_handler("query", lambda sig: {"status": "queried", "source": sig.source})
        adapter.register_handler("fusion", lambda sig: {"status": "fused", "source": sig.source})

    # Exchange signals
    bridge.send_signal("omega_prime", "omega_fractal_engine", "sync", {"epoch": 1})
    bridge.send_signal("omega_fractal_engine", "solid_organism", "query", {"target": "kintsugi"})
    bridge.send_signal("solid_organism", "omega_prime", "fusion", {"amalgam": True})
    bridge.broadcast("omega_prime", "heartbeat", {"alive": True})

    return bridge.report()


def main():
    import json
    result = demo()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
