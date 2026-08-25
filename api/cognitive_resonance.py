"""Cognitive Resonance Engine — emergent multi-agent problem solving.

When agents form "thought clusters," their combined cognitive output
exceeds the sum of individual capabilities. This module measures
cognitive resonance between agent pairs and facilitates emergent
synthesis when resonance exceeds thresholds.

Usage:
    POST /api/resonance/pair          — measure resonance between two agents
    POST /api/resonance/cluster       — form a thought cluster
    GET  /api/resonance/clusters      — list active clusters
    POST /api/resonance/synthesize    — run synthesis on a cluster
    GET  /api/resonance/history       — resonance event history
"""
from __future__ import annotations

import hashlib
import json
import math
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

AGENT_PROFILES = {
    "scout_alpha": {"cognitive_style": "exploratory", "energy": 0.8, "specialty": "pattern_detection"},
    "analyst_beta": {"cognitive_style": "analytical", "energy": 0.7, "specialty": "statistical_reasoning"},
    "sentinel_gamma": {"cognitive_style": "vigilant", "energy": 0.9, "specialty": "anomaly_detection"},
    "weaver_delta": {"cognitive_style": "connective", "energy": 0.6, "specialty": "cross_system_analysis"},
    "oracle_epsilon": {"cognitive_style": "predictive", "energy": 0.5, "specialty": "forecasting"},
    "kintsugi_zeta": {"cognitive_style": "restorative", "energy": 0.85, "specialty": "error_recovery"},
}

COGNITIVE_DIMENSIONS = [
    "exploratory", "analytical", "vigilant", "connective",
    "predictive", "restorative", "creative", "logical",
]


def _resonance_score(profile_a: Dict, profile_b: Dict) -> float:
    """Compute resonance between two agent cognitive profiles."""
    style_match = 1.0 - (1.0 if profile_a["cognitive_style"] == profile_b["cognitive_style"] else 0.3)
    energy_harmony = 1.0 - abs(profile_a["energy"] - profile_b["energy"])
    specialty_complement = 0.9 if profile_a["specialty"] != profile_b["specialty"] else 0.4
    base = (style_match * 0.3 + energy_harmony * 0.3 + specialty_complement * 0.4)
    noise = hash(f"{profile_a['specialty']}:{profile_b['specialty']}") % 100 / 1000.0
    return round(min(1.0, base + noise), 4)


