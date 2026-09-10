#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
def roster() -> dict:
    neg = list((HERE / "negotiators").glob("*.neg")) if (HERE / "negotiators").exists() else []
    obs = list((HERE / "observers").glob("*.obs")) if (HERE / "observers").exists() else []
    return {
        "negotiators": [p.stem for p in neg],
        "observers": [p.stem for p in obs],
        "protocol": (HERE / "agent_protocol.hex").read_text().strip() if (HERE / "agent_protocol.hex").exists() else None,
    }
if __name__ == "__main__":
    print(json.dumps(roster(), indent=2))
