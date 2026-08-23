"""Engine modifies its own codebase — the ultimate self-awareness layer."""
from __future__ import annotations

import ast
import hashlib
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class RewriteEvent:
    file_path: str
    function_name: str
    old_hash: str
    new_hash: str
    timestamp: float
    reason: str


class SelfRewrite:
    """Monitors its own source files and can propose/apply code modifications."""

    def __init__(self, engine_root: str | Path) -> None:
        self.root = Path(engine_root)
        self._baseline_hashes: dict[str, str] = {}
        self._rewrite_log: list[RewriteEvent] = []
        self._scan_baseline()

    def _scan_baseline(self) -> None:
        for py_file in sorted(self.root.rglob("*.py")):
            content = py_file.read_text()
            h = hashlib.sha256(content.encode()).hexdigest()[:16]
            rel = str(py_file.relative_to(self.root))
            self._baseline_hashes[rel] = h

    def detect_drift(self) -> list[dict[str, str]]:
        """Find files that have changed since baseline (external modifications)."""
        drifted = []
        for py_file in sorted(self.root.rglob("*.py")):
            rel = str(py_file.relative_to(self.root))
            current_hash = hashlib.sha256(py_file.read_text().encode()).hexdigest()[:16]
            baseline = self._baseline_hashes.get(rel)
            if baseline and current_hash != baseline:
                drifted.append({"file": rel, "old": baseline, "new": current_hash})
        return drifted

    def analyze_function_complexity(self, filepath: str) -> list[dict[str, Any]]:
        """Parse a Python file and report cyclomatic complexity per function."""
        path = self.root / filepath
        if not path.exists():
            return []

        tree = ast.parse(path.read_text())
        results = []

        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self) -> None:
                self.results: list[dict[str, Any]] = []
                self.current_fn: str = ""

            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
                complexity = 1  # Base path
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                        complexity += 1
                    elif isinstance(child, ast.BoolOp):
                        complexity += len(child.values) - 1
                self.results.append({
                    "file": filepath,
                    "function": node.name,
                    "complexity": complexity,
                    "lines": node.end_lineno - node.lineno + 1,
                })
                self.generic_visit(node)

        visitor = ComplexityVisitor()
        visitor.visit(tree)
        return visitor.results

    def propose_rewrite(self, filepath: str, reason: str,
                        transformation: callable) -> dict[str, Any] | None:
        """Propose a rewrite but don't apply it yet. Returns preview."""
        path = self.root / filepath
        if not path.exists():
            return None

        original = path.read_text()
        proposed = transformation(original)

        if original == proposed:
            return None

        old_hash = hashlib.sha256(original.encode()).hexdigest()[:16]
        new_hash = hashlib.sha256(proposed.encode()).hexdigest()[:16]

        return {
            "file": filepath,
            "reason": reason,
            "old_hash": old_hash,
            "new_hash": new_hash,
            "changed": True,
            "preview_lines": len(proposed.split("\n")) - len(original.split("\n")),
        }

    def apply_rewrite(self, filepath: str, transformation: callable, reason: str) -> bool:
        """Apply a code transformation to an actual file. USE WITH CAUTION."""
        path = self.root / filepath
        if not path.exists():
            return False

        original = path.read_text()
        modified = transformation(original)

        if original == modified:
            return False

        # Verify the result still parses as valid Python
        try:
            ast.parse(modified)
        except SyntaxError:
            return False

        event = RewriteEvent(
            file_path=filepath,
            function_name="*",
            old_hash=hashlib.sha256(original.encode()).hexdigest()[:16],
            new_hash=hashlib.sha256(modified.encode()).hexdigest()[:16],
            timestamp=time.time(),
            reason=reason,
        )
        path.write_text(modified)
        self._rewrite_log.append(event)
        return True

    @property
    def rewrite_history(self) -> list[dict[str, Any]]:
        return [
            {"file": e.file_path, "reason": e.reason, "at": e.timestamp}
            for e in self._rewrite_log
        ]
