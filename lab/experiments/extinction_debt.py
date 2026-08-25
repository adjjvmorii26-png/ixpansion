from __future__ import annotations
"""Extinction Debt — predicts which modules are doomed based on trends.

Like extinction debt in ecology where species are doomed but haven't
died yet, some modules are on a trajectory to failure. This module
analyzes trends and predicts which modules will become extinct.
"""
import math
import json
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class ModuleTrend:
    name: str
    health_history: List[float]
    dependency_count: int = 0
    last_activity: int = 0
    predicted_extinction_tick: int = -1
    debt_status: str = "healthy"

class ExtinctionDebtAnalyzer:
    def __init__(self):
        self.trends: Dict[str, ModuleTrend] = {}

    def register(self, name: str, health_history: List[float],
                 dependency_count: int = 0, last_activity: int = 0):
        trend = ModuleTrend(
            name=name, health_history=health_history,
            dependency_count=dependency_count, last_activity=last_activity,
        )
        self.trends[name] = trend

    def analyze(self, current_tick: int = 100):
        for name, trend in self.trends.items():
            if len(trend.health_history) < 3:
                trend.debt_status = "insufficient_data"
                continue
            recent = trend.health_history[-5:]
            slope = (recent[-1] - recent[0]) / max(len(recent) - 1, 1)
            current_health = trend.health_history[-1]

            if current_health <= 0:
                trend.debt_status = "extinct"
                trend.predicted_extinction_tick = current_tick
            elif slope < -0.05 and current_health < 0.3:
                ticks_to_zero = current_health / abs(slope) if slope != 0 else 999
                trend.predicted_extinction_tick = current_tick + int(ticks_to_zero)
                trend.debt_status = "doomed"
            elif slope < -0.02:
                trend.debt_status = "declining"
                trend.predicted_extinction_tick = current_tick + int(current_health / abs(slope)) if slope != 0 else -1
            elif current_health > 0.7:
                trend.debt_status = "thriving"
            else:
                trend.debt_status = "stable"

    def endangered(self) -> List[Dict]:
        return sorted([
            {"name": t.name, "status": t.debt_status,
             "health": t.health_history[-1] if t.health_history else 0,
             "extinction_tick": t.predicted_extinction_tick}
            for t in self.trends.values()
            if t.debt_status in ("doomed", "declining", "extinct")
        ], key=lambda x: x["extinction_tick"])

    def report(self) -> Dict:
        self.analyze(100)
        statuses = {}
        for t in self.trends.values():
            statuses[t.debt_status] = statuses.get(t.debt_status, 0) + 1
        return {"total": len(self.trends), "statuses": statuses,
                "endangered": self.endangered()}


def demo():
    analyzer = ExtinctionDebtAnalyzer()
    print("=== Extinction Debt Analyzer ===")
    analyzer.register("healthy_mod", [0.9, 0.85, 0.88, 0.9, 0.87], 5, 95)
    analyzer.register("doomed_mod", [0.8, 0.6, 0.4, 0.2, 0.05], 2, 30)
    analyzer.register("declining_mod", [0.7, 0.65, 0.6, 0.55, 0.5], 3, 60)
    analyzer.register("stable_mod", [0.5, 0.5, 0.5, 0.5, 0.5], 4, 80)
    report = analyzer.report()
    print(f"  Total modules: {report['total']}")
    print(f"  Statuses: {report['statuses']}")
    print(f"  Endangered:")
    for e in report["endangered"]:
        print(f"    {e['name']}: {e['status']} (health={e['health']:.2f}, "
              f"extinction_tick={e['extinction_tick']})")
    return report


if __name__ == "__main__":
    demo()
