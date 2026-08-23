from __future__ import annotations
import json
from pathlib import Path
from core.config_loader import load_config
from expansion.models.seed import Seed


def load_seeds(path: Path) -> list[Seed]:
    data = load_config(path)
    raw = data.get("seeds", [])
    if isinstance(raw, dict):
        raw = [dict(value, id=name) for name, value in raw.items()]
    if path.suffix == ".json":
        payload = json.loads(json.dumps(raw))
    else:
        payload = raw
    if not isinstance(payload, list):
        raise ValueError("seeds must be a list")
    return [Seed(id=str(item["id"]), rules=list(item.get("rules", [])), mutations=list(item.get("mutations", []))) for item in payload]
