from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Seed:
    id: str
    rules: list[dict[str, Any]] = field(default_factory=list)
    mutations: list[dict[str, Any]] = field(default_factory=list)
