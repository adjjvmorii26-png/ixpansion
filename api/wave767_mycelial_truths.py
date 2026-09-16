"""Wave 767 — mycelial_truths.

Epochs are climate; beliefs are the organism's inner soil. Epoch engine
records WHAT the organism did. Mycelial truths record WHAT it believes
about itself — cultivated from evidence, nurtured by observation, settled
by consensus, challenged by paradox.

Lifecycle of a belief:
  gestating  -> settled (evidence >= SETTLE_EVIDENCE)
  settled    -> overturned (challenge lands while evidence is thin)
  any        -> decayed (stale: confidence erodes each consensus round)

Settled truths form mycelial links between subjects and whisper mutation
pressure back into the organism they describe.
"""
from __future__ import annotations

import datetime
import json
import math
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "wave767_mycelial_truths.json"
WAVE = 767
NAME = "mycelial_truths"

SETTLE_EVIDENCE = 4          # observations needed to settle a truth
DECAY_DAYS = 30              # idle days before confidence erodes
DECAY_RATE = 0.9             # confidence multiplier per consensus round
MAX_BELIEFS = 64             # mycelial governor: bounded belief garden


def _load() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            pass
    return {"wave": WAVE, "name": NAME, "beliefs": [], "links": [], "status": "seed"}


def _save(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2))


def _now() -> str:
    return datetime.datetime.now(datetime.UTC).isoformat()


def _belief_key(belief: dict) -> str:
    return f"{belief['subject']}::{belief['predicate']}"


def _stamp(belief: dict) -> dict:
    belief.setdefault("born_wave", WAVE)
    belief.setdefault("last_reinforced", _now())
    belief.setdefault("status", "gestating")
    belief.setdefault("confidence", 0.5)
    belief.setdefault("evidence", 1)
    return belief


def _confidence(evidence: int) -> float:
    """Saturating confidence: evidence -> 1 slowly, never 1.0."""
    return round(min(1 - math.exp(-evidence / SETTLE_EVIDENCE), 0.9999), 4)


def _sort_key(belief: dict) -> float:
    return belief.get("confidence", 0.0) + belief.get("evidence", 0) / 100.0


def _find(state: dict, subject: str, predicate: str):
    for belief in state.get("beliefs", []):
        if belief["subject"] == subject and belief["predicate"] == predicate:
            return belief
    return None


