"""HORTUS HEXIS — the garden exposed on a local web server.

Serves the gallery UI (/hortus) plus a small JSON API so the app is
interactive in the browser, not just the shell.

Run:  python -m hortus_hexis.web [--port 8090]
"""
from __future__ import annotations

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from hortus_hexis.autogenesis import grow_and_gate  # noqa: E402
from hortus_hexis.cross import hybrid_name, hybrid_seed  # noqa: E402
from hortus_hexis.growth import Organism  # noqa: E402
from hortus_hexis.registry import all, record  # noqa: E402
from hortus_hexis.seed import species_from_hex, words_to_seed  # noqa: E402

GARDEN_HTML = ROOT / "dashboard" / "hortus.html"


def _organisms_payload() -> Dict[str, Any]:
    rows = all()
    out = []
    for e in rows:
        spec = ROOT / "hortus_hexis" / "organisms" / f"{e['name']}.json"
        parents = []
        if spec.exists():
            try:
                parents = json.loads(spec.read_text()).get("parents", [])
            except Exception:
                parents = []
        seed = e["seed"] or (e.get("content") or "")
        o = Organism(e["name"], seed, e.get("content") or e["name"])
        out.append({
            "name": e["name"], "seed": seed, "cells": len(o.cells),
            "vitality": o.vitality, "parents": parents,
            "art": "\n".join(o.to_art()[:22]),
        })
    out.reverse()
    return {"count": len(out), "organisms": out}


def _plant(words: str, commit: bool = True) -> Dict[str, Any]:
    seed = words_to_seed(words)
    name = species_from_hex(seed)
    o = Organism(name, seed, words)
    res = grow_and_gate(name, seed, words, o.to_dict(), commit=commit, verbose=False)
    if res["gate"] != "open":
        return {"error": "gate closed", "name": name}
    record(name, seed, words, 1, res.get("commit") or "")
    return {"name": name, "commit": res.get("commit"), "vitality": o.vitality}


def _cross(a: str, b: str, commit: bool = True) -> Dict[str, Any]:
    rows = all()
    by_name = {e["name"]: e for e in rows}
    if a not in by_name or b not in by_name:
        return {"error": f"unknown parent (have: {', '.join(by_name)})"}
    seed = hybrid_seed(by_name[a]["seed"], by_name[b]["seed"])
    name = hybrid_name(a, b)
    o = Organism(name, seed, f"hybrid:{a}+{b}")
    res = grow_and_gate(name, seed, f"hybrid of {a} and {b}", o.to_dict(),
                        commit=commit, verbose=False, parents=[a, b])
    if res["gate"] != "open":
        return {"error": "gate closed", "name": name}
    record(name, seed, f"hybrid:{a}+{b}", 1, res.get("commit") or "")
    return {"name": name, "commit": res.get("commit"), "vitality": o.vitality, "parents": [a, b]}


class GardenHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # quiet
        pass

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _html(self, path: Path):
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/hortus" or path == "/hortus/":
            if GARDEN_HTML.exists():
                return self._html(GARDEN_HTML)
            return self._json({"error": "garden ui missing"}, 404)
        if path == "/hortus/api/organisms":
            return self._json(_organisms_payload())
        if path == "/hortus/api/song":
            from urllib.parse import parse_qs
            q = parse_qs(self.path.split("?", 1)[1]) if "?" in self.path else {}
            name = (q.get("name") or [""])[0]
            spec = ROOT / "hortus_hexis" / "organisms" / f"{name}.json"
            song = ""
            if spec.exists():
                try:
                    song = json.loads(spec.read_text()).get("song_text", "")
                except Exception:
                    song = ""
            return self._json({"name": name, "song": song})
        return self._json({"error": "not found"}, 404)

    def do_POST(self):
        path = self.path.split("?")[0]
        length = int(self.headers.get("Content-Length") or 0)
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        except Exception:
            payload = {}
        if path == "/hortus/api/plant":
            words = str(payload.get("words") or "").strip()
            if not words:
                return self._json({"error": "no words"}, 400)
            return self._json(_plant(words, bool(payload.get("commit", True))))
        if path == "/hortus/api/cross":
            a = str(payload.get("a") or "").strip()
            b = str(payload.get("b") or "").strip()
            if not a or not b:
                return self._json({"error": "need a and b"}, 400)
            return self._json(_cross(a, b, bool(payload.get("commit", True))))
        return self._json({"error": "not found"}, 404)


def serve(port: int = 8090, host: str = "0.0.0.0"):
    srv = ThreadingHTTPServer((host, port), GardenHandler)
    print(f"  HORTUS HEXIS garden:  http://localhost:{port}/hortus")
    print(f"  organisms api:        http://localhost:{port}/hortus/api/organisms")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8090)
    args = ap.parse_args()
    serve(args.port)
