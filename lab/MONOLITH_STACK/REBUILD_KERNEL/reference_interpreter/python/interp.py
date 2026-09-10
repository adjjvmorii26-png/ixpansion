#!/usr/bin/env python3
import json
def run(code):
    sealed=ethics=False
    for op in code:
        if op==2: sealed=True
        elif op==3: ethics=True
        elif op==255: break
    return {"ok": ethics and sealed, "sealed": sealed, "ethics": ethics}
if __name__=="__main__":
    print(json.dumps(run([3,2,255]), indent=2))
