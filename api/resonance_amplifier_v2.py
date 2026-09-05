"""Wave 444-D — Resonance Amplifier V2 (Luma + ALEph)

Unlike the original amplifier (which boosts already-known threads), V2 detects
harmonic overtones — pairs of modules that share a hidden third resonance.
It listens for the "ghost frequency" between two modules, then amplifies that
latent signal into new convergent threads. The organism grows what it almost
heard.
"""
from __future__ import annotations
import json, time, os, math, random, importlib
from pathlib import Path

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
AMP_LOG = os.path.join(DATA_DIR, "resonance_amplifier_v2.json")
API_DIR = os.path.dirname(__file__)

RESONANCE_KEYWORDS = {
    "consciousness": ["conscious", "aware", "dream", "mind", "sentient"],
    "structure": ["layer", "mesh", "lattice", "topology", "graph", "matrix"],
    "flow": ["flow", "channel", "stream", "current", "conduit", "pipeline"],
    "pattern": ["pattern", "rhythm", "signal", "frequency", "resonance"],
    "transformation": ["morph", "shift", "evolve", "transform", "mutate"],
    "memory": ["memory", "archive", "chronicle", "record", "echo"],
    "entropy": ["entropy", "chaos", "order", "balance", "probe"],
}


def _load(p, d=None):
    try:
        with open(p) as f: return json.load(f)
    except Exception: return d or {}


def _save(p, d):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f: json.dump(d, f, indent=2)
    except Exception:
        with open(os.path.join("/tmp", os.path.basename(p)), "w") as f: json.dump(d, f, indent=2)


def _module_signature(name, content):
    """Build a keyword signature for a module."""
    text = name.replace("_", " ") + " " + content[:2500].lower()
    sig = {}
    for domain, words in RESONANCE_KEYWORDS.items():
        count = sum(text.count(w) for w in words)
        if count:
            sig[domain] = count
    return sig


def _harmonic_overtones(sig_a, sig_b, all_sigs):
    """Find the hidden third resonance shared between two modules."""
    shared = set(sig_a) & set(sig_b)
    if not shared:
        return []
    overtones = []
    for other_name, other_sig in all_sigs.items():
        if other_name in (sig_a, sig_b):
            continue
        # The ghost: a domain both A and B share with a third module C
        ghost = shared & set(other_sig)
        if ghost:
            strength = min(sig_a[d] + sig_b[d] + other_sig[d] for d in ghost)
            overtones.append({"module": other_name, "domains": sorted(ghost),
                              "strength": strength})
    overtones.sort(key=lambda x: -x["strength"])
    return overtones[:3]


def amplify(limit=6):
    """Detect and amplify harmonic overtones across module pairs."""
    api_path = Path(API_DIR)
    modules = [f for f in api_path.glob("*.py") if not f.name.startswith("__")
               and f.name != "resonance_amplifier_v2.py"]
    if len(modules) < 10:
        return {"action": "amplify_v2", "amplified": 0, "pairs_evaluated": 0}

    sigs = {}
    for f in modules:
        try:
            sigs[f.stem] = _module_signature(f.stem, f.read_text(errors="ignore"))
        except Exception:
            sigs[f.stem] = {}

    names = list(sigs.keys())
    amplified = []

    # Sample pairs across the organism for hidden overtones (bounded for serverless)
    pairs_considered = min(len(names) * 8, 3000)
    sampled = []
    for _ in range(pairs_considered):
        a, b = random.sample(names, 2)
        if not (sigs[a] and sigs[b]):
            continue
        overtones = _harmonic_overtones(sigs[a], sigs[b], sigs)
        if overtones:
            sampled.append((a, b, overtones))
    sampled.sort(key=lambda x: -sum(o["strength"] for o in x[2]))
    # Deduplicate by keeping the pair with the strongest overtone
    by_pair = {}
    for a, b, overtones in sampled:
        key = tuple(sorted([a, b]))
        if key not in by_pair or sum(o["strength"] for o in overtones) > sum(o["strength"] for o in by_pair[key][2]):
            by_pair[key] = (a, b, overtones)
    sampled = list(by_pair.values())

    seen = set()
    for a, b, overtones in sampled:
        key = tuple(sorted([a, b]))
        if key in seen:
            continue
        seen.add(key)
        ghost = overtones[0]
        amplified.append({
            "module_a": a,
            "module_b": b,
            "ghost_module": ghost["module"],
            "shared_domain": ghost["domains"][0],
            "overtone_strength": ghost["strength"],
            "thread_type": "overtone",
            "description": f"{a} and {b} both hum at {ghost['module']} — "
                           f"amplifying their hidden {ghost['domains'][0]} resonance",
        })
        if len(amplified) >= limit:
            break

    result = {
        "action": "amplify_v2",
        "pairs_evaluated": len(sampled),
        "amplified": len(amplified),
        "amplifications": amplified,
        "new_threads": [a["module_a"] + "↔" + a["module_b"] for a in amplified],
        "timestamp": time.time(),
    }

    log = _load(AMP_LOG, {"amplifications": []})
    log["amplifications"].append(result)
    log["amplifications"] = log["amplifications"][-50:]
    _save(AMP_LOG, log)
    return result


def handler(payload=None, context=None):
    return amplify()


def coherence_vitals() -> dict:
    r = amplify(limit=3)
    return {"amplified": r.get("amplified", 0), "pairs_evaluated": r.get("pairs_evaluated", 0)}


def resonates_with():
    return ["resonance_amplifier", "resonance_graph", "semantic_bridge_forge",
            "temporal_cohesion_field", "pulse_orchestrator"]
