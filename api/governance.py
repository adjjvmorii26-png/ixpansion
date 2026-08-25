"""Governance Token — let users vote on experiment development priorities.

Holders of IXPN (IXpansion Network) tokens can vote on which experiments
get developed next, which bugs get fixed, and which features ship first.
Tokens are earned through usage, referrals, and marketplace sales.

Usage:
    POST /api/governance/mint     — mint tokens (earned)
    GET  /api/governance/balance  — check token balance
    POST /api/governance/vote     — vote on a proposal
    GET  /api/governance/proposals — list active proposals
    POST /api/governance/propose  — create a proposal
"""
from __future__ import annotations

import hashlib
import json
import time
import sys
from pathlib import Path
from typing import Any, Dict, List
from dataclasses import dataclass, field

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

GOVERNANCE_FILE = ROOT / ".runtime" / "governance.json"

TOKEN_EARN_RATES = {
    "api_call": 1,
    "experiment_run": 5,
    "marketplace_sale": 50,
    "referral": 100,
    "bug_report": 200,
    "test_contribution": 150,
}


@dataclass
class Proposal:
    proposal_id: str
    title: str
    description: str
    creator: str
    category: str
    votes_for: int = 0
    votes_against: int = 0
    voters: Dict[str, int] = field(default_factory=dict)
    status: str = "active"
    created: float = 0.0
    ends: float = 0.0


class GovernanceSystem:
    def __init__(self):
        self.balances: Dict[str, int] = {}
        self.proposals: List[Dict] = []
        self.tx_history: List[Dict] = []
        self._load()

    def _load(self):
        GOVERNANCE_FILE.parent.mkdir(parents=True, exist_ok=True)
        if GOVERNANCE_FILE.exists():
            data = json.loads(GOVERNANCE_FILE.read_text())
            self.balances = data.get("balances", {})
            self.proposals = data.get("proposals", [])
            self.tx_history = data.get("tx_history", [])

    def _save(self):
        GOVERNANCE_FILE.parent.mkdir(parents=True, exist_ok=True)
        GOVERNANCE_FILE.write_text(json.dumps({
            "balances": self.balances,
            "proposals": self.proposals,
            "tx_history": self.tx_history[-500:],
        }, indent=2))

    def mint(self, user: str, activity: str, amount: int = None) -> Dict:
        if amount is None:
            amount = TOKEN_EARN_RATES.get(activity, 1)
        self.balances[user] = self.balances.get(user, 0) + amount
        self.tx_history.append({
            "user": user, "type": "mint", "activity": activity,
            "amount": amount, "time": time.time(),
        })
        self._save()
        return {"minted": amount, "balance": self.balances[user], "activity": activity}

    def get_balance(self, user: str) -> int:
        return self.balances.get(user, 0)

    def propose(self, title: str, description: str, creator: str,
                category: str = "experiment") -> Dict:
        balance = self.balances.get(creator, 0)
        if balance < 100:
            return {"error": "need at least 100 IXPN to propose"}
        proposal_id = hashlib.sha256(f"{title}:{creator}:{time.time()}".encode()).hexdigest()[:10]
        proposal = {
            "id": proposal_id, "title": title, "description": description,
            "creator": creator, "category": category,
            "votes_for": 0, "votes_against": 0, "voters": {},
            "status": "active", "created": time.time(),
            "ends": time.time() + 7 * 86400,
        }
        self.proposals.append(proposal)
        self._save()
        return {"proposed": True, "id": proposal_id, "title": title}

    def vote(self, proposal_id: str, voter: str, vote: int) -> Dict:
        if vote not in (1, -1):
            return {"error": "vote must be 1 (for) or -1 (against)"}
        balance = self.balances.get(voter, 0)
        if balance <= 0:
            return {"error": "no IXPN tokens to vote"}
        for p in self.proposals:
            if p["id"] == proposal_id:
                if voter in p["voters"]:
                    return {"error": "already voted"}
                weight = min(balance, 100)
                p["voters"][voter] = vote
                if vote == 1:
                    p["votes_for"] += weight
                else:
                    p["votes_against"] += weight
                self._save()
                return {
                    "voted": True, "proposal": p["title"],
                    "vote": "for" if vote == 1 else "against",
                    "weight": weight,
                    "tally": f"{p['votes_for']} for / {p['votes_against']} against",
                }
        return {"error": "proposal not found"}

    def list_proposals(self, status: str = "active") -> List[Dict]:
        return [p for p in self.proposals if p["status"] == status]

    def tokenomics(self) -> Dict:
        total_supply = sum(self.balances.values())
        holders = len(self.balances)
        return {
            "total_supply": total_supply,
            "holders": holders,
            "earn_rates": TOKEN_EARN_RATES,
            "top_holders": sorted(
                [{"user": u, "balance": b} for u, b in self.balances.items()],
                key=lambda x: x["balance"], reverse=True
            )[:10],
        }


def demo():
    gov = GovernanceSystem()
    print("=== Governance Token System ===")
    gov.mint("aleph", "marketplace_sale", 200)
    gov.mint("user_b", "test_contribution", 150)
    gov.mint("user_c", "referral", 100)

    prop = gov.propose("Add quantum gravity simulator",
                       "A new experiment that simulates quantum gravity effects",
                       "aleph", "experiment")
    print(f"  Proposal: {prop}")

    v1 = gov.vote(prop["id"], "user_b", 1)
    print(f"  User B voted: {v1}")
    v2 = gov.vote(prop["id"], "user_c", 1)
    print(f"  User C voted: {v2}")

    proposals = gov.list_proposals()
    print(f"\n  Active proposals: {len(proposals)}")
    for p in proposals:
        print(f"    {p['title']}: {p['votes_for']} for / {p['votes_against']} against")

    tok = gov.tokenomics()
    print(f"\n  Token supply: {tok['total_supply']} IXPN")
    print(f"  Holders: {tok['holders']}")

    return tok


def handler(request, response):
    gs = GovernanceSystem()
    return {"proposals": len(gs.list_proposals()), "total_tokens": sum(gs.get_balance(u) for u in set(p["creator"] for p in gs.list_proposals("all"))) if gs.list_proposals("all") else 0}


if __name__ == "__main__":
    demo()
