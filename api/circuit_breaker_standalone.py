"""Circuit Breaker — standalone fault tolerance module.

Prevents cascading failures by tracking error rates per service.
Opens the circuit when errors exceed threshold, allows periodic
half-open probes, and closes when service recovers.
"""
from __future__ import annotations

import json
import time
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.circuits: Dict[str, Dict] = {}

    def _get_circuit(self, service: str) -> Dict:
        if service not in self.circuits:
            self.circuits[service] = {
                "state": "closed", "failures": 0,
                "last_failure": 0, "last_success": time.time(),
                "trips": 0,
            }
        return self.circuits[service]

    def record_success(self, service: str) -> Dict:
        circuit = self._get_circuit(service)
        circuit["failures"] = 0
        circuit["last_success"] = time.time()
        if circuit["state"] == "half_open":
            circuit["state"] = "closed"
        return {"service": service, "state": circuit["state"]}

    def record_failure(self, service: str) -> Dict:
        circuit = self._get_circuit(service)
        circuit["failures"] += 1
        circuit["last_failure"] = time.time()
        if circuit["failures"] >= self.failure_threshold:
            circuit["state"] = "open"
            circuit["trips"] += 1
        return {"service": service, "state": circuit["state"], "failures": circuit["failures"]}

    def allow_request(self, service: str) -> Dict:
        circuit = self._get_circuit(service)
        if circuit["state"] == "closed":
            return {"allowed": True, "state": "closed"}
        if circuit["state"] == "open":
            if time.time() - circuit["last_failure"] > self.recovery_timeout:
                circuit["state"] = "half_open"
                return {"allowed": True, "state": "half_open"}
            return {"allowed": False, "state": "open"}
        return {"allowed": True, "state": "half_open"}

    def status(self, service: str = None) -> Dict:
        if service:
            return self._get_circuit(service)
        return {s: c["state"] for s, c in self.circuits.items()}


def handler(request, response):
    cb = CircuitBreaker()
    return cb.status()


def demo():
    cb = CircuitBreaker(failure_threshold=3)
    print("=== Circuit Breaker ===")
    for i in range(4):
        result = cb.record_failure("api_service")
        print(f"  Failure {i+1}: state={result['state']}, failures={result['failures']}")
    allowed = cb.allow_request("api_service")
    print(f"  Allow request: {allowed['allowed']} (state: {allowed['state']})")
    cb.record_success("api_service")
    print(f"  After success: {cb.status('api_service')['state']}")
    return cb.status()


if __name__ == "__main__":
    demo()
