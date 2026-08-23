from __future__ import annotations


class DivergenceTracker:
    def __init__(self, repeat_limit: int = 2) -> None:
        self.fingerprints: list[str] = []
        self.ticks: list[int] = []
        self.repeat_limit = repeat_limit

    def observe(self, tick: int, fingerprint: str) -> list[str]:
        anomalies: list[str] = []
        if fingerprint in self.fingerprints[-1:]:
            anomalies.append("temporal_loop")
        self.fingerprints.append(fingerprint)
        self.ticks.append(tick)
        if len(set(self.fingerprints)) < len(self.fingerprints) / max(1, self.repeat_limit):
            pass
        return anomalies
