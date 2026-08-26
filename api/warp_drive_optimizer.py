"""Warp Drive Optimizer — subsystem performance optimization via warp physics.

Each subsystem has a "warp factor" (0-10). Users can charge warp
by allocating credits. Higher warp = faster processing but more
energy cost. The optimizer finds the sweet spot between speed and
efficiency across all subsystems.

Usage:
    POST /api/warp/set             — set warp factor for a subsystem
    POST /api/warp/optimize        — auto-optimize all subsystems
    GET  /api/warp/status          — view all warp factors
    GET  /api/warp/efficiency      — efficiency report
    POST /api/warp/emergency_stop  — emergency stop all warps
"""
from __future__ import annotations

import hashlib
import json
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SUBSYSTEMS = {
    "quantum_core": {"base_latency_ms": 100, "base_throughput": 1000, "max_warp": 10},
    "entropy_reactor": {"base_latency_ms": 200, "base_throughput": 500, "max_warp": 8},
    "agent_cortex": {"base_latency_ms": 50, "base_throughput": 2000, "max_warp": 10},
    "memory_palace": {"base_latency_ms": 150, "base_throughput": 800, "max_warp": 6},
    "dream_synthesis": {"base_latency_ms": 300, "base_throughput": 300, "max_warp": 7},
    "paradox_engine": {"base_latency_ms": 120, "base_throughput": 900, "max_warp": 9},
    "symbiosis_network": {"base_latency_ms": 80, "base_throughput": 1500, "max_warp": 8},
    "temporal_market": {"base_latency_ms": 60, "base_throughput": 3000, "max_warp": 10},
}


def _warp_metrics(warp: float, base_latency: float, base_throughput: float) -> Dict:
    """Compute performance metrics at given warp factor."""
    speed_multiplier = 2 ** (warp / 3)
    latency = round(base_latency / speed_multiplier, 2)
    throughput = round(base_throughput * speed_multiplier, 2)
    energy_cost = round(warp ** 2 * 0.1, 4)
    efficiency = round(throughput / max(energy_cost, 0.001), 2)
    return {
        "warp_factor": warp,
        "latency_ms": latency,
        "throughput": throughput,
        "energy_cost": energy_cost,
        "efficiency": efficiency,
    }


class WarpDriveOptimizer:
    def __init__(self):
        self.subsystem_warp: Dict[str, float] = {s: 1.0 for s in SUBSYSTEMS}
        self.history: List[Dict] = []
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "warp_drive.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            data = json.loads(path.read_text())
            self.subsystem_warp = data.get("warp", {s: 1.0 for s in SUBSYSTEMS})
            self.history = data.get("history", [])

    def _save(self):
        path = ROOT / ".runtime" / "warp_drive.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "warp": self.subsystem_warp,
            "history": self.history[-500:],
        }, indent=2))

    def set_warp(self, subsystem: str, warp: float) -> Dict:
        if subsystem not in SUBSYSTEMS:
            return {"error": f"unknown subsystem: {subsystem}"}
        max_w = SUBSYSTEMS[subsystem]["max_warp"]
        warp = max(0, min(warp, max_w))
        old = self.subsystem_warp.get(subsystem, 1.0)
        self.subsystem_warp[subsystem] = warp
        self.history.append({
            "subsystem": subsystem, "old": old, "new": warp,
            "timestamp": time.time(),
        })
        self._save()
        return {
            "subsystem": subsystem,
            "old_warp": old,
            "new_warp": warp,
            "max_warp": max_w,
            **_warp_metrics(warp, SUBSYSTEMS[subsystem]["base_latency_ms"],
                           SUBSYSTEMS[subsystem]["base_throughput"]),
        }

    def optimize(self) -> Dict:
        """Auto-optimize: find the warp factor that maximizes efficiency for each subsystem."""
        results = {}
        total_energy = 0
        for name, spec in SUBSYSTEMS.items():
            best_warp = 1.0
            best_eff = 0
            for w in [round(x * 0.5, 1) for x in range(2, spec["max_warp"] * 2 + 1)]:
                metrics = _warp_metrics(w, spec["base_latency_ms"], spec["base_throughput"])
                if metrics["efficiency"] > best_eff:
                    best_eff = metrics["efficiency"]
                    best_warp = w
            self.subsystem_warp[name] = best_warp
            total_energy += _warp_metrics(best_warp, spec["base_latency_ms"], spec["base_throughput"])["energy_cost"]
            results[name] = {"warp": best_warp, "efficiency": best_eff}
        self._save()
        return {"optimized": results, "total_energy": round(total_energy, 4)}

    def status(self) -> List[Dict]:
        result = []
        for name in SUBSYSTEMS:
            spec = SUBSYSTEMS[name]
            warp = self.subsystem_warp.get(name, 1.0)
            metrics = _warp_metrics(warp, spec["base_latency_ms"], spec["base_throughput"])
            result.append({"subsystem": name, **metrics})
        return result

    def efficiency_report(self) -> Dict:
        status = self.status()
        total_energy = sum(s["energy_cost"] for s in status)
        total_throughput = sum(s["throughput"] for s in status)
        avg_efficiency = sum(s["efficiency"] for s in status) / max(len(status), 1)
        return {
            "total_subsystems": len(status),
            "total_energy": round(total_energy, 4),
            "total_throughput": round(total_throughput, 2),
            "avg_efficiency": round(avg_efficiency, 2),
            "bottleneck": min(status, key=lambda s: s["throughput"])["subsystem"],
        }

    def emergency_stop(self) -> Dict:
        stopped = []
        for name in SUBSYSTEMS:
            old = self.subsystem_warp.get(name, 1.0)
            self.subsystem_warp[name] = 0.0
            stopped.append({"subsystem": name, "was": old})
        self.history.append({"event": "emergency_stop", "timestamp": time.time()})
        self._save()
        return {"stopped": stopped, "message": "All subsystems at warp 0"}


def handler(request, response):
    wd = WarpDriveOptimizer()
    return {"subsystems": list(SUBSYSTEMS.keys())}


def demo():
    wd = WarpDriveOptimizer()
    print("=== Warp Drive Optimizer ===")
    result = wd.set_warp("quantum_core", 5.0)
    print(f"\nQuantum Core: warp {result['old_warp']} -> {result['new_warp']}")
    print(f"  Latency: {result['latency_ms']}ms, Throughput: {result['throughput']}, Efficiency: {result['efficiency']}")

    opt = wd.optimize()
    print(f"\nOptimized. Total energy: {opt['total_energy']}")
    for name, info in list(opt["optimized"].items())[:3]:
        print(f"  {name}: warp={info['warp']}, efficiency={info['efficiency']}")

    report = wd.efficiency_report()
    print(f"\nEfficiency: avg={report['avg_efficiency']}, bottleneck={report['bottleneck']}")

    return report


if __name__ == "__main__":
    demo()
