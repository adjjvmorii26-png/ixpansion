from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Mutation:
    target: str
    field: str
    operation: str
    value: Any = 1

    def __post_init__(self) -> None:
        if self.operation not in {"set", "add", "multiply", "append"}:
            raise ValueError(f"unknown mutation operation: {self.operation}")
