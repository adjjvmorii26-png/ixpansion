#!/usr/bin/env python3
"""Astral Network Weaver — module discovery bus and capability registry."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lab.runtime_vault import (
    CHAIN_FIELDS,
    append_jsonl,
    ledger_path,
    read_json,
    state_path,
    write_json,
)

SCHEMA = "aleph.experiments.astral-network-weaver.v1"



def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash(payload: dict[str, Any]) -> str:
    material = {key: value for key, value in payload.items() if key != "weave_hash"}
    return hashlib.sha256(_canonical(material)).hexdigest()


def _registry_path() -> Path:
    return state_path("astral", "network_registry.json")


def _load_registry() -> dict[str, Any]:
    return read_json(_registry_path(), {"modules": {}, "discovery_log": []})


def _save_registry(registry: dict[str, Any]) -> None:
    write_json(_registry_path(), registry)


def register_module(
    name: str,
    *,
    capabilities: list[str],
    consumes: list[str] | None = None,
    description: str = "",
    module_path: str = "",
    clock: Any = utc_now,
) -> dict[str, Any]:
    """Register a module's capabilities in the discovery registry."""
    if not name or not isinstance(name, str):
        raise ValueError("module name is required")
    if not capabilities or not all(isinstance(c, str) for c in capabilities):
        raise ValueError("at least one string capability is required")
    registry = _load_registry()
    entry = {
        "name": name,
        "capabilities": sorted(set(capabilities)),
        "consumes": sorted(set(consumes or [])),
        "description": description,
        "module_path": module_path,
        "registered_at": clock(),
        "status": "active",
    }
    registry["modules"][name] = entry
    _save_registry(registry)
    return entry


def discover_peers(
    providing: str | None = None,
    consuming: str | None = None,
) -> list[dict[str, Any]]:
    """Find registered modules that provide or consume a given capability."""
    registry = _load_registry()
    results = []
    for entry in registry.get("modules", {}).values():
        if providing and providing in entry.get("capabilities", []):
            results.append(entry)
        elif consuming and consuming in entry.get("consumes", []):
            results.append(entry)
    return results


def weave_network(*, clock: Any = utc_now) -> dict[str, Any]:
    """Generate a sealed snapshot of the current module discovery network."""
    registry = _load_registry()
    modules = registry.get("modules", {})
    capability_map: dict[str, list[str]] = {}
    for name, entry in modules.items():
        for cap in entry.get("capabilities", []):
            capability_map.setdefault(cap, []).append(name)
    topology = []
    for name, entry in modules.items():
        provides = entry.get("capabilities", [])
        consumes = entry.get("consumes", [])
        peers_providing = [
            other for other_name, other in modules.items()
            if other_name != name and any(c in other.get("capabilities", []) for c in consumes)
        ]
        topology.append({
            "module": name,
            "provides": provides,
            "consumes": consumes,
            "peer_count": len(peers_providing),
            "peer_names": sorted([p["name"] for p in peers_providing]),
        })
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "experiment": "astral-network-weaver",
        "status": "sealed",
        "mode": "read-only-discovery",
        "sealed_at": clock(),
        "module_count": len(modules),
        "modules": list(modules.values()),
        "capability_map": capability_map,
        "unique_capabilities": len(capability_map),
        "topology": topology,
        "execution_enabled": False,
    }
    result["weave_hash"] = _hash(result)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    reg = sub.add_parser("register", help="register a module")
    reg.add_argument("name")
    reg.add_argument("--capabilities", nargs="+", required=True)
    reg.add_argument("--consumes", nargs="*", default=[])
    reg.add_argument("--description", default="")
    reg.add_argument("--module-path", default="")
    disc = sub.add_parser("discover", help="discover peers")
    disc.add_argument("--providing")
    disc.add_argument("--consuming")
    sub.add_parser("weave", help="snapshot the network topology")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "register":
            entry = register_module(
                args.name,
                capabilities=args.capabilities,
                consumes=args.consumes,
                description=args.description,
                module_path=args.module_path,
            )
        elif args.command == "discover":
            entry = discover_peers(providing=args.providing, consuming=args.consuming)
        else:
            entry = weave_network()
        print(json.dumps(entry, sort_keys=True, indent=2))
        return 0
    except (OSError, TypeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
