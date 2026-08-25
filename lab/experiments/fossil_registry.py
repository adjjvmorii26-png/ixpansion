"""Fossil Registry — Catalogs dead code, stubs, and abandoned patterns.

Scans the codebase for artifacts that were once active but are now dormant:
empty functions, commented-out code blocks, unused imports, and stub modules.
"""
from __future__ import annotations
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Fossil:
    """A dead code artifact."""

    def __init__(self, fossil_type: str, file: str, line: int, detail: str, age_estimate: str):
        self.fossil_type = fossil_type
        self.file = file
        self.line = line
        self.detail = detail
        self.age_estimate = age_estimate

    def to_dict(self) -> dict:
        return {
            "type": self.fossil_type,
            "file": self.file,
            "line": self.line,
            "detail": self.detail,
            "age": self.age_estimate,
        }


class FossilRegistry:
    """Scans and catalogs dead code fossils."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.fossils: list[Fossil] = []
        self.scan_dirs = [
            ROOT / "api",
            ROOT / "lab" / "experiments",
            ROOT / "bridges",
            ROOT / "lab",
        ]

    def scan_empty_functions(self, text: str, filepath: str):
        """Find functions with only pass or docstring."""
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if re.match(r"\s*def \w+", line):
                func_indent = len(line) - len(line.lstrip())
                j = i + 1
                found_body = False
                while j < len(lines) and j < i + 5:
                    stripped = lines[j].strip()
                    if lines[j].strip() and not lines[j].strip().startswith("#"):
                        if re.match(r"\s*(def |class )", lines[j]):
                            curr_indent = len(lines[j]) - len(lines[j].lstrip())
                            if curr_indent <= func_indent:
                                break
                    if stripped and stripped != chr(34)*3 and stripped != chr(39)*3:
                        if stripped != "pass" and not stripped.startswith(chr(34)*3) and not stripped.startswith(chr(39)*3):
                            found_body = True
                            break
                    j += 1
                if not found_body:
                    func_name = line.strip().split("(")[0].replace("def ", "")
                    self.fossils.append(Fossil(
                        "empty_function", filepath, i + 1,
                        f"Function {func_name!r} has no meaningful body",
                        "stale" if i < len(lines) * 0.3 else "recent",
                    ))


    def scan_commented_code(self, text: str, filepath: str):
        """Find blocks of commented-out code."""
        lines = text.splitlines()
        block_start = None
        block_size = 0

        for i, line in enumerate(lines):
            stripped = line.strip()
            # Commented code patterns: # var = ..., # if ..., # return ...
            if stripped.startswith("#") and any(kw in stripped for kw in ["=", "if ", "return ", "for ", "while ", "def ", "class "]):
                if block_start is None:
                    block_start = i + 1
                block_size += 1
            else:
                if block_size >= 3:
                    self.fossils.append(Fossil(
                        "commented_block", filepath, block_start,
                        f"Commented-out code block ({block_size} lines)",
                        "stale",
                    ))
                block_start = None
                block_size = 0

    def scan_stubs(self, text: str, filepath: str):
        """Find stub modules (very short files with minimal content)."""
        lines = text.splitlines()
        if len(lines) < 10:
            code_lines = [l for l in lines if l.strip() and not l.strip().startswith("#")]
            if len(code_lines) < 3:
                self.fossils.append(Fossil(
                    "stub_module", filepath, 1,
                    f"Very thin module ({len(lines)} lines, {len(code_lines)} code lines)",
                    "recent",
                ))

    def scan_unused_patterns(self, text: str, filepath: str):
        """Find potentially unused patterns."""
        # Find variables assigned but never referenced
        assigns = {}
        for i, line in enumerate(lines := text.splitlines()):
            match = re.match(r"\s*(\w+)\s*=", line)
            if match:
                var_name = match.group(1)
                if len(var_name) > 2 and not var_name.startswith("_"):
                    assigns[var_name] = i + 1

        for var_name, line_num in assigns.items():
            # Count references (excluding the assignment line itself)
            ref_count = sum(
                1 for l in lines
                if var_name in l and l.strip() != f"{var_name} = ..." and not l.strip().startswith(f"{var_name} =")
            )
            if ref_count == 0:
                self.fossils.append(Fossil(
                    "unused_variable", filepath, line_num,
                    f"Variable '{var_name}' assigned but never referenced",
                    "recent",
                ))

    def scan_all(self) -> list[Fossil]:
        """Run all scans across all directories."""
        for base in self.scan_dirs:
            if not base.exists():
                continue
            for py in base.rglob("*.py"):
                if py.name.startswith("_") or py.name.startswith("test_"):
                    continue
                try:
                    text = py.read_text(errors="replace")
                except Exception:
                    continue
                rel = str(py.relative_to(ROOT))
                self.scan_empty_functions(text, rel)
                self.scan_commented_code(text, rel)
                self.scan_stubs(text, rel)
                self.scan_unused_patterns(text, rel)

        return self.fossils

    def report(self) -> dict:
        """Generate fossil registry report."""
        self.scan_all()

        # Group by type
        by_type = {}
        for f in self.fossils:
            if f.fossil_type not in by_type:
                by_type[f.fossil_type] = []
            by_type[f.fossil_type].append(f)

        # Group by file
        by_file = {}
        for f in self.fossils:
            if f.file not in by_file:
                by_file[f.file] = 0
            by_file[f.file] += 1

        return {
            "registry": "fossil_registry",
            "total_fossils": len(self.fossils),
            "by_type": {k: len(v) for k, v in by_type.items()},
            "by_file": dict(sorted(by_file.items(), key=lambda x: x[1], reverse=True)[:10]),
            "fossils": [f.to_dict() for f in self.fossils[:30]],
            "verdict": (
                f"Found {len(self.fossils)} fossils across {len(by_file)} files. "
                f"Types: {', '.join(f'{k}({len(v)})' for k, v in by_type.items())}."
            ),
        }


def demo():
    registry = FossilRegistry(seed=42)
    return registry.report()


def main():
    import json
    result = demo()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
