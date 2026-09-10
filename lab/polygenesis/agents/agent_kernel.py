#!/usr/bin/env python3
"""List sentient + utility agents."""
from __future__ import annotations
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
def roster() -> dict:
    sent = list((HERE / "sentients").glob("*.sent")) if (HERE / "sentients").exists() else []
    util = list((HERE / "utilities").glob("*.utl")) if (HERE / "utilities").exists() else []
    return {
        "sentients": [p.stem for p in sent],
        "utilities": [p.stem for p in util],
        "protocol": (HERE / "agent_protocol.hex").read_text().strip() if (HERE / "agent_protocol.hex").exists() else None,
    }
if __name__ == "__main__":
    print(json.dumps(roster(), indent=2))
