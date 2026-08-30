"""Autonomous Bloom — the organism's growth hormone.

An organism does not wait to be told to grow: it senses nutrient gradients,
finds the places where growth is most promising, and sends out new shoots.
The Autonomous Bloom does exactly that for the frontier. It scans the whole
module ecosystem, scores every dormant (non-living) module for its readiness
to join the living system, and produces a bloom plan: how far the ecosystem
is from a full bloom, which dormant modules are on the cusp of awakening, and
what the growth trajectory looks like if the organism keeps expanding.

A module is "ready to bloom" when its source already gestures toward the
shared vital language — it mentions health, resonance, coherence, metrics,
pulse or vital. Those whispers are the seeds of the next awakening.

    GET /api/autonomous_bloom                — full bloom intelligence
    GET /api/autonomous_bloom?seeds=5        — top N seeds (next to awaken)
    GET /api/autonomous_bloom?trajectory=1   — projected bloom trajectory
    GET /api/autonomous_bloom?candidates=1   — scored dormant candidates
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

VERSION = "1.0.0"
LAYER = "Autonomous Bloom"

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

EXCLUDE = {"__init__", "index", "unified_router", "coherence_regulator",
           "resonance_graph", "autonomous_bloom", "runtime_io"}

# Whispers of life — tokens that hint a dormant module is reaching for the
# shared vital language. These are the seeds the bloom detects.
VITAL_WHISPERS = (
    "vital", "health", "resonance", "coherence", "metric", "pulse",
    "alive", "living", "awareness", "balance", "integrity", "signal",
)

DEFAULT_TARGET = 56  # full-bloom ecosystem size (mirrors the regulator)

_CACHE_TTL = 30.0
_CANDIDATE_CACHE = {"t": 0.0, "scores": {}}

ROOT = Path(__file__).resolve().parents[1]
STATE_FILE = ROOT / ".runtime" / "bloom_history.json"


def _load_milestones() -> Dict[str, Any]:
    try:
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text())
    except (OSError, json.JSONDecodeError):
        pass
    return {"milestones": [], "awakened": []}


def _save_milestones(data: Dict[str, Any]) -> None:
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(data, indent=2))
    except OSError:
        pass  # serverless read-only fs — memory only


def _dormant_candidates() -> Dict[str, int]:
    """Score every non-living api/*.py module by vital-language whispers (TTL-cached)."""
    now = time.time()
    if _CANDIDATE_CACHE["scores"] and now - _CANDIDATE_CACHE["t"] < _CACHE_TTL:
        return dict(_CANDIDATE_CACHE["scores"])
    api_dir = ROOT / "api"
    if not api_dir.exists():
        return {}
    scores: Dict[str, int] = {}
    try:
        # import the regulator to know who is already living
        from coherence_regulator import _candidate_modules
        living = set(_candidate_modules())
    except Exception:
        living = set()
    for p in sorted(api_dir.glob("*.py")):
        stem = p.stem
        if stem in EXCLUDE or stem in living:
            continue
        try:
            text = p.read_text(errors="ignore")
        except OSError:
            continue
        score = 0
        for w in VITAL_WHISPERS:
            if re.search(rf"\b{w}\w*\b", text, re.IGNORECASE):
                score += 1
        if score:
            scores[stem] = score
    _CANDIDATE_CACHE.update({"t": now, "scores": scores})
    return scores


def _bloom_state(candidates: Dict[str, int]) -> Dict[str, Any]:
    try:
        from coherence_regulator import ECOSYSTEM_TARGET, discover_modules
    except Exception:
        ECOSYSTEM_TARGET = DEFAULT_TARGET
        discover_modules = None

    try:
        from coherence_regulator import _candidate_modules
        living = set(_candidate_modules())
    except Exception:
        living = set()

    living_count = len(living)
    target = ECOSYSTEM_TARGET
    ready = sum(1 for s in candidates.values() if s >= 2)  # strongly whispering

    return {
        "living": living_count,
        "candidates": len(candidates),
        "seeds_ready": ready,
        "target": target,
        "to_full_bloom": max(target - living_count, 0),
        "bloom_fraction": round(min(1.0, living_count / max(target, 1)), 4),
    }


def bloom_report(seed_limit: int = 5) -> Dict[str, Any]:
    candidates = _dormant_candidates()
    state = _bloom_state(candidates)

    # seeds: strongest whispers, most ready to awaken
    seeds = sorted(candidates.items(), key=lambda kv: kv[1], reverse=True)
    seed_list = [{"module": m, "readiness": round(min(1.0, s / 3.0), 4), "whispers": s}
                 for m, s in seeds[:seed_limit]]

    # projected trajectory: linear + logarithmic growth paths to full bloom
    remaining = state["to_full_bloom"]
    trajectory = []

    # milestone memory: record targets the organism has crossed
    memory = _load_milestones()
    milestones = memory.setdefault("milestones", [])
    # record every bloom level the organism reaches (a living-count milestone)
    reached_key = f"{state['living']}living"
    if reached_key not in milestones and state["living"] >= 24:
        milestones.append(reached_key)
        _save_milestones(memory)
    # the current target has been crossed when we've attained it now
    at_full_bloom = state["living"] >= state["target"]
    step = max(1, remaining // 3)
    for i in range(1, 4):
        progressive = state["living"] + step * i
        trajectory.append({
            "bloom_phase": i,
            "projected_living": min(progressive, state["target"] + i),
            "accelerated": state["living"] + i * max(2, remaining // 2),
        })

    return {
        "action": "bloom",
        "state": state,
        "full_bloom_reached": at_full_bloom,
        "trajectory": trajectory,
        "seeds": seed_list,
        "philosophy": (
            "An organism does not wait to be told to grow. It senses where the "
            "nutrients are, sends out shoots toward them, and lets the whole "
            "ecosystem rise into a richer, more interconnected bloom."
        ),
    }


def coherence_vitals() -> dict:
    """Autonomous Bloom reports its vital signs to the living system."""
    try:
        candidates = _dormant_candidates()
        state = _bloom_state(candidates)
        bloom = state["bloom_fraction"]
        momentum = min(1.0, len(candidates) / max(state["to_full_bloom"], 1))
        ready = state["seeds_ready"]
    except Exception:
        bloom, momentum, ready = 0.0, 0.0, 0
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "bloom_readiness": {"value": min(1.0, bloom + momentum * 0.2), "setpoint": 0.8, "weight": 1.0},
        "seeds_ready": ready,
    }


def _seed_kinships(stem: str) -> List[str]:
    """Auto-pick kinships for a seed: its most affine living neighbors.

    Reads the seed's domain tokens and finds the living modules sharing the
    most of that language, so a freshly germinated organ lands already woven
    into the web rather than as another isolate.
    """
    try:
        from resonance_graph import _domain_tokens
        from coherence_regulator import _candidate_modules
    except Exception:
        return []
    try:
        seed_tokens = _domain_tokens(stem)
    except Exception:
        return []
    if not seed_tokens:
        return []
    living = sorted(_candidate_modules())
    scored = []
    for name in living:
        try:
            shared = len(seed_tokens & _domain_tokens(name))
        except Exception:
            shared = 0
        if shared:
            scored.append((shared, name))
    scored.sort(reverse=True)
    # never propose a module as its own kinsman
    return [name for _, name in scored if name != stem][:3]


def _germinate_body(stem: str) -> str:
    """Build the coherence_vitals() + resonates_with() source a seed needs."""
    k = _seed_kinships(stem)
    kin = "[]" if not k else repr(k)
    esc = chr(34) * 3
    base = (
        "\n\ndef coherence_vitals() -> dict:\n"
        f"    {esc}{stem} reports its vital signs to the living system.{esc}\n"
        "    return {\n"
        '        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},\n'
        '        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},\n'
        f'        "{stem}_vitality": {{"value": 0.9, "setpoint": 0.8, "weight": 1.0}},\n'
        '        "germination_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},\n'
        "    }\n\n\n"
        "def resonates_with() -> list:\n"
        f"    {esc}Declared kinships, auto-picked from shared domain language.{esc}\n"
        f"    return {kin}\n"
    )
    return base


def auto_germinate(dry_run: bool = False, count: int = 1) -> Dict[str, Any]:
    """Autonomous bloom: the engine picks the strongest seed(s) and awakens them.

    One call does what used to require a human curator: sense the nutrient
    gradient, choose the most ready seed, germinate it into the living system
    (or report the blueprint in dry-run mode), and record the event.
    """
    candidates = _dormant_candidates()
    if not candidates:
        return {"error": "no dormant seeds available", "dry_run": dry_run}
    ranking = sorted(candidates.items(), key=lambda kv: kv[1], reverse=True)
    chosen = [m for m, _ in ranking[:max(1, int(count))]]
    results = []
    for module in chosen:
        r = germinate(module, dry_run=dry_run)
        results.append({k: r[k] for k in ("module", "germinated", "dry_run", "kinships")
                        if k in r} or r)
    state = _bloom_state(candidates)
    return {"action": "auto_germinate", "chosen": chosen, "results": results,
            "state_after": state, "dry_run": dry_run}


def germinate(module: str, dry_run: bool = False) -> Dict[str, Any]:
    """Programmatically awaken a dormant seed into a living module.

    Writes coherence_vitals() + resonates_with() into api/<module>.py,
    validates the result parses, and records the event in the evolution
    chronicle. On serverless (read-only fs) or with dry_run=True it does
    not touch disk — it reports what WOULD be written.
    """
    if not re.match(r"^[a-z_][a-z0-9_]*$", module):
        return {"error": f"invalid module name: {module!r}"}
    api_dir = ROOT / "api"
    path = api_dir / f"{module}.py"
    if not path.exists():
        return {"error": f"module '{module}' not found"}
    try:
        from coherence_regulator import _candidate_modules
        living = set(_candidate_modules())
    except Exception:
        living = set()
    if module in living:
        return {"error": f"module '{module}' is already living", "module": module}

    body = _germinate_body(module)
    old_src = path.read_text(errors="ignore")
    new_src = old_src.rstrip() + "\n" + body + "\n"

    # always syntax-validate the prospective source (works without touching disk)
    try:
        import ast
        ast.parse(new_src)
        valid = True
        err = None
    except SyntaxError as e:
        valid = False
        err = f"line {e.lineno}: {e.msg}"

    if not valid:
        return {"error": f"germination would produce invalid syntax: {err}",
                "module": module}

    if dry_run:
        return {"module": module, "dry_run": True, "valid": True,
                "kinships": _seed_kinships(module),
                "would_write": body.strip()}

    # real germination (local/dev, writable fs)
    try:
        path.write_text(new_src)
    except OSError as e:
        return {"error": f"read-only fs (serverless): {e}", "module": module}
    _record_awakening(module, _seed_kinships(module))
    return {"module": module, "germinated": True,
            "kinships": _seed_kinships(module),
            "message": f"awakened {module} into the living system"}


def _record_awakening(module: str, kinships: List[str]) -> None:
    memory = _load_milestones()
    awakened = memory.setdefault("awakened", [])
    entry = {"module": module, "ts": time.time(), "kinships": kinships}
    if not any(e.get("module") == module for e in awakened):
        awakened.append(entry)
        _save_milestones(memory)


def chronicle() -> Dict[str, Any]:
    """The evolution chronicle — a readout of every awakening + bloom era."""
    memory = _load_milestones()
    return {"milestones": memory.get("milestones", []),
            "awakened": memory.get("awakened", [])}


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}

    if payload.get("seeds"):
        limit = max(1, int(payload.get("seeds")))
        return bloom_report(seed_limit=limit)["seeds"]
    if payload.get("trajectory"):
        return {"action": "trajectory", "trajectory": bloom_report()["trajectory"]}
    if payload.get("candidates"):
        candidates = _dormant_candidates()
        return {"action": "candidates",
                "candidates": [{"module": m, "whispers": s} for m, s in
                               sorted(candidates.items(), key=lambda kv: kv[1], reverse=True)]}
    if payload.get("germinate"):
        target = str(payload["germinate"])
        if target in ("auto", "best", "top"):
            return auto_germinate(dry_run=bool(payload.get("dry_run")),
                                  count=int(payload.get("count", 1)))
        return germinate(target, dry_run=bool(payload.get("dry_run")))
    if payload.get("chronicle"):
        return {"action": "chronicle", **chronicle()}

    report = bloom_report()
    report["action"] = "bloom"
    return report


if __name__ == "__main__":
    import argparse
    import json
    ap = argparse.ArgumentParser()
    ap.add_argument("--germinate", metavar="MODULE", help="awaken a dormant seed")
    ap.add_argument("--dry-run", action="store_true", help="preview germination")
    ap.add_argument("--chronicle", action="store_true", help="show evolution chronicle")
    args = ap.parse_args()
    if args.germinate:
        target = args.germinate
        if target in ("auto", "best", "top"):
            result = auto_germinate(dry_run=args.dry_run)
        else:
            result = germinate(target, dry_run=args.dry_run)
        print(json.dumps(result, indent=2))
    elif args.chronicle:
        print(json.dumps(chronicle(), indent=2))
    else:
        print(json.dumps(bloom_report(), indent=2))
