"""Cosmic Web Mapper — Maps the universe of possible module interactions.

Creates a cosmological model where modules are galaxies, functions are
stars, and imports are cosmic filaments connecting them.
"""
from __future__ import annotations
import hashlib
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Galaxy:
    def __init__(self, name: str, subsystem: str, stars: int, luminosity: float):
        self.name = name
        self.subsystem = subsystem
        self.stars = stars
        self.luminosity = luminosity
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.filaments: list[str] = []

    def distance_to(self, other: "Galaxy") -> float:
        return math.sqrt((self.x-other.x)**2 + (self.y-other.y)**2 + (self.z-other.z)**2)

    def to_dict(self) -> dict:
        return {
            "name": self.name, "subsystem": self.subsystem,
            "stars": self.stars, "luminosity": round(self.luminosity, 4),
            "position": (round(self.x, 2), round(self.y, 2), round(self.z, 2)),
            "filaments": len(self.filaments),
        }


class CosmicWebMapper:
    def __init__(self, seed=42):
        self.seed = seed
        self.galaxies: dict[str, Galaxy] = {}
        self.filaments: list[tuple[str, str, float]] = []

    def map_galaxy(self, name: str, subsystem: str, filepath: Path):
        text = filepath.read_text(errors="replace")
        lines = text.splitlines()
        funcs = sum(1 for l in lines if l.strip().startswith("def "))
        classes = sum(1 for l in lines if l.strip().startswith("class "))
        imports = sum(1 for l in lines if l.strip().startswith(("import ", "from ")))
        luminosity = (funcs + classes * 2) / max(1, len(lines)) * 100
        g = Galaxy(name, subsystem, funcs + classes, luminosity)
        self.galaxies[name] = g

    def position_galaxies(self):
        import random
        rng = random.Random(self.seed)
        for i, (name, g) in enumerate(self.galaxies.items()):
            angle = rng.uniform(0, 2 * math.pi)
            phi = rng.uniform(-math.pi/2, math.pi/2)
            r = rng.uniform(1, 10)
            g.x = r * math.cos(phi) * math.cos(angle + i * 0.5)
            g.y = r * math.cos(phi) * math.sin(angle + i * 0.5)
            g.z = r * math.sin(phi)

    def create_filaments(self):
        """Connect galaxies that share subsystem (cosmic filaments)."""
        by_sub = {}
        for name, g in self.galaxies.items():
            by_sub.setdefault(g.subsystem, []).append(name)
        for subsys, names in by_sub.items():
            for i in range(len(names) - 1):
                a, b = names[i], names[i+1]
                dist = self.galaxies[a].distance_to(self.galaxies[b])
                self.filaments.append((a, b, dist))
                self.galaxies[a].filaments.append(b)
                self.galaxies[b].filaments.append(a)

    def cosmic_age(self) -> str:
        n = len(self.galaxies)
        if n < 10: return "early_universe"
        elif n < 30: return "galactic_formation"
        elif n < 60: return "cosmic_web"
        else: return "mature_universe"

    def report(self) -> dict:
        self.position_galaxies()
        self.create_filaments()
        total_stars = sum(g.stars for g in self.galaxies.values())
        avg_luminosity = sum(g.luminosity for g in self.galaxies.values()) / max(1, len(self.galaxies))
        return {
            "cosmos": "cosmic_web_mapper",
            "age": self.cosmic_age(),
            "galaxies": len(self.galaxies),
            "total_stars": total_stars,
            "filaments": len(self.filaments),
            "avg_luminosity": round(avg_luminosity, 4),
            "brightest": max(self.galaxies.values(), key=lambda g: g.luminosity).to_dict() if self.galaxies else None,
            "largest": max(self.galaxies.values(), key=lambda g: g.stars).to_dict() if self.galaxies else None,
        }


def demo():
    mapper = CosmicWebMapper(seed=42)
    dirs = {
        "api": ROOT / "api", "lab": ROOT / "lab" / "experiments",
        "bridges": ROOT / "bridges", "constellation": ROOT / "constellation",
    }
    for subsys, base in dirs.items():
        if base.exists():
            for py in base.glob("*.py"):
                if not py.name.startswith("_") and not py.name.startswith("test_"):
                    mapper.map_galaxy(py.stem, subsys, py)
    return mapper.report()


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
