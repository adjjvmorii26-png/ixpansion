#!/usr/bin/env python3
import json, hashlib
from datetime import datetime, timezone
def construct(spec: str = "stub") -> dict:
    artifact = hashlib.sha256(f"{spec}-{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:12]
    return {"agent": "builder", "spec": spec, "artifact": artifact, "ok": True}
if __name__ == "__main__":
    import sys
    print(json.dumps(construct(sys.argv[1] if len(sys.argv) > 1 else "stub")))
