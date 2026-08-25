"""Codebase Cartography — Generates a navigable map of the entire repository.

Creates a hierarchical map with districts, neighborhoods, and landmarks,
treating the codebase as a city that can be explored and navigated.
"""
from __future__ import annotations
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Landmark:
    """A point of interest in the codebase map."""

    def __init__(self, name: str, kind: str, size: int, district: str):
        self.name = name
        self.kind = kind  # file, directory, module, test
        self.size = size
        self.district = district
        self.elevation = min(100, size / 50)  # Larger = higher elevation

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "kind": self.kind,
            "size": self.size,
            "district": self.district,
            "elevation": round(self.elevation, 1),
        }


class District:
    """A neighborhood/area in the codebase map."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.landmarks: list[Landmark] = []
        self.population = 0  # Number of files
        self.area = 0  # Total lines

    def add_landmark(self, landmark: Landmark):
        self.landmarks.append(landmark)
        self.population += 1
        self.area += landmark.size

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "population": self.population,
            "area": self.area,
            "landmark_count": len(self.landmarks),
            "top_landmarks": sorted(
                [l.to_dict() for l in self.landmarks],
                key=lambda x: x["size"], reverse=True
            )[:5],
        }


class CodebaseCartographer:
    """Generates a navigable map of the codebase."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.districts: dict[str, District] = {}
        self.roads: list[tuple[str, str]] = []  # Connections between districts

    def define_districts(self):
        """Define the major districts of the codebase."""
        definitions = {
            "api": "The control center — HTTP endpoints and serverless functions",
            "lab": "The laboratory — experimental modules and research",
            "bridges": "The bridge district — cross-system connectors",
            "constellation": "The observatory — dependency mapping and navigation",
            "mycelium": "The underground network — hidden connections and signals",
            "ixpansion": "The expansion zone — HEX VM, agents, and world systems",
            "omega_prime": "The prime directive — core kernel and agent species",
            "omega_fractal_engine": "The fractal engine — recursive generation systems",
            "solid-organism": "The living tissue — organic growth modules",
            "project_root": "The foundation — base architecture and utilities",
        }
        for name, desc in definitions.items():
            self.districts[name] = District(name, desc)

    def survey_district(self, district_name: str, base: Path):
        """Survey a district and catalog its landmarks."""
        if not base.exists() or district_name not in self.districts:
            return

        district = self.districts[district_name]

        for py in sorted(base.glob("*.py")):
            if py.name.startswith("_") or py.name.startswith("test_"):
                continue
            landmark = Landmark(
                py.stem, "module", py.stat().st_size, district_name
            )
            district.add_landmark(landmark)

        # Count test files
        test_count = sum(1 for f in base.glob("test_*.py"))
        if test_count > 0:
            district.add_landmark(Landmark("test_suite", "test", test_count * 200, district_name))

    def build_roads(self):
        """Connect districts that share modules or imports."""
        district_names = list(self.districts.keys())
        for i, a in enumerate(district_names):
            for b in district_names[i+1:]:
                # Check if districts have similar naming patterns
                a_landmarks = {l.name for l in self.districts[a].landmarks}
                b_landmarks = {l.name for l in self.districts[b].landmarks}
                overlap = a_landmarks & b_landmarks
                if overlap or (a != b and self.districts[a].population > 0 and self.districts[b].population > 0):
                    self.roads.append((a, b))

    def navigate(self, from_district: str, to_district: str) -> dict:
        """Find a path between two districts."""
        if from_district not in self.districts or to_district not in self.districts:
            return {"error": "district not found"}

        # Simple BFS
        from collections import deque
        graph = {}
        for a, b in self.roads:
            graph.setdefault(a, []).append(b)
            graph.setdefault(b, []).append(a)

        queue = deque([(from_district, [from_district])])
        visited = {from_district}

        while queue:
            current, path = queue.popleft()
            if current == to_district:
                return {"path": path, "distance": len(path) - 1, "found": True}
            for neighbor in graph.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return {"path": [], "distance": -1, "found": False}

    def report(self) -> dict:
        """Generate the full cartography report."""
        self.define_districts()

        # Survey all districts
        district_dirs = {
            "api": ROOT / "api",
            "lab": ROOT / "lab" / "experiments",
            "bridges": ROOT / "bridges",
            "constellation": ROOT / "constellation",
            "mycelium": ROOT / "mycelium",
            "ixpansion": ROOT / "ixpansion",
            "omega_prime": ROOT / "omega_prime",
            "omega_fractal_engine": ROOT / "omega_fractal_engine",
            "solid-organism": ROOT / "solid-organism",
            "project_root": ROOT / "project_root",
        }

        for name, base in district_dirs.items():
            self.survey_district(name, base)

        self.build_roads()

        total_landmarks = sum(d.population for d in self.districts.values())
        total_area = sum(d.area for d in self.districts.values())
        active_districts = sum(1 for d in self.districts.values() if d.population > 0)

        return {
            "cartography": "codebase_cartography",
            "total_districts": len(self.districts),
            "active_districts": active_districts,
            "total_landmarks": total_landmarks,
            "total_area": total_area,
            "roads": len(self.roads),
            "districts": {k: v.to_dict() for k, v in self.districts.items() if v.population > 0},
            "map_hash": hashlib.sha256(f"{total_landmarks}:{total_area}".encode()).hexdigest()[:12],
        }


def demo():
    cartographer = CodebaseCartographer(seed=42)
    return cartographer.report()


def main():
    import json
    result = demo()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
