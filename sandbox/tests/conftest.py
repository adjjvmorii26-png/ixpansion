"""Ensure the sandbox package directory is importable for pytest runs.

The sandbox modules import each other with flat, top-level names (e.g.
``from idea_lab import IdeaLab``) rather than as a package, matching the
style of the sibling IXPANSION modules at the repository root. This puts
``sandbox/`` itself on ``sys.path`` so both ``pytest`` and
``python -m unittest discover -s sandbox/tests`` can resolve those imports
regardless of the current working directory.
"""

import sys
from pathlib import Path

_SANDBOX_DIR = Path(__file__).resolve().parent.parent
if str(_SANDBOX_DIR) not in sys.path:
    sys.path.insert(0, str(_SANDBOX_DIR))
