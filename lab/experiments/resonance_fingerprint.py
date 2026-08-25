"""Resonance Fingerprint — Generates unique fingerprints for code modules.

Each module gets a multi-dimensional fingerprint based on its structure,
naming patterns, import graph, and code texture. Two modules with similar
fingerprints are likely related or co-evolved.
"""
from __future__ import annotations
import hashlib
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Fingerprint:
    """A multi-dimensional code fingerprint."""

    def __init__(self, name: str, dimensions: dict[str, float]):
        self.name = name
        self.dimensions = dimensions
        self.hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """Generate a stable hash from the fingerprint dimensions."""
        dim_str = ":".join(f"{k}={v:.4f}" for k, v in sorted(self.dimensions.items()))
        return hashlib.sha256(dim_str.encode()).hexdigest()[:16]

    def similarity(self, other: "Fingerprint") -> float:
        """Compute cosine similarity with another fingerprint."""
        common_keys = set(self.dimensions.keys()) & set(other.dimensions.keys())
        if not common_keys:
            return 0.0

        dot = sum(self.dimensions[k] * other.dimensions[k] for k in common_keys)
        mag_a = math.sqrt(sum(self.dimensions[k] ** 2 for k in common_keys))
        mag_b = math.sqrt(sum(other.dimensions[k] ** 2 for k in common_keys))

        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot / (mag_a * mag_b)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "dimensions": {k: round(v, 4) for k, v in self.dimensions.items()},
            "hash": self.hash,
        }


class ResonanceFingerprinter:
    """Generates and compares code fingerprints."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.fingerprints: dict[str, Fingerprint] = {}

    def extract_features(self, filepath: Path) -> dict[str, float]:
        """Extract multi-dimensional features from a Python file."""
        text = filepath.read_text(errors="replace")
        lines = text.splitlines()

        # Dimension 1: Complexity (control flow density)
        control_keywords = sum(
            1 for ln in lines
            if any(kw in ln for kw in ["if ", "elif ", "else:", "for ", "while ", "try:", "except", "with "])
        )
        complexity = control_keywords / max(1, len(lines))

        # Dimension 2: Abstraction (class + function ratio)
        classes = sum(1 for ln in lines if ln.strip().startswith("class "))
        functions = sum(1 for ln in lines if ln.strip().startswith("def "))
        abstraction = classes / max(1, functions)

        # Dimension 3: Import density
        imports = sum(1 for ln in lines if ln.strip().startswith(("import ", "from ")))
        import_density = imports / max(1, len(lines))

        # Dimension 4: Docstring coverage
        doc_lines = sum(1 for ln in lines if '"""' in ln or "'''" in ln)
        doc_coverage = doc_lines / max(1, len(lines))

        # Dimension 5: Naming entropy (average word length in identifiers)
        identifiers = re.findall(r"\b[a-z_][a-z0-9_]*\b", text)
        avg_id_length = sum(len(id_) for id_ in identifiers) / max(1, len(identifiers))
        naming_entropy = min(1.0, avg_id_length / 15.0)

        # Dimension 6: Size (normalized)
        size = min(1.0, len(lines) / 500.0)

        # Dimension 7: Nesting depth
        max_indent = 0
        for ln in lines:
            if ln.strip():
                indent = len(ln) - len(ln.lstrip())
                max_indent = max(max_indent, indent)
        nesting = min(1.0, max_indent / 40.0)

        # Dimension 8: Return density (function output richness)
        returns = sum(1 for ln in lines if "return " in ln)
        return_density = returns / max(1, functions)

        return {
            "complexity": complexity,
            "abstraction": abstraction,
            "import_density": import_density,
            "doc_coverage": doc_coverage,
            "naming_entropy": naming_entropy,
            "size": size,
            "nesting": nesting,
            "return_density": return_density,
        }

    def fingerprint_file(self, filepath: Path) -> Fingerprint:
        """Generate a fingerprint for a single file."""
        features = self.extract_features(filepath)
        fp = Fingerprint(filepath.stem, features)
        self.fingerprints[filepath.stem] = fp
        return fp

    def fingerprint_directory(self, base: Path, subsystem: str = ""):
        """Fingerprint all Python files in a directory."""
        if not base.exists():
            return
        for py in sorted(base.glob("*.py")):
            if py.name.startswith("_") or py.name.startswith("test_"):
                continue
            self.fingerprint_file(py)

    def find_twins(self, threshold: float = 0.95) -> list[dict]:
        """Find pairs of modules with very similar fingerprints."""
        twins = []
        names = list(self.fingerprints.keys())
        for i, a in enumerate(names):
            for b in names[i+1:]:
                sim = self.fingerprints[a].similarity(self.fingerprints[b])
                if sim >= threshold:
                    twins.append({
                        "module_a": a,
                        "module_b": b,
                        "similarity": round(sim, 4),
                    })
        twins.sort(key=lambda x: x["similarity"], reverse=True)
        return twins

    def report(self) -> dict:
        """Generate full fingerprint report."""
        # Fingerprint key directories
        dirs = [
            ROOT / "api",
            ROOT / "lab" / "experiments",
            ROOT / "bridges",
        ]
        for d in dirs:
            self.fingerprint_directory(d)

        twins = self.find_twins(threshold=0.90)

        # Compute average fingerprint dimensions
        if self.fingerprints:
            avg_dims = {}
            for key in list(self.fingerprints.values())[0].dimensions:
                values = [fp.dimensions[key] for fp in self.fingerprints.values() if key in fp.dimensions]
                avg_dims[key] = sum(values) / max(1, len(values))
        else:
            avg_dims = {}

        return {
            "fingerprinter": "resonance_fingerprint",
            "fingerprint_count": len(self.fingerprints),
            "twins": twins,
            "twin_count": len(twins),
            "average_dimensions": {k: round(v, 4) for k, v in avg_dims.items()},
            "fingerprints": {k: v.to_dict() for k, v in list(self.fingerprints.items())[:20]},
        }


def demo():
    fp = ResonanceFingerprinter(seed=42)
    return fp.report()


def main():
    import json
    result = demo()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
