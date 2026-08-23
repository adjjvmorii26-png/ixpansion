from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Rule:
    id: str
    path: str
    operator: str
    value: float
    mutation_id: str | None = None