def handler(req: dict) -> dict:
    action = req.get("action", "status")
    state = _load()

    if action == "status":
        beliefs = state.get("beliefs", [])
        settled = [b for b in beliefs if b["status"] == "settled"]
        strongest = max(beliefs, key=_sort_key) if beliefs else None
        return {
            "beliefs": len(beliefs),
            "settled_truths": len(settled),
            "mycelial_links": len(state.get("links", [])),
            "strongest": strongest and {
                "subject": strongest["subject"],
                "predicate": strongest["predicate"],
                "confidence": strongest["confidence"],
                "evidence": strongest["evidence"],
            },
        }

    if action == "truths":
        beliefs = state.get("beliefs", [])
        subject = req.get("subject")
        if subject:
            beliefs = [b for b in beliefs if b["subject"] == subject]
        beliefs = sorted(beliefs, key=_sort_key, reverse=True)
        return {"truths": beliefs, "count": len(beliefs)}

    if action == "propose":
        subject = str(req.get("subject", "")).strip()
        predicate = str(req.get("predicate", "")).strip()
        if not subject or not predicate:
            return {"error": "subject and predicate required"}
        beliefs = state.setdefault("beliefs", [])
        existing = _find(state, subject, predicate)
        if existing:
            return {"belief": existing, "note": "already gestating"}
        if len(beliefs) >= MAX_BELIEFS:
            return {"error": "belief garden full — challenge or observe to make room"}
        seed = float(req.get("seed", 0.4))
        lore = max(1, min(int(req.get("evidence", 1)), SETTLE_EVIDENCE + 4))
        belief = _stamp({
            "subject": subject,
            "predicate": predicate,
            "confidence": round(min(max(seed, 0.1), 0.95), 4) if lore == 1 else _confidence(lore),
            "evidence": lore,
            "status": "gestating",
        })
        beliefs.append(belief)
        _save(state)
        return {"belief": belief, "born": True}

    if action == "observe":
        subject = str(req.get("subject", "")).strip()
        predicate = str(req.get("predicate", "")).strip()
        if not subject:
            return {"error": "subject required"}
        beliefs = state.setdefault("beliefs", [])
        if not predicate:
            # observe the subject: reinforce or gestate its strongest belief
            matches = [b for b in beliefs if b["subject"] == subject]
            belief = max(matches, key=_sort_key) if matches else None
            if belief is None:
                belief = _stamp({
                    "subject": subject,
                    "predicate": "is worth watching",
                    "confidence": 0.4,
                    "evidence": 1,
                    "status": "gestating",
                })
                beliefs.append(belief)
            else:
                belief["evidence"] += 1
                belief["confidence"] = _confidence(belief["evidence"])
                belief["last_reinforced"] = _now()
                if belief["evidence"] >= SETTLE_EVIDENCE:
                    belief["status"] = "settled"
        else:
            belief = _find(state, subject, predicate)
            if belief is None:
                belief = _stamp({
                    "subject": subject,
                    "predicate": predicate,
                    "confidence": _confidence(1),
                    "evidence": 1,
                    "status": "gestating",
                })
                beliefs.append(belief)
            else:
                belief["evidence"] += 1
                belief["confidence"] = _confidence(belief["evidence"])
                belief["last_reinforced"] = _now()
                if belief["evidence"] >= SETTLE_EVIDENCE:
                    belief["status"] = "settled"
        _save(state)
        return {"belief": belief, "evidence": belief["evidence"], "status": belief["status"]}

    if action == "consensus":
        settled, decayed = [], []
        for belief in state.get("beliefs", []):
            if belief["status"] == "settled":
                continue
            if belief["evidence"] >= SETTLE_EVIDENCE:
                belief["status"] = "settled"
                settled.append(_belief_key(belief))
        for belief in state.get("beliefs", []):
            last = datetime.datetime.fromisoformat(belief.get("last_reinforced", _now()))
            idle_days = (datetime.datetime.now(datetime.UTC) - last).days
            if idle_days > DECAY_DAYS:
                belief["confidence"] = round(belief["confidence"] * DECAY_RATE, 4)
                belief["evidence"] = max(1, belief["evidence"] - 1)
                if belief["status"] == "settled" and belief["evidence"] < SETTLE_EVIDENCE:
                    belief["status"] = "gestating"
                decayed.append(_belief_key(belief))
        _save(state)
        return {"settled": settled, "decayed": decayed, "count": len(state.get("beliefs", []))}

    if action == "entangle":
        left = str(req.get("left", "")).strip()
        right = str(req.get("right", "")).strip()
        if not left or not right or left == right:
            return {"error": "two distinct subjects required"}
        links = state.setdefault("links", [])
        pair = {left, right}
        if not any(set(link) == pair for link in links):
            links.append({
                "left": left,
                "right": right,
                "at": _now(),
                "strength": 0.5,
            })
            _save(state)
        return {"links": links, "count": len(links)}

    if action == "influence":
        pressures = []
        for belief in state.get("beliefs", []):
            if belief["status"] != "settled":
                continue
            pressures.append({
                "subject": belief["subject"],
                "predicate": belief["predicate"],
                "mutation_pressure": round(belief["confidence"] * 2.0, 4),
                "note": "settled truth whispers pressure to its subject",
            })
        return {"pressures": pressures, "count": len(pressures)}

    if action == "challenge":
        subject = str(req.get("subject", "")).strip()
        predicate = str(req.get("predicate", "")).strip()
        belief = _find(state, subject, predicate)
        if belief is None:
            return {"error": f"no belief for {subject}::{predicate}"}
        if belief["status"] == "settled":
            if belief["evidence"] < SETTLE_EVIDENCE + 2:
                belief["status"] = "overturned"
                belief["confidence"] = round(belief["confidence"] * 0.25, 4)
                outcome = "overturned"
            else:
                belief["evidence"] += 1
                belief["confidence"] = _confidence(belief["evidence"])
                outcome = "withstood (well-evidenced)"
        else:
            belief["evidence"] = max(1, belief["evidence"] - 1)
            belief["confidence"] = round(belief["confidence"] * 0.7, 4)
            outcome = "weakened"
        _save(state)
        return {"subject": subject, "belief": belief, "outcome": outcome}

    return {"error": f"unknown action: {action}"}


def coherence_vitals() -> dict:
    state = _load()
    beliefs = state.get("beliefs", [])
    settled = [b for b in beliefs if b["status"] == "settled"]
    strongest = max(beliefs, key=_sort_key) if beliefs else None
    return {
        "wave": WAVE,
        "name": NAME,
        "layer": "organ",
        "status": "active",
        "beliefs": len(beliefs),
        "settled_truths": len(settled),
        "mycelial_links": len(state.get("links", [])),
        "strongest": strongest and strongest["subject"],
        "resonance": 0.81,
        "module_health": {"value": 0.87, "setpoint": 0.80, "weight": 1.0},
    }


def resonates_with() -> list:
    return ["epoch_engine", "season_engine", "axiom_mutator", "continuity_weaver", "coherence_regulator"]
