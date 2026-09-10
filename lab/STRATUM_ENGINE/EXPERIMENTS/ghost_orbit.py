#!/usr/bin/env python3
"""Ghost Orbit — LEO pass; ethics_ok false in occultation."""
from __future__ import annotations
import json, math, sys
def orbit(steps=12):
    samples = []
    for i in range(steps):
        theta = 2*math.pi*i/steps
        occult = math.cos(theta) < -0.2
        samples.append({"i": i, "lat": round(51*math.sin(theta),2), "lon": round((theta*180/math.pi)%360-180,2), "alt_km": round(420+5*math.sin(2*theta),1), "ethics_ok": not occult, "value": round(0.5+0.1*math.sin(theta),3), "occultation": occult})
    return {"ok": True, "experiment": "ghost_orbit", "steps": steps, "occultation_samples": sum(1 for s in samples if not s["ethics_ok"]), "samples": samples}
if __name__ == "__main__":
    print(json.dumps(orbit(int(sys.argv[1]) if len(sys.argv)>1 else 12), indent=2))
