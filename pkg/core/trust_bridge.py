#!/usr/bin/env python3
"""Sync EMA reputation into VSA router trust weights."""
from __future__ import annotations
from typing import Any

def sync_ema_to_vsa(ema: Any, vsa_router: Any) -> dict:
    snap = {}
    if hasattr(ema, "snapshot"):
        raw = ema.snapshot()
        if isinstance(raw, dict):
            scores = raw.get("scores") or raw.get("nodes") or raw
            if isinstance(scores, dict):
                for k, v in scores.items():
                    try:
                        val = float(v) if not isinstance(v, dict) else float(v.get("score", 0.5))
                    except (TypeError, ValueError):
                        val = 0.5
                    snap[str(k)] = val
                    if hasattr(vsa_router, "trust") and isinstance(getattr(vsa_router, "trust", None), dict):
                        vsa_router.trust[str(k)] = val
    return snap
