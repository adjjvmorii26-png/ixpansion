"""Lineage — the garden's family tree.

Every organism is born from words, but some are born from *each other*.
This module reads every provenance signal the garden leaves behind:

  - registry entries whose content reads  "hybrid:A+B"
  - organism specs whose words read      "hybrid of A and B"
  - organism specs with an explicit      parents: [A, B] field

and assembles them into an actual family tree: founders, descendants,
generations, and a renderable ASCII map of how the species spread.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "hortus_hexis" / "registry.json"
ORGANISMS = ROOT / "hortus_hexis" / "organisms"

_COLON_HYBRID = re.compile(r"^hybrid:([^+]+)\+([^+]+)$")
_WORD_HYBRID = re.compile(r"hybrid of ([a-z]+) and ([a-z]+)", re.IGNORECASE)


def parents_of(entry: Dict[str, Any]) -> List[str]:
    """Extract parent names from every known provenance signal."""
    found: List[str] = []
    content = (entry.get("content") or "").strip()
    words = (entry.get("words") or "").strip()

    m = _COLON_HYBRID.match(content)
    if m:
        found.extend([m.group(1).strip(), m.group(2).strip()])
    m = _WORD_HYBRID.search(words)
    if m:
        found.extend([m.group(1).strip(), m.group(2).strip()])
    explicit = entry.get("parents") or []
    if isinstance(explicit, list):
        found.extend(str(p).strip() for p in explicit if str(p).strip())

    # keep order stable, drop self-references, dedupe
    seen, out = set(), []
    for name in found:
        if name and name != (entry.get("name") or "") and name not in seen:
            seen.add(name)
            out.append(name)
    return out


def build() -> List[Dict[str, Any]]:
    """Merge registry + organism specs into rich lineage nodes."""
    if not REGISTRY.exists():
        return []
    try:
        rows = json.loads(REGISTRY.read_text())
    except json.JSONDecodeError:
        rows = []

    nodes: List[Dict[str, Any]] = []
    for e in rows:
        name = e.get("name") or ""
        if not name:
            continue
        spec: Dict[str, Any] = {}
        spec_path = ORGANISMS / f"{name}.json"
        if spec_path.exists():
            try:
                spec = json.loads(spec_path.read_text())
            except Exception:
                spec = {}
        merged = {**e, **{k: v for k, v in spec.items() if k not in e or e[k] in (None, "", [], {})}}
        merged["parents"] = parents_of(merged)
        nodes.append(merged)
    return nodes


def lineage_index(nodes: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Dict[str, Any]]:
    nodes = nodes if nodes is not None else build()
    index: Dict[str, Dict[str, Any]] = {}
    for n in nodes:
        name = n.get("name")
        if not name:
            continue
        node = dict(n)
        node["parents"] = parents_of(node)
        index[name] = node
    for name, node in index.items():
        node["children"] = sorted({c["name"] for c in nodes
                                   if name in (parents_of(c) or [])})
    return index


def _depth_of(name: str, index: Dict[str, Dict[str, Any]], memo: Dict[str, int]) -> int:
    if name in memo:
        return memo[name]
    node = index.get(name, {})
    parents = node.get("parents") or []
    if not parents:
        memo[name] = 0
        return 0
    depth = 1 + max((_depth_of(p, index, memo) for p in parents if p in index), default=0)
    memo[name] = depth
    return depth


def generations() -> Dict[str, Dict[str, Any]]:
    """Rolodex of the garden: founders, generations, families, branches."""
    payload = _generations_from(build())
    payload["children"] = sorted(
        n for n in payload["founders"] for n in payload["depths"]
        if payload["depths"].get(n, 0) > 0
    ) if False else sorted(
        n for n, node in lineage_index().items()
        if node.get("parents")
    )
    return payload


def _generations_from(nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
    index = lineage_index(nodes)
    memo: Dict[str, int] = {}
    for name in index:
        _depth_of(name, index, memo)
    founders = sorted(n for n, node in index.items() if not (node.get("parents") or []))
    families = {}
    for name, node in index.items():
        if node.get("parents"):
            for p in node["parents"]:
                families.setdefault(p, []).append(name)
    return {"total": len(index), "founders": founders, "depths": memo,
            "max_generation": max(memo.values(), default=0),
            "families": {k: sorted(v) for k, v in families.items()}}


def render_ascii(nodes: Optional[List[Dict[str, Any]]] = None) -> str:
    """Renders the garden's family tree as an ASCII map."""
    nodes = nodes if nodes is not None else build()
    index = lineage_index(nodes)
    gen = _generations_from(nodes)
    founders = gen["founders"]

    def _subtree(name: str, prefix: str, is_last: bool, out: List[str]) -> None:
        node = index[name]
        branch = "`-" if is_last else "|-"
        out.append(f"{prefix}{branch} {name}")
        kids = node.get("children") or []
        child_prefix = prefix + ("   " if is_last else "|  ")
        for i, kid in enumerate(kids):
            _subtree(kid, child_prefix, i == len(kids) - 1, out)

    lines = [f"GARDEN FAMILY TREE — {gen['total']} organisms, "
             f"{len(founders)} founders, {gen['max_generation']} generations",
             ""]
    for i, f in enumerate(founders):
        _subtree(f, "", i == len(founders) - 1, lines)
    return "\n".join(lines)


def export(path: Optional[Path] = None) -> Path:
    """Writes family_lineage.json (committed as the garden's family bible)."""
    path = path or (ROOT / "hortus_hexis" / "family_lineage.json")
    index = lineage_index()
    payload = {
        "generated": True,
        "count": len(index),
        "generations": generations(),
        "nodes": [{k: n.get(k) for k in ("name", "seed", "content", "commit", "parents", "children")}
                  for n in index.values()],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2))
    return path
