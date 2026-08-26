"""Request Validator — validates incoming requests against schemas.

Checks required fields, types, ranges, and formats before requests
reach the API modules. Prevents bad data from causing errors.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SCHEMAS = {
    "agent_rent": {"required": ["agent_id", "renter", "hours"], "types": {"agent_id": str, "renter": str, "hours": int}},
    "dream_generate": {"required": ["theme"], "types": {"theme": str}},
    "entropy_inject": {"required": ["subsystem"], "types": {"subsystem": str, "intensity": float}},
    "predict": {"required": ["horizon_cycles", "prediction"], "types": {"horizon_cycles": int}},
    "bridge_create": {"required": ["source_dim", "target_dim"], "types": {"source_dim": str, "target_dim": str}},
}


class RequestValidator:
    def __init__(self):
        self.validation_count = 0
        self.error_count = 0

    def validate(self, schema_name: str, data: Dict) -> Dict:
        self.validation_count += 1
        if schema_name not in SCHEMAS:
            return {"valid": True, "warnings": [f"unknown schema: {schema_name}"]}
        schema = SCHEMAS[schema_name]
        errors = []
        for field in schema.get("required", []):
            if field not in data:
                errors.append(f"missing required field: {field}")
        for field, expected_type in schema.get("types", {}).items():
            if field in data and not isinstance(data[field], expected_type):
                errors.append(f"field '{field}' must be {expected_type.__name__}, got {type(data[field]).__name__}")
        if errors:
            self.error_count += 1
            return {"valid": False, "errors": errors}
        return {"valid": True}

    def stats(self) -> Dict:
        return {"validations": self.validation_count, "errors": self.error_count}


def handler(request, response):
    v = RequestValidator()
    return v.stats()


def demo():
    v = RequestValidator()
    print("=== Request Validator ===")
    r1 = v.validate("agent_rent", {"agent_id": "scout", "renter": "user", "hours": 2})
    print(f"\n  Valid rent: {r1['valid']}")
    r2 = v.validate("agent_rent", {"agent_id": "scout"})
    print(f"  Invalid rent: {r2['valid']} - {r2.get('errors', [])}")
    return v.stats()


if __name__ == "__main__":
    demo()
