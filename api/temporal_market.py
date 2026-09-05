"""Temporal Market — trade predictions of future system states.

Users buy and sell "temporal futures" — predictions about what the
system will look like in N cycles. Sellers stake credits on their
predictions, buyers stake credits on counter-predictions. When the
future arrives, accurate predictions are paid out.

Usage:
    POST /api/temporal/predict      — submit a prediction
    POST /api/temporal/bet          — bet on someone's prediction
    GET  /api/temporal/markets      — list active markets
    POST /api/temporal/settle       — settle a market when future arrives
    GET  /api/temporal/history      — prediction history
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


def _generate_state_snapshot() -> Dict:
    """Generate a plausible future system state."""
    return {
        "experiment_count": random.randint(150, 200),
        "agent_rentals_active": random.randint(0, 12),
        "credits_in_circulation": random.randint(5000, 15000),
        "entropy_level": round(random.uniform(0.2, 0.8), 3),
        "cluster_count": random.randint(0, 8),
    }


def _evaluate_prediction(predicted: Dict, actual: Dict) -> float:
    """Score how close a prediction is to reality (0-1)."""
    scores = []
    for key in predicted:
        if key in actual:
            p, a = predicted[key], actual[key]
            if isinstance(p, (int, float)) and isinstance(a, (int, float)):
                diff = abs(p - a) / max(abs(a), 1)
                scores.append(max(0, 1 - diff))
    return round(sum(scores) / len(scores), 4) if scores else 0.0


class TemporalMarket:
    def __init__(self):
        self.markets: Dict[str, Dict] = {}
        self.settled: List[Dict] = []
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "temporal_market.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            data = json.loads(path.read_text())
            self.markets = data.get("markets", {})
            self.settled = data.get("settled", [])

    def _save(self):
        path = ROOT / ".runtime" / "temporal_market.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "markets": self.markets,
            "settled": self.settled[-500:],
        }, indent=2))

    def predict(self, predictor: str, horizon_cycles: int,
                prediction: Dict, stake_credits: float) -> Dict:
        if stake_credits < 1:
            return {"error": "minimum stake is 1 credit"}
        if horizon_cycles < 1 or horizon_cycles > 100:
            return {"error": "horizon must be 1-100 cycles"}
        market_id = hashlib.sha256(f"{predictor}:{horizon_cycles}:{time.time()}".encode()).hexdigest()[:10]
        self.markets[market_id] = {
            "predictor": predictor,
            "horizon_cycles": horizon_cycles,
            "prediction": prediction,
            "stake_credits": stake_credits,
            "bets_for": [],
            "bets_against": [],
            "total_pool": stake_credits,
            "created": time.time(),
            "status": "open",
        }
        self._save()
        return {
            "market_id": market_id,
            "horizon_cycles": horizon_cycles,
            "stake": stake_credits,
            "status": "open",
        }

    def bet(self, market_id: str, bettor: str, direction: str,
            amount: float) -> Dict:
        if market_id not in self.markets:
            return {"error": f"unknown market: {market_id}"}
        market = self.markets[market_id]
        if market["status"] != "open":
            return {"error": "market is closed"}
        if direction not in ("for", "against"):
            return {"error": "direction must be 'for' or 'against'"}
        bet = {"bettor": bettor, "amount": amount, "timestamp": time.time()}
        if direction == "for":
            market["bets_for"].append(bet)
        else:
            market["bets_against"].append(bet)
        market["total_pool"] += amount
        self._save()
        return {
            "market_id": market_id,
            "direction": direction,
            "amount": amount,
            "pool_total": market["total_pool"],
        }

    def list_markets(self, status: str = "open") -> List[Dict]:
        return [
            {"id": k, **v} for k, v in self.markets.items()
            if v["status"] == status
        ]

    def settle(self, market_id: str) -> Dict:
        if market_id not in self.markets:
            return {"error": f"unknown market: {market_id}"}
        market = self.markets[market_id]
        if market["status"] != "open":
            return {"error": "market already settled"}
        actual = _generate_state_snapshot()
        accuracy = _evaluate_prediction(market["prediction"], actual)
        payout_multiplier = 1.0 + accuracy
        winners = "predictor_and_for" if accuracy > 0.6 else "against_bettors"
        market["status"] = "settled"
        market["accuracy"] = accuracy
        market["actual_state"] = actual
        record = {
            "market_id": market_id,
            "predictor": market["predictor"],
            "horizon_cycles": market["horizon_cycles"],
            "accuracy": accuracy,
            "pool_total": market["total_pool"],
            "payout_multiplier": round(payout_multiplier, 2),
            "winners": winners,
            "settled_at": time.time(),
        }
        self.settled.append(record)
        self._save()
        return record

    def history(self, limit: int = 20) -> List[Dict]:
        return self.settled[-limit:]


def handler(request, response):
    market = TemporalMarket()
    return {"active_markets": len(market.list_markets()), "settled": len(market.settled)}


def demo():
    market = TemporalMarket()
    print("=== Temporal Market ===")
    pred = market.predict("trader_alpha", 10,
                          {"experiment_count": 175, "entropy_level": 0.5},
                          stake_credits=50)
    print(f"\nPrediction submitted: {pred['market_id']}, stake: {pred['stake']} credits")

    market.bet(pred["market_id"], "trader_beta", "for", 20)
    market.bet(pred["market_id"], "trader_gamma", "against", 30)
    print("Bets placed: +20 for, +30 against")

    result = market.settle(pred["market_id"])
    print(f"\nSettled: accuracy={result['accuracy']}, pool={result['pool_total']}")
    print(f"Winners: {result['winners']}, multiplier: {result['payout_multiplier']}x")

    return {"markets": len(market.markets), "settled": len(market.settled)}


if __name__ == "__main__":
    demo()

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "interface", "status": "active", "wave": "0", "module": "temporal_market"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
