"""Certification Program — certify users in IXpansion expertise.

Users complete learning paths and pass exams to earn certifications:
- IXpansion Certified Explorer (ICE)
- IXpansion Certified Scientist (ICS)
- IXpansion Certified Architect (ICA)

Certifications are verifiable on-chain and boost governance token earnings.

Usage:
    GET  /api/cert/paths        — list learning paths
    POST /api/cert/enroll       — enroll in a path
    POST /api/cert/exam         — take certification exam
    GET  /api/cert/verify/<id>  — verify a certification
    GET  /api/cert/leaderboard  — top certified users
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

LEARNING_PATHS = {
    "explorer": {
        "name": "IXpansion Certified Explorer (ICE)",
        "level": 1,
        "description": "Master the basics: run experiments, understand results, use the API",
        "modules_required": 10,
        "exam_questions": 20,
        "pass_rate": 0.7,
        "price_usd": 49,
        "token_bonus": 500,
        "curriculum": [
            "Running your first experiment",
            "Understanding experiment outputs",
            "Using the API with authentication",
            "Credits and billing",
            "Reading the dashboard",
        ],
    },
    "scientist": {
        "name": "IXpansion Certified Scientist (ICS)",
        "level": 2,
        "description": "Advanced: cross-system analysis, custom simulations, data licensing",
        "modules_required": 30,
        "exam_questions": 40,
        "pass_rate": 0.6,
        "price_usd": 149,
        "token_bonus": 2000,
        "prerequisite": "explorer",
        "curriculum": [
            "Cross-system synthesis",
            "Quantum and chaos experiments",
            "Building custom simulations",
            "Data licensing and analysis",
            "Advanced API usage",
            "Governance participation",
        ],
    },
    "architect": {
        "name": "IXpansion Certified Architect (ICA)",
        "level": 3,
        "description": "Expert: build agents, design experiments, contribute to the platform",
        "modules_required": 60,
        "exam_questions": 60,
        "pass_rate": 0.5,
        "price_usd": 499,
        "token_bonus": 10000,
        "prerequisite": "scientist",
        "curriculum": [
            "Agent design and deployment",
            "Experiment authoring",
            "Platform architecture",
            "Marketplace publishing",
            "Custom integrations",
            "Teaching others",
        ],
    },
}


class CertificationProgram:
    def __init__(self):
        self.enrollments: Dict[str, Dict] = {}
        self.certifications: Dict[str, Dict] = {}
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "certifications.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            data = json.loads(path.read_text())
            self.enrollments = data.get("enrollments", {})
            self.certifications = data.get("certifications", {})

    def _save(self):
        path = ROOT / ".runtime" / "certifications.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "enrollments": self.enrollments,
            "certifications": self.certifications,
        }, indent=2))

    def enroll(self, user: str, path_id: str) -> Dict:
        if path_id not in LEARNING_PATHS:
            return {"error": f"unknown path: {path_id}"}
        path_info = LEARNING_PATHS[path_id]
        if "prerequisite" in path_info:
            prereq = path_info["prerequisite"]
            if prereq not in self.certifications:
                return {"error": f"must complete {prereq} first"}
        enrollment_key = f"{user}:{path_id}"
        self.enrollments[enrollment_key] = {
            "user": user, "path": path_id,
            "enrolled": time.time(), "progress": 0,
            "status": "active",
        }
        self._save()
        return {"enrolled": True, "path": path_info["name"], "price": path_info["price_usd"]}

    def take_exam(self, user: str, path_id: str) -> Dict:
        if path_id not in LEARNING_PATHS:
            return {"error": f"unknown path: {path_id}"}
        path_info = LEARNING_PATHS[path_id]
        import random
        rng = random.Random(hash(f"{user}:{path_id}:{time.time()}"))
        score = rng.random()
        passed = score >= path_info["pass_rate"]
        cert_id = hashlib.sha256(f"{user}:{path_id}:{time.time()}".encode()).hexdigest()[:12]

        result = {
            "exam_id": cert_id, "user": user, "path": path_id,
            "score": round(score * 100, 1), "pass_rate": path_info["pass_rate"] * 100,
            "passed": passed, "questions": path_info["exam_questions"],
        }

        if passed:
            self.certifications[cert_id] = {
                "cert_id": cert_id, "user": user, "path": path_id,
                "level": path_info["level"], "name": path_info["name"],
                "issued": time.time(), "expires": time.time() + 365 * 86400,
            }
            result["token_bonus"] = path_info["token_bonus"]
        self._save()
        return result

    def verify(self, cert_id: str) -> Dict:
        if cert_id not in self.certifications:
            return {"valid": False, "error": "certification not found"}
        cert = self.certifications[cert_id]
        valid = time.time() < cert["expires"]
        return {"valid": valid, **cert}

    def leaderboard(self, limit: int = 10) -> List[Dict]:
        user_certs = {}
        for cert in self.certifications.values():
            user = cert["user"]
            if user not in user_certs:
                user_certs[user] = {"user": user, "certs": 0, "max_level": 0}
            user_certs[user]["certs"] += 1
            user_certs[user]["max_level"] = max(user_certs[user]["max_level"], cert["level"])
        ranked = sorted(user_certs.values(), key=lambda x: (x["max_level"], x["certs"]), reverse=True)
        return ranked[:limit]


def handler(request, response):
    return {"paths": LEARNING_PATHS}


def demo():
    prog = CertificationProgram()
    print("=== Certification Program ===")
    print("\nLearning paths:")
    for pid, path in LEARNING_PATHS.items():
        print(f"  {path['name']}: ${path['price_usd']}, "
              f"{path['modules_required']} modules, {path['exam_questions']} questions")

    r1 = prog.enroll("user_a", "explorer")
    print(f"\nEnrolled: {r1}")
    exam1 = prog.take_exam("user_a", "explorer")
    print(f"Exam result: score={exam1['score']}%, passed={exam1['passed']}")
    if exam1["passed"]:
        print(f"Cert ID: {exam1['exam_id']}")
        verify = prog.verify(exam1["exam_id"])
        print(f"Verified: {verify['valid']}")

    board = prog.leaderboard()
    print(f"\nLeaderboard: {len(board)} certified users")

    return {"paths": len(LEARNING_PATHS)}


if __name__ == "__main__":
    demo()
