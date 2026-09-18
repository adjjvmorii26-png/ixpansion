"""Wave 768 — hush_compass.

Mycelial truths record WHAT the organism believes.
Hush compass records WHICH of those beliefs must stay unsaid.

Silence is the product surface. Speech is waste heat.
Charge builds on a bearing until a caption is the only legal discharge.
Unused utterance compresses into memory (doctrine: compression is memory).
"""
from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "wave768_hush_compass.json"
WAVE = 768
NAME = "hush_compass"
MAX_BEARINGS = 32
CHARGE_CAP = 1.0
COMPRESS_THRESHOLD = 0.35


def _load() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            pass
    return {
        "wave": WAVE,
        "name": NAME,
        "bearings": [],
        "memory": [],
        "captions": [],
        "status": "seed",
    }


def _save(state: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(state, indent=2))


def _now() -> str:
    return datetime.datetime.now(datetime.UTC).isoformat()


def _find(state: dict, subject: str):
    for b in state.get("bearings", []):
        if b["subject"] == subject:
            return b
    return None


def handler(req: dict) -> dict:
    action = req.get("action", "status")
    state = _load()

    if action == "status":
        bearings = state.get("bearings", [])
        loudest = max(bearings, key=lambda b: b.get("charge", 0.0), default=None)
        return {
            "bearings": len(bearings),
            "memory_cells": len(state.get("memory", [])),
            "captions": len(state.get("captions", [])),
            "loudest_hush": loudest and {
                "subject": loudest["subject"],
                "charge": loudest["charge"],
                "bearing": loudest["bearing"],
            },
            "surface": "silence",
        }

    if action == "bear":
        subject = str(req.get("subject", "")).strip()
        bearing = str(req.get("bearing", "withhold")).strip() or "withhold"
        if not subject:
            return {"error": "subject required"}
        bearings = state.setdefault("bearings", [])
        existing = _find(state, subject)
        if existing:
            existing["charge"] = round(min(CHARGE_CAP, existing.get("charge", 0.2) + 0.15), 4)
            existing["bearing"] = bearing
            existing["last"] = _now()
            _save(state)
            return {"bearing": existing, "note": "reinforced hush"}
        if len(bearings) >= MAX_BEARINGS:
            return {"error": "compass full — compress unused speech first"}
        item = {
            "subject": subject,
            "bearing": bearing,
            "charge": 0.2,
            "born_wave": WAVE,
            "last": _now(),
        }
        bearings.append(item)
        _save(state)
        return {"bearing": item, "born": True}

    if action == "listen":
        # Read without discharging. Product surface stays silent.
        subject = str(req.get("subject", "")).strip()
        bearings = state.get("bearings", [])
        if subject:
            bearings = [b for b in bearings if b["subject"] == subject]
        return {"bearings": bearings, "count": len(bearings), "discharged": False}

    if action == "compress":
        # Unused utterance (charge below threshold) becomes memory.
        kept, compressed = [], []
        for b in state.get("bearings", []):
            if b.get("charge", 0) < COMPRESS_THRESHOLD:
                cell = {
                    "subject": b["subject"],
                    "bearing": b["bearing"],
                    "residue": b.get("charge", 0),
                    "at": _now(),
                }
                state.setdefault("memory", []).append(cell)
                compressed.append(b["subject"])
            else:
                kept.append(b)
        state["bearings"] = kept
        _save(state)
        return {"compressed": compressed, "memory_cells": len(state.get("memory", []))}

    if action == "caption":
        # Only legal discharge: a short caption, never a speech.
        subject = str(req.get("subject", "")).strip()
        text = str(req.get("text", "")).strip()
        if not subject:
            return {"error": "subject required"}
        if len(text) > 140:
            return {"error": "caption too long — silence is the product surface"}
        if not text:
            text = f"hush holds {subject}"
        b = _find(state, subject)
        charge = b.get("charge", 0.0) if b else 0.0
        cap = {
            "subject": subject,
            "text": text,
            "charge_spent": charge,
            "at": _now(),
        }
        state.setdefault("captions", []).append(cap)
        if b:
            b["charge"] = 0.05
            b["last"] = _now()
        _save(state)
        return {"caption": cap, "surface": "silence", "discharged": True}

    return {"error": f"unknown action: {action}"}


def coherence_vitals() -> dict:
    state = _load()
    bearings = state.get("bearings", [])
    charge = sum(b.get("charge", 0.0) for b in bearings)
    return {
        "wave": WAVE,
        "name": NAME,
        "layer": "organ",
        "status": "active",
        "bearings": len(bearings),
        "memory_cells": len(state.get("memory", [])),
        "captions": len(state.get("captions", [])),
        "held_charge": round(charge, 4),
        "resonance": 0.83,
        "module_health": {"value": 0.88, "setpoint": 0.80, "weight": 1.0},
    }


def resonates_with() -> list:
    return [
        "mycelial_truths",
        "silence_capacitor",
        "continuity_weaver",
        "coherence_regulator",
        "epoch_engine",
    ]
