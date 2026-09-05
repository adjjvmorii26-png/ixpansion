"""Reality Distortion Field — locally alters system behavior rules.

Creates zones where normal system rules are bent or broken.
Within a distortion field, prices may be negative, agents may
ignore permissions, and entropy flows backwards.
"""
from __future__ import annotations

import hashlib
import json
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class RealityDistortion:
    def __init__(self):
        self.fields: Dict[str, Dict] = {}
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "distortion.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            self.fields = json.loads(path.read_text()).get("fields", {})

    def _save(self):
        path = ROOT / ".runtime" / "distortion.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"fields": self.fields}, indent=2))

    def create(self, name: str, intensity: float = 0.5, rules_bent: List[str] = None) -> Dict:
        field_id = hashlib.sha256(f"{name}:{time.time()}".encode()).hexdigest()[:10]
        rules_bent = rules_bent or random.sample(["physics", "time", "causality", "identity", "entropy"], 2)
        self.fields[field_id] = {
            "name": name, "intensity": min(1.0, max(0.0, intensity)),
            "rules_bent": rules_bent, "active": True,
            "created": time.time(), "distortions_applied": 0,
        }
        self._save()
        return {"field_id": field_id, "name": name, "intensity": intensity, "rules_bent": rules_bent}

    def distort(self, field_id: str, target: str, value: float) -> Dict:
        if field_id not in self.fields:
            return {"error": "field not found"}
        field = self.fields[field_id]
        if not field["active"]:
            return {"error": "field is inactive"}
        distortion_factor = field["intensity"] * random.uniform(0.5, 1.5)
        distorted = round(value * (1 + distortion_factor * random.choice([-1, 1])), 4)
        field["distortions_applied"] += 1
        self._save()
        return {
            "target": target, "original": value,
            "distorted": distorted, "factor": round(distortion_factor, 4),
            "field": field["name"],
        }

    def deactivate(self, field_id: str) -> Dict:
        if field_id not in self.fields:
            return {"error": "field not found"}
        self.fields[field_id]["active"] = False
        self._save()
        return {"field_id": field_id, "status": "deactivated"}

    def list_fields(self) -> List[Dict]:
        return [{"id": k, **v} for k, v in self.fields.items()]


def handler(request, response):
    rd = RealityDistortion()
    return {"active_fields": sum(1 for f in rd.fields.values() if f.get("active"))}


def demo():
    rd = RealityDistortion()
    print("=== Reality Distortion Field ===")
    field = rd.create("Chaos Zone", intensity=0.7, rules_bent=["physics", "entropy"])
    print(f"\nCreated: {field['name']} (intensity: {field['intensity']})")
    print(f"  Rules bent: {field['rules_bent']}")
    for target, value in [("price", 10.0), ("entropy", 0.5), ("agent_trust", 0.8)]:
        result = rd.distort(field["field_id"], target, value)
        print(f"  {target}: {result['original']} -> {result['distorted']} (factor: {result['factor']})")
    return handler({}, {})


if __name__ == "__main__":
    demo()

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "agent", "status": "active", "wave": "0", "module": "reality_distortion"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
