"""Repository bootstrap for direct and per-project pytest invocations."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(ROOT))
