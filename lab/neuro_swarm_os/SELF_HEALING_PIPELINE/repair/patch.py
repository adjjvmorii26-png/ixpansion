#!/usr/bin/env python3
import json
def patch(target: str = "stub") -> dict:
    return {"patched": target, "mode": "soft", "ok": True}
if __name__ == "__main__":
    import sys
    print(json.dumps(patch(sys.argv[1] if len(sys.argv) > 1 else "stub")))
