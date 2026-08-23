"""Grows new directories and modules automatically — the engine expands itself."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any


class FractalGrowth:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self._created: list[str] = []
        self._depth_limit = 4

    def grow(self, pattern: str = "branch", branching: int = 2, depth: int = 2) -> list[str]:
        """Create a fractal directory structure under root."""
        created = []

        def _grow(parent: Path, current_depth: int) -> None:
            if current_depth >= depth:
                return
            for i in range(branching):
                dirname = f"{pattern}_{current_depth}_{i}"
                new_dir = parent / dirname
                if not new_dir.exists():
                    new_dir.mkdir(parents=True, exist_ok=True)
                    init_file = new_dir / "__init__.py"
                    init_file.touch()
                    created.append(str(new_dir.relative_to(self.root)))

                _grow(new_dir, current_depth + 1)

        _grow(self.root, 0)
        self._created.extend(created)
        return created

    @property
    def total_created(self) -> int:
        return len(self._created)
