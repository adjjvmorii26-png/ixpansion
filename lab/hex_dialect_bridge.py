"""HEX Dialect Bridge — Connects alpha, delta, and omega dialects.

Provides a unified interface to the three HEX dialects, enabling
cross-dialect translation and protocol negotiation.
"""
from __future__ import annotations
import hashlib
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


class Dialect:
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self.transforms: list[str] = []

    def encode(self, payload: dict) -> dict:
        return {"_dialect": self.name, "_version": self.version, "body": payload}

    def decode(self, envelope: dict) -> dict:
        return envelope.get("body", {})


class AlphaDialect(Dialect):
    def __init__(self):
        super().__init__("alpha", "1.0")
        self.transforms = ["wrap", "sign"]

    def encode(self, payload: dict) -> dict:
        result = super().encode(payload)
        result["_sig"] = hashlib.md5(str(payload).encode()).hexdigest()[:8]
        return result


class DeltaDialect(Dialect):
    def __init__(self):
        super().__init__("delta", "1.0")
        self.transforms = ["wrap", "timestamp"]

    def encode(self, payload: dict) -> dict:
        result = super().encode(payload)
        result["_ts"] = time.time()
        return result


class OmegaDialect(Dialect):
    def __init__(self):
        super().__init__("omega", "1.0")
        self.transforms = ["wrap", "compress", "encrypt"]

    def encode(self, payload: dict) -> dict:
        result = super().encode(payload)
        result["_compressed"] = True
        result["_hash"] = hashlib.sha256(str(payload).encode()).hexdigest()[:16]
        return result


class DialectBridge:
    def __init__(self):
        self.dialects: dict[str, Dialect] = {
            "alpha": AlphaDialect(),
            "delta": DeltaDialect(),
            "omega": OmegaDialect(),
        }
        self.translation_log: list[dict] = []

    def translate(self, payload: dict, source: str, target: str) -> dict:
        if source not in self.dialects or target not in self.dialects:
            return {"error": f"unknown dialect: {source} or {target}"}
        encoded = self.dialects[source].encode(payload)
        decoded = self.dialects[target].decode(encoded)
        re_encoded = self.dialects[target].encode(decoded)
        self.translation_log.append({
            "source": source, "target": target,
            "input_hash": hashlib.md5(str(payload).encode()).hexdigest()[:8],
            "output_hash": hashlib.md5(str(re_encoded).encode()).hexdigest()[:8],
        })
        return re_encoded

    def broadcast(self, payload: dict, source: str) -> dict:
        results = {}
        for name, dialect in self.dialects.items():
            if name != source:
                results[name] = self.translate(payload, source, name)
        return results

    def report(self) -> dict:
        return {
            "bridge": "hex_dialect_bridge",
            "dialects": {name: {"version": d.version, "transforms": d.transforms}
                        for name, d in self.dialects.items()},
            "translation_count": len(self.translation_log),
            "translations": self.translation_log[:10],
        }


def demo():
    bridge = DialectBridge()
    payload = {"action": "spawn", "entity": "sentinel", "params": {"strength": 0.8}}
    bridge.translate(payload, "alpha", "delta")
    bridge.translate(payload, "delta", "omega")
    bridge.translate(payload, "omega", "alpha")
    bridge.broadcast(payload, "alpha")
    return bridge.report()


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
