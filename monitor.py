#!/usr/bin/env python3
"""IXPANSION Monitoring — health checks, alerts, and system status.

Usage:
    python monitor.py             # full health report
    python monitor.py --quick     # quick check (exit code only)
    python monitor.py --json      # JSON output
    python monitor.py --watch 5   # watch mode (refresh every 5s)
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Callable

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


@dataclass
class HealthCheck:
    name: str
    status: str = "unknown"
    latency_ms: float = 0.0
    error: str = ""
    details: dict = field(default_factory=dict)
    passed: bool = False


class OrganismMonitor:
    """Monitors the health of all organism subsystems."""

    def __init__(self):
        self.checks: list[HealthCheck] = []
        self.overall_healthy = True
        self.timestamp = time.time()

    def _run_check(self, name: str, fn: Callable) -> HealthCheck:
        check = HealthCheck(name=name)
        t0 = time.time()
        try:
            result = fn()
            check.latency_ms = (time.time() - t0) * 1000
            check.status = result.get("status", "ok")
            check.details = result
            check.passed = True
        except Exception as e:
            check.latency_ms = (time.time() - t0) * 1000
            check.status = "error"
            check.error = str(e)
            check.passed = False
            self.overall_healthy = False
        return check

    def _import_handler(self, module: str):
        mod = __import__(f"api.{module}", fromlist=["handler"])
        return mod.handler

    def check_wave(self, module: str, action: str = "status") -> HealthCheck:
        def fn():
            handler = self._import_handler(module)
            return handler({"action": action})
        return self._run_check(module, fn)

    def check_python_env(self) -> HealthCheck:
        def fn():
            import sys
            return {"status": "ok", "python": sys.version, "version": sys.version_info[:2]}
        return self._run_check("python_env", fn)

    def check_test_suite(self) -> HealthCheck:
        def fn():
            import subprocess
            r = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/test_wave432.py", "tests/test_wave440.py", "-q", "--tb=no"],
                capture_output=True, text=True, timeout=30
            )
            passed = r.returncode == 0
            return {"status": "ok" if passed else "fail", "output": r.stdout.strip().split("\n")[-1] if r.stdout else ""}
        return self._run_check("test_suite", fn)

    def check_git_status(self) -> HealthCheck:
        def fn():
            import subprocess
            r = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, timeout=5)
            dirty = len(r.stdout.strip().split("\n")) if r.stdout.strip() else 0
            r2 = subprocess.run(["git", "log", "--oneline", "-1"], capture_output=True, text=True, timeout=5)
            commit = r2.stdout.strip().split()[0] if r2.stdout else "unknown"
            return {"status": "ok", "dirty_files": dirty, "last_commit": commit}
        return self._run_check("git_status", fn)

    def run_all_checks(self) -> dict:
        self.checks = []
        self.overall_healthy = True
        self.timestamp = time.time()

        # Core checks
        self.checks.append(self.check_python_env())
        self.checks.append(self.check_git_status())
        self.checks.append(self.check_test_suite())

        # Wave checks
        wave_modules = [
            "wave432_vault_driven_evolution",
            "wave433_consciousness_experiments",
            "wave434_fusion_organism",
            "wave435_resonance_cartography",
            "wave436_entropic_weather",
            "wave437_paradox_genome",
            "wave438_semantic_loom",
            "wave439_echo_stratigraphy",
            "wave440_linguistic_emergence",
        ]
        for module in wave_modules:
            self.checks.append(self.check_wave(module))

        passed = sum(1 for c in self.checks if c.passed)
        total = len(self.checks)
        avg_latency = sum(c.latency_ms for c in self.checks) / max(1, total)

        return {
            "overall": "HEALTHY" if self.overall_healthy else "DEGRADED",
            "timestamp": self.timestamp,
            "checks_passed": passed,
            "checks_total": total,
            "avg_latency_ms": round(avg_latency, 1),
            "checks": [
                {
                    "name": c.name,
                    "status": c.status,
                    "latency_ms": round(c.latency_ms, 1),
                    "passed": c.passed,
                    "error": c.error or None,
                }
                for c in self.checks
            ],
        }

    def print_report(self, result: dict):
        icon = "🟢" if result["overall"] == "HEALTHY" else "🔴"
        print(f"\n{icon} IXPANSION Organism Monitor — {result['overall']}")
        print(f"   {result['checks_passed']}/{result['checks_total']} checks passed")
        print(f"   Avg latency: {result['avg_latency_ms']}ms")
        print(f"   {'─'*50}")
        for check in result["checks"]:
            icon = "✓" if check["passed"] else "✗"
            latency = f"{check['latency_ms']}ms"
            error = f" — {check['error']}" if check["error"] else ""
            print(f"   {icon} {check['name']:<40} {latency:>8}{error}")
        print(f"{'─'*50}\n")


def main():
    monitor = OrganismMonitor()
    args = sys.argv[1:]

    if "--quick" in args:
        result = monitor.run_all_checks()
        sys.exit(0 if result["overall"] == "HEALTHY" else 1)

    if "--json" in args:
        result = monitor.run_all_checks()
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["overall"] == "HEALTHY" else 1)

    if "--watch" in args:
        idx = args.index("--watch")
        interval = int(args[idx + 1]) if idx + 1 < len(args) else 5
        try:
            while True:
                result = monitor.run_all_checks()
                monitor.print_report(result)
                time.sleep(interval)
        except KeyboardInterrupt:
            pass
        return

    result = monitor.run_all_checks()
    monitor.print_report(result)
    sys.exit(0 if result["overall"] == "HEALTHY" else 1)


if __name__ == "__main__":
    main()
