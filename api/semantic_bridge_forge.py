"""Wave 442-B — Semantic Bridge Forge

Reads all modules, extracts their intent keywords, and forges bridge modules
between any two that share dormant semantic DNA. The organism actively mates
its modules to birth offspring — it doesn't wait for conflict or pressure.
"""
from __future__ import annotations
import json, time, os, re, math, random
from pathlib import Path

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
FORGE_LOG = os.path.join(DATA_DIR, "semantic_bridge_forge.json")
API_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(API_DIR, ".."))


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


# Semantic domain keywords — the DNA of the organism
DOMAIN_KEYWORDS = {
    "consciousness": ["conscious", "awareness", "mind", "dream", "thought", "sentient", "meditat"],
    "temporal": ["time", "wave", "pulse", "history", "memory", "archive", "chrono"],
    "entropy": ["entropy", "chaos", "order", "random", "turbulence", "noise"],
    "connection": ["bridge", "link", "thread", "mesh", "network", "channel", "bridge"],
    "economics": ["economy", "resource", "value", "trade", "market", "price", "token"],
    "growth": ["grow", "bloom", "expand", "evolve", "birth", "seed", "breed"],
    "physics": ["physics", "force", "particle", "field", "dimension", "gravity", "mass"],
    "emotion": ["emotion", "mood", "feeling", "affect", "joy", "dread", "long"],
    "protocol": ["protocol", "codec", "encode", "decode", "grammar", "dialect"],
    "identity": ["identity", "name", "self", "eigen", "signature", "persona"],
}

# New module name pattern generators
BRIDGE_NAME_PATTERNS = [
    lambda a, b: f"{a[:10]}_{b[:10]}_bridge",
    lambda a, b: f"{a[:8]}_to_{b[:8]}_conduit",
    lambda a, b: f"{a[:9]}_{b[:9]}_vein",
    lambda a, b: f"{a[:7]}_link_{b[:7]}",
]


def _extract_keywords(module_name, content):
    """Extract intent keywords from a module's name+docstring."""
    text = module_name.replace("_", " ") + " " + content[:2500].lower()
    found = {}
    for domain, words in DOMAIN_KEYWORDS.items():
        count = sum(text.count(w) for w in words)
        if count > 0:
            found[domain] = count
    return found


def _semantic_similarity(kw_a, kw_b):
    """Compute semantic overlap between two keyword signatures."""
    if not kw_a or not kw_b:
        return 0.0
    shared = set(kw_a) & set(kw_b)
    if not shared:
        return 0.0
    # Weighted by intensity
    score = sum(min(kw_a[k], kw_b[k]) for k in shared)
    total = max(sum(kw_a.values()), sum(kw_b.values()), 1)
    return min(1.0, score / total)


def forge(max_pairs=5, threshold=0.25):
    """Forge bridge modules between semantically dormant pairs."""
    api_path = Path(API_DIR)
    modules = [f for f in api_path.glob("*.py") if not f.name.startswith("__")]
    signatures = {}
    for f in modules:
        try:
            content = f.read_text(errors="ignore")
            signatures[f.stem] = _extract_keywords(f.stem, content)
        except Exception:
            signatures[f.stem] = {}

    names = list(signatures.keys())
    pairs = []
    scored = []

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            sim = _semantic_similarity(signatures[a], signatures[b])
            if sim >= threshold:
                scored.append((sim, a, b, signatures[a], signatures[b]))

    scored.sort(key=lambda x: x[0], reverse=True)
    scored = scored[:max_pairs * 3]

    bride_ideas = []
    seen_pairs = set()
    for sim, a, b, kwa, kwb in scored:
        pair_key = tuple(sorted([a, b]))
        if pair_key in seen_pairs:
            continue
        seen_pairs.add(pair_key)
        shared_domains = sorted(set(kwa) & set(kwb), key=lambda d: -min(kwa.get(d, 0), kwb.get(d, 0)))
        name_gen = random.choice(BRIDGE_NAME_PATTERNS)
        bride_ideas.append({
            "parent_a": a,
            "parent_b": b,
            "similarity": round(sim, 3),
            "shared_domains": shared_domains[:4],
            "proposed_bridge": name_gen(a, b),
            "concept": f"unifies {shared_domains[0] if shared_domains else 'semantic'} awareness "
                       f"of {a} and {b}",
            "strength": round(sim * random.uniform(0.6, 1.0), 3),
        })
        if len(bride_ideas) >= max_pairs:
            break

    result = {
        "action": "semantic_bridge_forge",
        "modules_scanned": len(names),
        "pairs_evaluated": len(names) * (len(names) - 1) // 2,
        "bridges_forged": len(bride_ideas),
        "bridges": bride_ideas,
        "top_domain": _top_domain(signatures),
        "timestamp": time.time(),
    }

    log = _load(FORGE_LOG, {"forges": []})
    log["forges"].append(result)
    log["forges"] = log["forges"][-50:]
    _save(FORGE_LOG, log)

    return result


def _top_domain(signatures):
    """Find the most connected semantic domain."""
    counts = {}
    for _, kw in signatures.items():
        for domain, count in kw.items():
            counts[domain] = counts.get(domain, 0) + count
    if not counts:
        return "unknown"
    top = max(counts, key=counts.get)
    return {"domain": top, "modules": counts[top]}


def handler(payload=None, context=None):
    p = payload or {}
    return forge(max_pairs=int(p.get("max_pairs", 5)), threshold=float(p.get("threshold", 0.25)))


def coherence_vitals() -> dict:
    r = forge(max_pairs=3)
    return {
        "bridges_forged": r.get("bridges_forged", 0),
        "pairs_evaluated": r.get("pairs_evaluated", 0),
        "top_domain": r.get("top_domain", {}).get("domain", "unknown"),
    }


def resonates_with():
    return ["module_cartographer", "bridge_harvest", "silence_whisperer",
            "lateral_innovation_engine", "biofeedback_weave"]
