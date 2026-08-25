#!/usr/bin/env python3
"""Neural Topology Mapper — discover the living graph structure of the codebase.

Scans Python imports across the entire repo and builds a dependency graph.
Then applies graph-theoretic analysis to find:
- Central hub modules (high betweenness centrality)
- Isolated components (disconnected subgraphs)
- Feedback loops (circular import chains)
- Bridge modules (connecting otherwise disconnected components)

This creates a "brain scan" of the project — revealing its actual
structure vs. its intended structure.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ModuleNode:
    module_id: str
    file_path: str
    imports: list[str]
    imported_by: list[str]
    is_hub: bool = False
    is_bridge: bool = False
    in_loop: bool = False
    component_id: int = -1

    def payload(self) -> dict[str, Any]:
        return {
            "module_id": self.module_id,
            "file_path": self.file_path,
            "imports": self.imports,
            "imported_by": self.imported_by,
            "is_hub": self.is_hub,
            "is_bridge": self.is_bridge,
            "in_loop": self.in_loop,
            "component_id": self.component_id,
        }


@dataclass
class TopologyMapper:
    """Scan repo and build dependency graph."""
    root: Path
    exclude_dirs: set[str] = field(default_factory=lambda: {
        "__pycache__", ".git", "node_modules", "backup", ".runtime",
        ".pytest_cache",
    })
    exclude_files: set[str] = field(default_factory=lambda: {
        "conftest.py",
    })

    def scan(self) -> dict[str, Any]:
        modules, import_graph = self._scan_files()
        components = self._find_components(import_graph)
        hubs = self._find_hubs(import_graph, modules)
        bridges = self._find_bridges(import_graph, components)
        loops = self._find_feedback_loops(import_graph)

        # Tag nodes
        enriched: dict[str, dict[str, Any]] = {}
        for mid, mod in modules.items():
            enriched[mid] = ModuleNode(
                module_id=mid,
                file_path=mod["file_path"],
                imports=mod["imports"],
                imported_by=mod["imported_by"],
                is_hub=mid in hubs,
                is_bridge=mid in bridges,
                in_loop=any(mid in loop for loop in loops),
                component_id=components.get(mid, -1),
            ).payload()

        return {
            "modules": enriched,
            "summary": {
                "total_modules": len(enriched),
                "total_edges": sum(len(m["imports"]) for m in enriched.values()),
                "components": len(set(components.values())) if components else 0,
                "hub_count": len(hubs),
                "bridge_count": len(bridges),
                "loop_count": len(loops),
                "largest_loop": max((len(l) for l in loops), default=0),
                "orphan_count": sum(
                    1 for mid, mod in enriched.items()
                    if not mod["imports"] and not mod["imported_by"]
                ),
            },
            "hubs": sorted(hubs),
            "bridges": sorted(bridges),
            "loops": [list(loop) for loop in loops[:5]],
        }

    def _scan_files(self) -> tuple[dict[str, dict], dict[str, set[str]]]:
        modules: dict[str, dict] = {}
        import_graph: dict[str, set[str]] = defaultdict(set)

        for py_file in self._find_python_files():
            try:
                source = py_file.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(source, filename=str(py_file))
            except (SyntaxError, UnicodeDecodeError):
                continue

            module_id = self._path_to_module(py_file)
            if module_id is None:
                continue

            imports = self._extract_imports(tree)
            local_imports = [
                imp for imp in imports
                if self._is_local_import(imp)
            ]

            modules[module_id] = {
                "file_path": str(py_file.relative_to(self.root)),
                "imports": local_imports,
                "imported_by": [],
            }
            for imp in local_imports:
                import_graph[module_id].add(imp)

        # Build reverse edges
        for source, targets in import_graph.items():
            for target in targets:
                if target in modules:
                    modules[target]["imported_by"].append(source)

        return modules, dict(import_graph)

    def _find_python_files(self):
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirs_to_skip = [d for d in dirnames if d in self.exclude_dirs]
            for d in dirs_to_skip:
                dirnames.remove(d)
            for fname in filenames:
                if fname.endswith(".py") and fname not in self.exclude_files:
                    yield Path(dirpath) / fname

    def _path_to_module(self, path: Path) -> str | None:
        try:
            rel = path.relative_to(self.root)
        except ValueError:
            return None
        parts = list(rel.with_suffix("").parts)
        if parts[-1] == "__init__":
            parts = parts[:-1]
        return ".".join(parts) if parts else None

    def _extract_imports(self, tree: ast.Module) -> list[str]:
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.level == 0:
                    imports.append(node.module.split(".")[0])
        return imports

    def _is_local_import(self, module_name: str) -> bool:
        """Check if an import name maps to a local directory/package."""
        candidate = self.root / module_name
        return candidate.is_dir() or (candidate.with_suffix(".py")).is_file()

    def _find_components(self, graph: dict[str, set[str]]) -> dict[str, int]:
        """BFS to find connected components."""
        all_nodes = set(graph.keys())
        for targets in graph.values():
            all_nodes.update(targets)

        visited: set[str] = set()
        components: dict[str, int] = {}
        comp_id = 0

        for node in sorted(all_nodes):
            if node in visited:
                continue
            queue = [node]
            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue
                visited.add(current)
                components[current] = comp_id
                for neighbor in graph.get(current, set()):
                    if neighbor not in visited:
                        queue.append(neighbor)
                # Also check reverse edges
                for source, targets in graph.items():
                    if current in targets and source not in visited:
                        queue.append(source)
            comp_id += 1

        return components

    def _find_hubs(self, graph: dict[str, set[str]], modules: dict) -> set[str]:
        """Find modules with highest connectivity."""
        in_degree = defaultdict(int)
        out_degree = defaultdict(int)
        for source, targets in graph.items():
            out_degree[source] += len(targets)
            for t in targets:
                in_degree[t] += 1

        total_nodes = len(set(list(graph.keys()) + [t for ts in graph.values() for t in ts]))
        if total_nodes == 0:
            return set()

        threshold = max(3, int(total_nodes * 0.1))
        hubs = set()
        for node in set(in_degree) | set(out_degree):
            score = in_degree[node] + out_degree[node]
            if score >= threshold:
                hubs.add(node)
        return hubs

    def _find_bridges(self, graph: dict[str, set[str]], components: dict[str, int]) -> set[str]:
        """Find nodes that connect different components (would split graph if removed)."""
        comp_values = set(components.values())
        if len(comp_values) <= 1:
            return set()

        bridges: set[str] = set()
        for node in components:
            # Temporarily remove node and check if component count increases
            neighbors = set()
            for source, targets in graph.items():
                if source == node:
                    neighbors.update(targets)
                elif node in targets:
                    neighbors.add(source)

            # BFS without this node
            reachable_from_first = set()
            first_unvisited = None
            for n in sorted(components):
                if n == node:
                    continue
                first_unvisited = n
                break

            if first_unvisited is None:
                continue

            queue = [first_unvisited]
            visited = set()
            while queue:
                curr = queue.pop(0)
                if curr in visited or curr == node:
                    continue
                visited.add(curr)
                for t in graph.get(curr, set()):
                    if t not in visited and t != node:
                        queue.append(t)
                for s, ts in graph.items():
                    if curr in ts and s not in visited and s != node:
                        queue.append(s)

            reachable_from_first = visited
            isolated_count = 0
            for n in components:
                if n != node and n not in reachable_from_first:
                    isolated_count += 1

            if isolated_count > 0:
                bridges.add(node)

        return bridges

    def _find_feedback_loops(self, graph: dict[str, set[str]]) -> list[list[str]]:
        """Find cycles using DFS."""
        loops: list[list[str]] = []
        visited_global: set[str] = set()

        for start in sorted(graph):
            if start in visited_global:
                continue
            stack = [(start, [start])]
            while stack:
                node, path = stack.pop()
                if node in visited_global:
                    if node in path:
                        # Found cycle
                        cycle_start = path.index(node)
                        cycle = path[cycle_start:]
                        if len(cycle) >= 2:
                            loops.append(cycle)
                    continue
                visited_global.add(node)
                for neighbor in graph.get(node, set()):
                    if neighbor not in visited_global or neighbor in path:
                        stack.append((neighbor, path + [neighbor]))

        # Deduplicate and sort
        seen = set()
        unique_loops = []
        for loop in loops:
            key = tuple(sorted(loop))
            if key not in seen:
                seen.add(key)
                unique_loops.append(loop)

        return sorted(unique_loops, key=len)


def demo() -> dict[str, Any]:
    root = Path(__file__).resolve().parents[2]
    mapper = TopologyMapper(root=root)
    return mapper.scan()


def main() -> None:
    result = demo()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
