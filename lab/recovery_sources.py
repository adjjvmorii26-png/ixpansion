"""Shared source-isolation boundary for the recovery chain."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from lab.runtime_vault import ledger_path


RECOVERY_DERIVED_LEDGERS = {
    "paradox-resolutions.jsonl",
    "repair-dreams.jsonl",
    "repair-theater.jsonl",
    "recovery-quorums.jsonl",
    "recovery-atlases.jsonl",
    "recovery-treaties.jsonl",
    "recovery-dossiers.jsonl",
}


def source_ledgers(explicit: list[Path] | None = None) -> list[Path]:
    """Resolve immutable input ledgers or all non-derived ledgers in the vault."""
    if explicit is None:
        directory = ledger_path().parent
        return sorted(
            path for path in directory.glob("*.jsonl")
            if path.name not in RECOVERY_DERIVED_LEDGERS
        )
    paths = sorted({Path(item).resolve() for item in explicit})
    for path in paths:
        if not path.is_file():
            raise ValueError(f"ledger does not exist: {path}")
    return paths
