"""Serverless-safe state paths.
Vercel source files are treated as immutable; transient writes belong in /tmp.
"""
from __future__ import annotations
import os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
LOCAL_STATE_DIR = ROOT / "data"
EPHEMERAL_STATE_DIR = Path(os.environ.get("IXPANSION_STATE_DIR", "/tmp/ixpansion"))
def state_dir() -> Path:
    if os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"):
        EPHEMERAL_STATE_DIR.mkdir(parents=True, exist_ok=True)
        return EPHEMERAL_STATE_DIR
    LOCAL_STATE_DIR.mkdir(parents=True, exist_ok=True)
    return LOCAL_STATE_DIR
def state_path(*parts: str) -> Path:
    return state_dir().joinpath(*parts)
