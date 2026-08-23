#!/usr/bin/env python3
"""Find the point least supported by the local constellation."""
from __future__ import annotations
import argparse, hashlib, json, math


def inspect(points: list[dict] | None = None) -> dict:
    points = points or [
        {"id":"a","x":0,"y":0}, {"id":"b","x":1,"y":1},
        {"id":"c","x":2,"y":0}, {"id":"interloper","x":12,"y":9},
    ]
    if len(points)<2: raise ValueError("at least two points required")
    center_x=sum(float(p["x"]) for p in points)/len(points); center_y=sum(float(p["y"]) for p in points)/len(points)
    scored=[]
    for point in points:
        distance=math.hypot(float(point["x"])-center_x,float(point["y"])-center_y)
        scored.append({**point,"distance":round(distance,4)})
    outsider=max(scored,key=lambda item:item["distance"])
    return {"centroid":[round(center_x,4),round(center_y,4)],"interloper":outsider,"confidence":round(outsider["distance"]/(sum(item["distance"] for item in scored)+1e-9),4),"signature":hashlib.sha256(json.dumps(scored,sort_keys=True).encode()).hexdigest()[:16]}


def main(argv=None):
    parser=argparse.ArgumentParser(); parser.parse_args(argv); print(json.dumps(inspect(),sort_keys=True)); return 0


if __name__ == "__main__": raise SystemExit(main())
