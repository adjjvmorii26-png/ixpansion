#!/usr/bin/env python3
import json
def merge(a: str = "A", b: str = "B") -> dict:
    return {"merged": f"{a}+{b}", "policy": "last-writer-wins-demo", "ok": True}
if __name__ == "__main__":
    import sys
    a = sys.argv[1] if len(sys.argv) > 1 else "A"
    b = sys.argv[2] if len(sys.argv) > 2 else "B"
    print(json.dumps(merge(a, b)))
