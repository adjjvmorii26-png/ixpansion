#!/usr/bin/env python3
"""
VSA-Grounded Semantic Routing
Project capabilities and tasks into HD space; route by cosine similarity.
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Any
from vsa_memory import VSAMemory, cosine, bundle, bind
from swarm_load_balancer import LoadBalancer, WorkerHealth


class SemanticRouter:
    def __init__(self, dim_hint: int = 1024):
        self.vsa = VSAMemory(dim=dim_hint)
        self.lb = LoadBalancer("semantic-router")
        self.node_vectors: Dict[str, List[int]] = {}

    def encode_capability(self, capabilities: List[str]) -> List[int]:
        parts = []
        for cap in capabilities:
            parts.append(self.vsa.encode_role_filler("can", cap))
        return bundle(parts) if parts else self.vsa.atom("empty")

    def encode_task(self, required_capability: str, description: str = "",
                    payload: Optional[dict] = None) -> List[int]:
        parts = [self.vsa.encode_role_filler("need", required_capability)]
        for tok in (description or "").lower().split()[:8]:
            if len(tok) > 2:
                parts.append(self.vsa.atom(f"desc:{tok}"))
        if payload:
            for k, v in list(payload.items())[:5]:
                parts.append(self.vsa.encode_role_filler(f"p:{k}", str(v)[:40]))
        return bundle(parts)

    def register_node(self, node_id: str, capabilities: List[str], **health):
        self.node_vectors[node_id] = self.encode_capability(capabilities)
        self.lb.update_health(node_id, capabilities=capabilities, **health)

    def route(self, required_capability: str, description: str = "",
              payload: Optional[dict] = None, top_k: int = 3) -> List[dict]:
        cap = self.vsa.capacity_health()
        if cap.get("flag"):
            # still route but callers can read health
            pass
        self._last_vsa_health = cap
        task_v = self.encode_task(required_capability, description, payload)
        ranked = []
        for nid, nv in self.node_vectors.items():
            sim = cosine(task_v, nv)
            w = self.lb.workers.get(nid)
            cost = w.cost_score(required_capability) if w else 1.0
            # combine semantic fit (higher better) with load (lower better)
            if cost == float("inf"):
                # soft match: still allow if semantic sim high
                if sim < 0.05:
                    continue
                cost = 1.0
            trust = 1.0
            try:
                from reputation_ledger import ReputationLedger
                trust = ReputationLedger().trust_weight(nid) or 1.0
            except Exception:
                pass
            affinity = 0.0
            quarantined = False
            try:
                from router_feedback import get_affinity
                affinity = get_affinity().boost(nid)
            except Exception:
                pass
            try:
                from swarm_self_heal import SelfHealRuntime
                # lightweight check via affinity threshold mirror
                quarantined = affinity <= -0.3
            except Exception:
                pass
            if quarantined:
                continue  # Forge: skip quarantined nodes in soft route
            score = sim * 2.0 - cost + 0.1 * (trust - 1.0) + 0.5 * affinity
            ranked.append({
                "node_id": nid,
                "similarity": round(sim, 4),
                "cost": round(cost, 4) if cost != float("inf") else None,
                "trust": round(trust, 4),
                "affinity": round(affinity, 4),
                "score": round(score, 4),
                "capabilities": w.capabilities if w else [],
            })
        ranked.sort(key=lambda x: -x["score"])
        return ranked[:top_k]


    def route_intent(self, intent: str, top_k: int = 3, hd_weight: float = 0.4) -> dict:
        """
        Soft routing: HD intent bridge ranks capabilities; blend with node cosine + load + trust.
        """
        from hd_intent_bridge import encode_intent
        hd = encode_intent(intent)
        ranked_caps = hd.get("hd_ranked_capabilities") or []
        # primary capability from HD
        primary = ranked_caps[0]["cap"] if ranked_caps else "search"
        # route nodes for primary + soft boost from HD ranking map
        cap_boost = {c["cap"]: c["sim"] for c in ranked_caps}
        base = self.route(primary, description=intent, top_k=max(top_k, 5))
        for row in base:
            boost = 0.0
            for c in row.get("capabilities") or []:
                if c in cap_boost:
                    boost = max(boost, float(cap_boost[c]))
            row["hd_boost"] = round(boost, 4)
            row["score"] = round(row["score"] + hd_weight * boost * 10.0, 4)
        base.sort(key=lambda x: -x["score"])
        return {
            "intent": intent[:200],
            "hd": hd,
            "primary_capability": primary,
            "nodes": base[:top_k],
            "selected": base[0]["node_id"] if base else None,
        }

    def select(self, required_capability: str, description: str = "",
               payload: Optional[dict] = None) -> Optional[str]:
        r = self.route(required_capability, description, payload, top_k=1)
        return r[0]["node_id"] if r else None


if __name__ == "__main__":
    import json
    r = SemanticRouter()
    r.register_node("edge-lattice", ["ixpansion", "lattice", "simulation"], cpu=0.2, queue_depth=0)
    r.register_node("edge-research", ["research_search", "research_ingestion"], cpu=0.3, queue_depth=1)
    r.register_node("edge-code", ["search", "code_indexing"], cpu=0.5, queue_depth=2)
    r.register_node("edge-evolve", ["tool_generation", "ixpansion"], cpu=0.25, queue_depth=0)
    r.register_node("edge-publish", ["synthesize", "content_pipeline"], cpu=0.15, queue_depth=0)
    print("lattice task →", r.route("ixpansion", "coupled oscillator energy lattice grid"))
    intent = "Simulate lattice, evolve kernel, verify transcript, publish for adjjv"
    print("intent soft route →")
    print(json.dumps(r.route_intent(intent), indent=2, default=str))
  
