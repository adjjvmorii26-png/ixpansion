#!/usr/bin/env python3
import hashlib, json
from datetime import datetime, timezone
def branch(label: str = "B") -> dict:
    h = hashlib.sha256(f"{label}-{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:12]
    return {"branch": label, "id": h, "ok": True}
if __name__ == "__main__":
    import sys
    print(json.dumps(branch(sys.argv[1] if len(sys.argv) > 1 else "B")))
