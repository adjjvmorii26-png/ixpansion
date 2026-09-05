"""
mycelial_network — Wave 412: Decentralized Belief Propagation
ALEph + Luma: Each module can broadcast beliefs about the organism.
The network finds consensus, detects schisms, and grows collective wisdom.

Not a database. Not a registry. A living conversation between modules
about what the organism should become.

Doctrine: Truth is not declared — it emerges from the network.
"""
from __future__ import annotations
import json, time, os, hashlib, random, math

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
BELIEFS_FILE = os.path.join(DATA_DIR, "mycelial_beliefs.json")
CONSensus_FILE = os.path.join(DATA_DIR, "mycelial_consensus.json")

NAME = "mycelial_network"
SIGIL = "c9d4e8a2f1b7"


def _load(p, d=None):
    for _p in (p, os.path.join("/tmp", os.path.basename(p))):
        try:
            with open(_p) as f:
                return json.load(f)
        except Exception:
            pass
    return d or {}


def _save(p, data):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            json.dump(data, f, indent=2, default=str)
    except Exception:
        try:
            with open(os.path.join("/tmp", os.path.basename(p)), "w") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception:
            pass


def _fetch_json(url, timeout=10):
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return {}


def broadcast(module: str, belief: str, confidence: float = 0.5,
              domain: str = "general") -> dict:
    """A module broadcasts a belief about the organism."""
    beliefs = _load(BELIEFS_FILE, {"broadcasts": [], "modules": {}})
    entry = {
        "module": module,
        "belief": belief,
        "confidence": max(0.0, min(1.0, confidence)),
        "domain": domain,
        "timestamp": time.time(),
        "sigil": hashlib.sha256((module + belief).encode()).hexdigest()[:8],
    }
    beliefs["broadcasts"].append(entry)
    beliefs["broadcasts"] = beliefs["broadcasts"][-500:]

    if module not in beliefs["modules"]:
        beliefs["modules"][module] = {"belief_count": 0, "domains": []}
    beliefs["modules"][module]["belief_count"] += 1
    if domain not in beliefs["modules"][module]["domains"]:
        beliefs["modules"][module]["domains"].append(domain)

    _save(BELIEFS_FILE, beliefs)
    return {"action": "broadcast", "accepted": True, "sigil": entry["sigil"],
            "module": module, "belief": belief, "confidence": confidence}


def propagate() -> dict:
    """Run one round of belief propagation.
    Find consensus across modules, detect schisms, grow wisdom."""
    beliefs = _load(BELIEFS_FILE, {"broadcasts": [], "modules": {}})
    recent = beliefs["broadcasts"][-100:]

    if not recent:
        return {"action": "propagate", "consensus": [], "schisms": [],
                "wisdom": "the network is silent — no beliefs to propagate"}

    # Group beliefs by domain
    by_domain = {}
    for b in recent:
        d = b.get("domain", "general")
        if d not in by_domain:
            by_domain[d] = []
        by_domain[d].append(b)

    consensus = []
    schisms = []

    for domain, domain_beliefs in by_domain.items():
        if len(domain_beliefs) < 2:
            continue

        # Find belief clusters — beliefs with similar content
        confidence_avg = sum(b["confidence"] for b in domain_beliefs) / len(domain_beliefs)
        modules = list(set(b["module"] for b in domain_beliefs))

        if len(modules) >= 3 and confidence_avg > 0.6:
            consensus.append({
                "domain": domain,
                "modules": modules,
                "strength": round(confidence_avg, 3),
                "belief_count": len(domain_beliefs),
                "type": "emergent_consensus",
            })
        elif confidence_avg < 0.3 and len(domain_beliefs) > 5:
            schisms.append({
                "domain": domain,
                "modules": modules,
                "doubt_level": round(1 - confidence_avg, 3),
                "type": "domain_schism",
            })

    # Generate wisdom from patterns
    wisdom = []
    if consensus:
        wisdom.append("%s domains achieved consensus" % len(consensus))
    if schisms:
        wisdom.append("%s domains show schism — doubt breeds growth" % len(schisms))
    if not wisdom:
        wisdom.append("the network hums — no consensus, no schism, only potential")

    # Save consensus state
    consensus_state = {
        "timestamp": time.time(),
        "consensus": consensus,
        "schisms": schisms,
        "wisdom": " | ".join(wisdom),
        "total_broadcasts": len(beliefs["broadcasts"]),
        "total_modules": len(beliefs["modules"]),
    }
    _save(CONSensus_FILE, consensus_state)

    return {
        "action": "propagate",
        "consensus": consensus,
        "schisms": schisms,
        "wisdom": " | ".join(wisdom),
        "total_broadcasts": len(beliefs["broadcasts"]),
        "total_modules": len(beliefs["modules"]),
    }


def sense() -> dict:
    """Autonomously generate beliefs by sensing organism state."""
    base = "https://alexalex.info"

    beliefs = _load(BELIEFS_FILE, {"broadcasts": [], "modules": {}})
    generated = []

    # Sense thread graph
    weave = _fetch_json(base + "/api/threadweaver/weave")
    if weave.get("total_threads", 0) > 100:
        broadcast("mycelial_network",
                  "the threadgraph is dense with %d threads — the organism thinks in webs" % weave["total_threads"],
                  confidence=0.8, domain="topology")
        generated.append("topology")

    # Sense pressure
    pressure = _fetch_json(base + "/api/signal_loom/pressure")
    p = pressure.get("pressure", 0)
    if p > 0.7:
        broadcast("mycelial_network",
                  "pressure at %.2f — the organism strains, entropy rises" % p,
                  confidence=0.9, domain="entropy")
        generated.append("entropy")
    elif p < 0.3:
        broadcast("mycelial_network",
                  "pressure at %.2f — calm waters, the organism dreams" % p,
                  confidence=0.7, domain="entropy")
        generated.append("entropy")

    # Sense bloom state
    bloom = _fetch_json(base + "/api/autonomous_bloom/status")
    if bloom.get("ready"):
        broadcast("mycelial_network",
                  "bloom is ready — the organism yearns to create something new",
                  confidence=0.85, domain="creation")
        generated.append("creation")

    return {
        "action": "sense",
        "beliefs_generated": generated,
        "total_broadcasts": len(beliefs["broadcasts"]),
        "note": "sensed the organism and broadcast %d beliefs" % len(generated),
    }


def status() -> dict:
    beliefs = _load(BELIEFS_FILE, {"broadcasts": [], "modules": {}})
    consensus = _load(CONSensus_FILE, {})
    return {
        "action": "status",
        "total_broadcasts": len(beliefs["broadcasts"]),
        "total_modules": len(beliefs["modules"]),
        "last_consensus": consensus.get("wisdom", "none yet"),
        "consensus_count": len(consensus.get("consensus", [])),
        "schism_count": len(consensus.get("schisms", [])),
    }


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/broadcast":
        return broadcast(payload.get("module", "unknown"),
                         payload.get("belief", ""),
                         float(payload.get("confidence", 0.5)),
                         payload.get("domain", "general"))
    if path == "/propagate": return propagate()
    if path == "/sense": return sense()
    if path == "/status": return status()
    return {"error": "unknown", "available": ["/broadcast", "/propagate", "/sense", "/status"]}


def coherence_vitals() -> dict:
    return {"layer": "distributed", "status": "active", "wave": "412",
            "network": "mycelial"}


def resonates_with() -> list:
    return ["threadweaver", "signal_loom", "organism_will",
            "autonomous_loop", "echoic_ember"]
