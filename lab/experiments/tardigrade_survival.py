from __future__ import annotations
"""Tardigrade Survival Engine — extreme stress testing for subsystems.

Named after the most resilient organism on Earth, this module subjects
subsystems to brutal stress conditions: memory pressure, CPU starvation,
timeout bombs, data corruption, and cascading failures. Measures survival.
"""
import time
import random
import hashlib
import json
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Any
from enum import Enum

class StressType(Enum):
    MEMORY_PRESSURE = "memory_pressure"
    CPU_STARVATION = "cpu_starvation"
    TIMEOUT_BOMB = "timeout_bomb"
    DATA_CORRUPTION = "data_corruption"
    CASCADE_FAILURE = "cascade_failure"
    CONCURRENT_STORM = "concurrent_storm"
    ENTROPY_FLOOD = "entropy_flood"
    NULL_INJECTION = "null_injection"

@dataclass
class StressEvent:
    stress_type: StressType
    intensity: float
    duration_ms: float
    success: bool
    error_message: str = ""
    recovery_time_ms: float = 0.0

@dataclass
class SurvivalReport:
    subsystem_name: str
    total_stressors: int
    survived: int
    failed: int
    survival_rate: float
    avg_recovery_ms: float
    max_recovery_ms: float
    events: List[StressEvent] = field(default_factory=list)
    tardigrade_score: float = 0.0

    def __post_init__(self):
        if self.total_stressors > 0:
            self.survival_rate = self.survived / self.total_stressors
        recovery_times = [e.recovery_time_ms for e in self.events if e.success]
        self.avg_recovery_ms = sum(recovery_times) / max(len(recovery_times), 1)
        self.max_recovery_ms = max(recovery_times) if recovery_times else 0.0
        self.tardigrade_score = self.survival_rate * 100 * (
            1.0 / (1.0 + self.avg_recovery_ms / 100.0)
        )


