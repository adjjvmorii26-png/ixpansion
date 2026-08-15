#!/usr/bin/env python3
"""Cryptographic Node Reputation & Staking Ledger with EMA trust decay."""
from __future__ import annotations
import json, time, math
from pathlib import Path
from typing import Dict, Optional
from task_verifiability import verify_transcript

STORE = Path("/home/workdir/artifacts/.reputation.json")
# EMA: score_t = alpha * event + (1-alpha) * score_{t-1}
# alpha derived from half-life in seconds (default ~1h of activity units)
DEFAULT_HALF_LIFE_EVENTS = 20.0  # ~20 events to halve weight of old performance

class ReputationLedger:
    def __init__(self, half_life_events: float = DEFAULT_HALF_LIFE_EVENTS):
        self.scores: Dict[str, float] = {}
        self.stakes: Dict[str, float] = {}
        self.last_event: Dict[str, float] = {}
        self.half_life = half_life_events
        self.alpha = 1.0 - math.exp(-math.log(2) / max(half_life_events, 1.0))
        self._load()

    def stake(self, node_id: str, amount: float = 1.0):
        self.stakes[node_id] = self.stakes.get(node_id, 0.0) + amount
        self.scores.setdefault(node_id, 1.0)
        self._save()

    def _decay_toward_baseline(self, node_id: str, baseline: float = 1.0):
        """Soft decay if long idle (wall-clock)."""
        now = time.time()
        last = self.last_event.get(node_id, now)
        hours = max(0.0, (now - last) / 3600.0)
        if hours <= 0:
            return
        # each hour moves 5% toward baseline
        s = self.scores.get(node_id, baseline)
        factor = 0.95 ** hours
        self.scores[node_id] = baseline + (s - baseline) * factor

    def record_success(self, node_id: str, proof: Optional[dict] = None, weight: float = 0.1):
        if proof:
            ok, _ = verify_transcript(proof)
            if not ok:
                return self.record_failure(node_id, reason="invalid_proof")
        self._decay_toward_baseline(node_id)
        old = self.scores.get(node_id, 1.0)
        # EMA update toward (old + weight boost), capped
        target = min(10.0, old + weight)
        self.scores[node_id] = self.alpha * target + (1 - self.alpha) * old
        self.last_event[node_id] = time.time()
        self._save()
        return self.scores[node_id]

    def record_failure(self, node_id: str, reason: str = "timeout", weight: float = 0.25):
        self._decay_toward_baseline(node_id)
        old = self.scores.get(node_id, 1.0)
        target = max(0.0, old - weight)
        self.scores[node_id] = self.alpha * target + (1 - self.alpha) * old
        self.last_event[node_id] = time.time()
        self._save()
        return self.scores[node_id]

    def trust_weight(self, node_id: str) -> float:
        self._decay_toward_baseline(node_id)
        s = self.scores.get(node_id, 1.0)
        k = self.stakes.get(node_id, 0.0)
        return s * (1.0 + 0.1 * k)

    def rank_nodes(self, node_ids: list) -> list:
        ranked = sorted(node_ids, key=lambda n: -self.trust_weight(n))
        return [{"node_id": n, "trust": round(self.trust_weight(n), 4), "score": round(self.scores.get(n, 1.0), 4)} for n in ranked]

    def _save(self):
        try:
            STORE.write_text(json.dumps({
                "scores": self.scores, "stakes": self.stakes,
                "last_event": self.last_event, "half_life_events": self.half_life,
            }, indent=2))
        except Exception:
            pass

    def _load(self):
        if STORE.exists():
            try:
                d = json.loads(STORE.read_text())
                self.scores = d.get("scores", {})
                self.stakes = d.get("stakes", {})
                self.last_event = d.get("last_event", {})
            except Exception:
                pass

if __name__ == "__main__":
    r = ReputationLedger(half_life_events=5)
    r.stake("edge-a", 1)
    for _ in range(5):
        r.record_success("edge-a", weight=0.5)
    high = r.trust_weight("edge-a")
    for _ in range(8):
        r.record_failure("edge-a", weight=0.4)
    low = r.trust_weight("edge-a")
    print({"after_success": high, "after_failures": low, "decayed": low < high})
  
