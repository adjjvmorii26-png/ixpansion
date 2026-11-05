#!/usr/bin/env python3
"""Compatibility entry point for the canonical scripts/skill_lab.py implementation.

Keep one implementation only. The script directory owns the CLI and testable
functions; this module preserves the historical import and command path.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent / "scripts"
_IMPL_PATH = _SCRIPT_DIR / "skill_lab.py"
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

_spec = importlib.util.spec_from_file_location("_skill_systems_foundry_impl", _IMPL_PATH)
if _spec is None or _spec.loader is None:
    raise ImportError(f"cannot load canonical skill lab implementation: {_IMPL_PATH}")
_impl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_impl)

for _name in dir(_impl):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_impl, _name)

if __name__ == "__main__":
    raise SystemExit(_impl.main())
