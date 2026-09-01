#!/usr/bin/env python3
import json
def regenerate(module: str = "manifest") -> dict:
    return {"regenerated": module, "ok": True}
if __name__ == "__main__":
    import sys
    print(json.dumps(regenerate(sys.argv[1] if len(sys.argv) > 1 else "manifest")))
