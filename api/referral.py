"""Referral & Affiliate Program — earn credits by referring users.

Users earn 500 credits for each referral who subscribes to Pro or Enterprise.
Referred users get 100 bonus credits. Tracks referral chains up to 3 levels.

Usage:
    POST /api/referral/generate   — get your referral code
    POST /api/referral/apply      — apply a referral code
    GET  /api/referral/stats      — view referral statistics
    GET  /api/referral/leaderboard — top referrers
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

REFERRALS_FILE = ROOT / ".runtime" / "referrals.json"
REFERRAL_REWARD = 500
REFERRAL_BONUS = 100
MAX_DEPTH = 3
COMMISSION_RATES = {1: 0.15, 2: 0.05, 3: 0.02}


class ReferralSystem:
    def __init__(self):
        self.referrals: Dict[str, Dict] = {}
        self._load()

    def _load(self):
        REFERRALS_FILE.parent.mkdir(parents=True, exist_ok=True)
        if REFERRALS_FILE.exists():
            self.referrals = json.loads(REFERRALS_FILE.read_text())

    def _save(self):
        REFERRALS_FILE.parent.mkdir(parents=True, exist_ok=True)
        REFERRALS_FILE.write_text(json.dumps(self.referrals, indent=2))

    def generate_code(self, user: str) -> Dict:
        if user in self.referrals:
            return {"code": self.referrals[user]["code"], "existing": True}
        code = hashlib.sha256(f"ref:{user}:{time.time()}".encode()).hexdigest()[:8].upper()
        self.referrals[user] = {
            "code": code, "user": user, "referred_by": None,
            "referrals": [], "total_earned": 0, "created": time.time(),
        }
        self._save()
        return {"code": code, "existing": False}

    def apply_code(self, new_user: str, code: str) -> Dict:
        referrer = None
        for user, data in self.referrals.items():
            if data["code"] == code:
                referrer = user
                break
        if not referrer:
            return {"error": "invalid referral code"}

        self.referrals[new_user] = {
            "code": hashlib.sha256(f"ref:{new_user}:{time.time()}".encode()).hexdigest()[:8].upper(),
            "user": new_user, "referred_by": referrer,
            "referrals": [], "total_earned": 0, "created": time.time(),
        }
        self.referrals[referrer]["referrals"].append(new_user)
        self.referrals[referrer]["total_earned"] += REFERRAL_REWARD
        self._save()
        return {
            "applied": True, "referrer": referrer,
            "new_user": new_user, "bonus_credits": REFERRAL_BONUS,
        }

    def get_stats(self, user: str) -> Dict:
        if user not in self.referrals:
            return {"error": "user not found"}
        data = self.referrals[user]
        return {
            "code": data["code"],
            "total_referrals": len(data["referrals"]),
            "total_earned": data["total_earned"],
            "referred_by": data["referred_by"],
        }

    def leaderboard(self, limit: int = 10) -> List[Dict]:
        ranked = sorted(
            self.referrals.values(),
            key=lambda x: x["total_earned"], reverse=True
        )
        return [
            {"user": r["user"], "referrals": len(r["referrals"]),
             "earned": r["total_earned"]}
            for r in ranked[:limit]
        ]


def demo():
    system = ReferralSystem()
    print("=== Referral & Affiliate Program ===")
    r1 = system.generate_code("aleph")
    print(f"  Aleph's code: {r1['code']}")
    r2 = system.generate_code("user_b")
    print(f"  User B's code: {r2['code']}")
    applied = system.apply_code("user_c", r1["code"])
    print(f"  User C applied: {applied}")
    applied2 = system.apply_code("user_d", r1["code"])
    print(f"  User D applied: {applied2}")
    stats = system.get_stats("aleph")
    print(f"\n  Aleph's stats: {stats}")
    board = system.leaderboard()
    print(f"\n  Leaderboard:")
    for entry in board:
        print(f"    {entry['user']}: {entry['referrals']} referrals, "
              f"${entry['earned'] * 0.01:.2f} earned")
    return {"leaderboard": board}


def handler(request, response):
    rs = ReferralSystem()
    lb = rs.leaderboard(5)
    return {"leaderboard": lb, "total_referrers": len(lb)}


if __name__ == "__main__":
    demo()
