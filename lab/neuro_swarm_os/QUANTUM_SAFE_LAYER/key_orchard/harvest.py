#!/usr/bin/env python3
import hashlib, json
from datetime import datetime, timezone
def harvest() -> dict:
    seed = datetime.now(timezone.utc).isoformat()
    return {"key_id": hashlib.sha256(seed.encode()).hexdigest()[:16], "policy": "rotate-demo"}
if __name__ == "__main__":
    print(json.dumps(harvest()))