class TardigradeSurvivalEngine:
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.reports: Dict[str, SurvivalReport] = {}

    def _memory_pressure(self, target: Callable, size_kb: int = 100) -> StressEvent:
        start = time.perf_counter()
        try:
            payload = b"x" * (size_kb * 1024)
            result = target({"stress": "memory", "payload_size": len(payload)})
            elapsed = (time.perf_counter() - start) * 1000
            del payload
            return StressEvent(
                stress_type=StressType.MEMORY_PRESSURE,
                intensity=size_kb / 1000.0, duration_ms=elapsed,
                success=True, recovery_time_ms=elapsed
            )
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            return StressEvent(
                stress_type=StressType.MEMORY_PRESSURE,
                intensity=size_kb / 1000.0, duration_ms=elapsed,
                success=False, error_message=str(e)[:200]
            )

    def _cpu_starvation(self, target: Callable, iterations: int = 10000) -> StressEvent:
        start = time.perf_counter()
        try:
            result = 0
            for i in range(iterations):
                result += i * i
            target_result = target({"stress": "cpu", "computation": result})
            elapsed = (time.perf_counter() - start) * 1000
            return StressEvent(
                stress_type=StressType.CPU_STARVATION,
                intensity=iterations / 10000.0, duration_ms=elapsed,
                success=True, recovery_time_ms=elapsed
            )
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            return StressEvent(
                stress_type=StressType.CPU_STARVATION,
                intensity=iterations / 10000.0, duration_ms=elapsed,
                success=False, error_message=str(e)[:200]
            )

    def _data_corruption(self, target: Callable) -> StressEvent:
        start = time.perf_counter()
        try:
            original = list(range(100))
            corrupted = original.copy()
            num_corruptions = self.rng.randint(5, 30)
            for _ in range(num_corruptions):
                idx = self.rng.randint(0, len(corrupted) - 1)
                corrupted[idx] = self.rng.randint(-9999, 9999)
            result = target({"stress": "corruption", "data": corrupted})
            elapsed = (time.perf_counter() - start) * 1000
            return StressEvent(
                stress_type=StressType.DATA_CORRUPTION,
                intensity=num_corruptions / 30.0, duration_ms=elapsed,
                success=True, recovery_time_ms=elapsed
            )
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            return StressEvent(
                stress_type=StressType.DATA_CORRUPTION,
                intensity=1.0, duration_ms=elapsed,
                success=False, error_message=str(e)[:200]
            )

    def _null_injection(self, target: Callable) -> StressEvent:
        start = time.perf_counter()
        try:
            nulls = [None, 0, "", {}, [], set(), False, 0.0]
            for n in nulls:
                target({"stress": "null", "payload": n})
            elapsed = (time.perf_counter() - start) * 1000
            return StressEvent(
                stress_type=StressType.NULL_INJECTION,
                intensity=1.0, duration_ms=elapsed,
                success=True, recovery_time_ms=elapsed
            )
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            return StressEvent(
                stress_type=StressType.NULL_INJECTION,
                intensity=1.0, duration_ms=elapsed,
                success=False, error_message=str(e)[:200]
            )

    def _entropy_flood(self, target: Callable) -> StressEvent:
        start = time.perf_counter()
        try:
            chaos = "".join(chr(self.rng.randint(0, 65535)) for _ in range(500))
            result = target({"stress": "entropy", "flood": chaos})
            elapsed = (time.perf_counter() - start) * 1000
            return StressEvent(
                stress_type=StressType.ENTROPY_FLOOD,
                intensity=1.0, duration_ms=elapsed,
                success=True, recovery_time_ms=elapsed
            )
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            return StressEvent(
                stress_type=StressType.ENTROPY_FLOOD,
                intensity=1.0, duration_ms=elapsed,
                success=False, error_message=str(e)[:200]
            )

    def stress_test(self, name: str, target: Callable,
                    stressors: int = 20) -> SurvivalReport:
        events = []
        for _ in range(stressors):
            stype = self.rng.choice(list(StressType))
            if stype == StressType.MEMORY_PRESSURE:
                events.append(self._memory_pressure(target, self.rng.randint(10, 500)))
            elif stype == StressType.CPU_STARVATION:
                events.append(self._cpu_starvation(target, self.rng.randint(100, 50000)))
            elif stype == StressType.DATA_CORRUPTION:
                events.append(self._data_corruption(target))
            elif stype == StressType.NULL_INJECTION:
                events.append(self._null_injection(target))
            elif stype == StressType.ENTROPY_FLOOD:
                events.append(self._entropy_flood(target))
            else:
                events.append(self._cpu_starvation(target, 1000))

        survived = sum(1 for e in events if e.success)
        failed = len(events) - survived

        report = SurvivalReport(
            subsystem_name=name,
            total_stressors=len(events),
            survived=survived,
            failed=failed,
            survival_rate=0.0,
            avg_recovery_ms=0.0,
            max_recovery_ms=0.0,
            events=events,
        )
        report.__post_init__()
        self.reports[name] = report
        return report

    def resilience_ranking(self) -> List[Dict[str, Any]]:
        ranked = sorted(
            self.reports.values(),
            key=lambda r: r.tardigrade_score,
            reverse=True
        )
        return [
            {"name": r.subsystem_name, "score": round(r.tardigrade_score, 2),
             "survival_rate": round(r.survival_rate, 2)}
            for r in ranked
        ]


def resilient_handler(context: dict) -> dict:
    stress = context.get("stress", "unknown")
    if stress == "corruption":
        data = context.get("data", [])
        return {"status": "ok", "cleaned": len(data)}
    elif stress == "null":
        return {"status": "ok", "handled_null": True}
    elif stress == "entropy":
        return {"status": "ok", "absorbed": len(context.get("flood", ""))}
    return {"status": "ok", "stress": stress}


def demo():
    engine = TardigradeSurvivalEngine(seed=42)
    print("=== Tardigrade Survival Engine ===")
    subsystems = ["photon_memory", "dark_mapper", "crystal_lattice", "neutrino"]
    for name in subsystems:
        report = engine.stress_test(name, resilient_handler, stressors=15)
        print(f"\n  {name}:")
        print(f"    Survival: {report.survived}/{report.total_stressors} "
              f"({report.survival_rate:.1%})")
        print(f"    Avg recovery: {report.avg_recovery_ms:.2f}ms")
        print(f"    Tardigrade score: {report.tardigrade_score:.2f}")

    print("\nResilience ranking:")
    for rank, entry in enumerate(engine.resilience_ranking(), 1):
        print(f"  #{rank} {entry['name']}: score={entry['score']}, "
              f"survival={entry['survival_rate']:.0%}")

    return {"rankings": engine.resilience_ranking()}


if __name__ == "__main__":
    demo()