class CognitiveResonanceEngine:
    def __init__(self):
        self.clusters: Dict[str, Dict] = {}
        self.history: List[Dict] = []
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "resonance.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            data = json.loads(path.read_text())
            self.clusters = data.get("clusters", {})
            self.history = data.get("history", [])

    def _save(self):
        path = ROOT / ".runtime" / "resonance.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "clusters": self.clusters,
            "history": self.history[-500:],
        }, indent=2))

    def measure_pair(self, agent_a: str, agent_b: str) -> Dict:
        if agent_a not in AGENT_PROFILES or agent_b not in AGENT_PROFILES:
            return {"error": f"unknown agent(s): {agent_a}, {agent_b}"}
        pa = AGENT_PROFILES[agent_a]
        pb = AGENT_PROFILES[agent_b]
        score = _resonance_score(pa, pb)
        event = {
            "type": "pair_measurement",
            "agents": [agent_a, agent_b],
            "resonance": score,
            "timestamp": time.time(),
        }
        self.history.append(event)
        self._save()
        return {
            "agent_a": agent_a, "agent_b": agent_b,
            "resonance": score,
            "resonance_level": "strong" if score > 0.7 else "moderate" if score > 0.4 else "weak",
            "insight": f"{'Complementary' if pa['cognitive_style'] != pb['cognitive_style'] else 'Similar'} minds with {('high' if pa['energy'] == pb['energy'] else 'varied')} energy",
        }

    def form_cluster(self, agents: List[str], name: str = "") -> Dict:
        for a in agents:
            if a not in AGENT_PROFILES:
                return {"error": f"unknown agent: {a}"}
        if len(agents) < 2:
            return {"error": "cluster needs at least 2 agents"}
        cluster_id = hashlib.sha256(f"{'-'.join(sorted(agents))}:{time.time()}".encode()).hexdigest()[:10]
        total_resonance = 0.0
        pairs = 0
        for i in range(len(agents)):
            for j in range(i + 1, len(agents)):
                total_resonance += _resonance_score(AGENT_PROFILES[agents[i]], AGENT_PROFILES[agents[j]])
                pairs += 1
        avg_resonance = total_resonance / pairs if pairs else 0
        cluster_name = name or f"cluster_{cluster_id}"
        self.clusters[cluster_id] = {
            "name": cluster_name,
            "agents": agents,
            "avg_resonance": round(avg_resonance, 4),
            "created": time.time(),
            "synthesis_count": 0,
            "status": "active",
        }
        self.history.append({
            "type": "cluster_formed",
            "cluster_id": cluster_id,
            "agents": agents,
            "avg_resonance": round(avg_resonance, 4),
            "timestamp": time.time(),
        })
        self._save()
        return {
            "cluster_id": cluster_id,
            "name": cluster_name,
            "agents": agents,
            "avg_resonance": round(avg_resonance, 4),
            "resonance_potential": "high" if avg_resonance > 0.65 else "moderate",
        }

    def list_clusters(self) -> List[Dict]:
        return [{"id": k, **v} for k, v in self.clusters.items()]

    def synthesize(self, cluster_id: str, problem: str = "general") -> Dict:
        if cluster_id not in self.clusters:
            return {"error": f"unknown cluster: {cluster_id}"}
        cluster = self.clusters[cluster_id]
        if cluster["status"] != "active":
            return {"error": "cluster is not active"}
        styles = [AGENT_PROFILES[a]["cognitive_style"] for a in cluster["agents"]]
        specialties = [AGENT_PROFILES[a]["specialty"] for a in cluster["agents"]]
        diversity = len(set(styles)) / len(styles) if styles else 0
        synthesis_power = cluster["avg_resonance"] * diversity
        insight = (
            f"Cluster '{cluster['name']}' synthesized across {len(cluster['agents'])} minds. "
            f"Cognitive diversity: {diversity:.0%}. "
            f"Specialties engaged: {', '.join(specialties[:3])}. "
            f"Synthesis power: {synthesis_power:.3f}."
        )
        cluster["synthesis_count"] += 1
        self.history.append({
            "type": "synthesis",
            "cluster_id": cluster_id,
            "problem": problem,
            "synthesis_power": round(synthesis_power, 4),
            "timestamp": time.time(),
        })
        self._save()
        return {
            "cluster_id": cluster_id,
            "problem": problem,
            "synthesis_power": round(synthesis_power, 4),
            "diversity_index": round(diversity, 4),
            "insight": insight,
            "synthesis_number": cluster["synthesis_count"],
        }

    def history_log(self, limit: int = 20) -> List[Dict]:
        return self.history[-limit:]


def handler(request, response):
    engine = CognitiveResonanceEngine()
    return {"agents": list(AGENT_PROFILES.keys()), "dimensions": COGNITIVE_DIMENSIONS}


def demo():
    engine = CognitiveResonanceEngine()
    print("=== Cognitive Resonance Engine ===")
    pair = engine.measure_pair("scout_alpha", "oracle_epsilon")
    print(f"\nResonance: scout_alpha <-> oracle_epsilon = {pair['resonance']} ({pair['resonance_level']})")
    print(f"  Insight: {pair['insight']}")

    cluster = engine.form_cluster(
        ["scout_alpha", "analyst_beta", "weaver_delta"],
        name="exploration_team"
    )
    print(f"\nCluster '{cluster['name']}' formed: avg resonance {cluster['avg_resonance']}")

    synth = engine.synthesize(cluster["cluster_id"], problem="find hidden dependencies")
    print(f"Synthesis power: {synth['synthesis_power']}")
    print(f"  {synth['insight']}")

    return {"agents": len(AGENT_PROFILES), "clusters": len(engine.clusters)}


if __name__ == "__main__":
    demo()
