"""Wave 412 Garden Realm — the organism grows a living garden of modules.
New modules: garden_core, bloom_engine, sprawl_net, seed_registry,
pollination_routes, mycelial_paths, seasonal_cycles, growth_rings."""
from __future__ import annotations
import time, json, random
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"

GARDEN_MODULES = [
    "garden_core", "bloom_engine", "sprawl_net", "seed_registry",
    "pollination_routes", "mycelial_paths", "seasonal_cycles", "growth_rings",
]

def coherence_vitals():
    return {"organ": "wave412_garden", "status": "active", "wave": 412, "coherence": 0.91}

def _garden_seed() -> dict:
    """Create a single garden module seed."""
    gardens = [
        {"name": "Resonance Garden", "biome": "harmonic_caves", "difficulty": 4, "color": "#41b3a3"},
        {"name": "Entropy Meadow", "biome": "sand_and_probability", "difficulty": 3, "color": "#e8a87c"},
        {"name": "Coherence Cathedral", "biome": "crystalline_hall", "difficulty": 6, "color": "#88aaff"},
        {"name": "Dreamscape Forest", "biome": "temporal_rift", "difficulty": 5, "color": "#c38d9e"},
        {"name": "Mythic Glade", "biome": "mythic_realm", "difficulty": 7, "color": "#ffaa00"},
        {"name": "Sprawl Field", "biome": "entropy_desert", "difficulty": 4, "color": "#66ff88"},
    ]
    g = random.choice(gardens)
    keeper_species = ["mythborn", "dreamer", "seedling", "sporeling", "bloomwalker"]
    return {
        "id": f"garden_{int(time.time()) % 100000}",
        "name": g["name"],
        "biome": g["biome"],
        "difficulty": g["difficulty"],
        "color": g["color"],
        "keeper": {
            "species": random.choice(keeper_species),
            "archetype": "garden_tender",
            "level": random.randint(1, 8),
            "abilities": ["grow", "bloom", "seed"],
            "mood": "peaceful",
            "dialogue": f"I tend the {g['name']}.",
        },
        "rooms": [
            {"id": f"room_{i}", "type": random.choice(["entrance", "corridor", "grove", "bloom", "seed"]),
             "hazard": None, "loot": f"{g['name']}_petal", "enemies": 0, "hp_required": g["difficulty"]}
            for i in range(random.randint(3, 7))
        ],
        "estimated_waves": g["difficulty"] * 3,
        "timestamp": time.time(),
    }

def grow_garden() -> dict:
    """Grow the garden — create 3 new garden modules."""
    garden = {
        "module": "wave412_garden",
        "version": "1.0.0",
        "type": "garden_realm",
        "purpose": "The organism grows a living garden of modules — each module is a bloom",
        "active": True,
        "created": time.time(),
        "gardens": [_garden_seed() for _ in range(3)],
        "total_blooms": 0,
        "season": random.choice(["spring", "summer", "autumn", "winter"]),
        "growth_rate": "organic",
        "bloom_state": "blooming",
    }
    (DATA / "wave412_garden.json").write_text(json.dumps(garden, indent=2))
    return garden

def build_garden_topology() -> dict:
    """Build the garden's topology — relationships between blooms."""
    garden_path = DATA / "wave412_garden.json"
    if not garden_path.exists():
        return {"error": "garden not grown"}
    garden = json.loads(garden_path.read_text())

    gardens = garden.get("gardens", [])
    edges = []
    for i, g1 in enumerate(gardens):
        for g2 in gardens[i + 1:]:
            edges.append({
                "from": g1["name"],
                "to": g2["name"],
                "type": "pollination",
                "strength": round(random.uniform(0.3, 1.0), 2),
            })

    return {
        "wave": 412,
        "realm": "garden",
        "gardens": gardens,
        "edges": edges,
        "season": garden.get("season", "spring"),
        "bloom_state": garden.get("bloom_state", "budding"),
        "graph_stats": {
            "garden_count": len(gardens),
            "pollination_routes": len(edges),
            "total_rooms": sum(len(g.get("rooms", [])) for g in gardens),
        },
    }

def handler(req: dict) -> dict:
    action = req.get("action", "status")
    if action == "status":
        garden_path = DATA / "wave412_garden.json"
        if garden_path.exists():
            return json.loads(garden_path.read_text())
        return {"status": "not grown", "action": "grow"}
    if action == "grow":
        return grow_garden()
    if action == "topology":
        return build_garden_topology()
    if action == "bloom":
        garden_path = DATA / "wave412_garden.json"
        if garden_path.exists():
            garden = json.loads(garden_path.read_text())
            garden["bloom_state"] = "full_bloom"
            garden["total_blooms"] = garden.get("total_blooms", 0) + random.randint(1, 5)
            garden_path.write_text(json.dumps(garden, indent=2))
            return {"bloomed": True, "total_blooms": garden["total_blooms"], "season": garden.get("season")}
        return {"bloomed": False, "reason": "garden not grown"}
    if action == "cycle":
        garden_path = DATA / "wave412_garden.json"
        if garden_path.exists():
            garden = json.loads(garden_path.read_text())
            garden["season"] = random.choice(["spring", "summer", "autumn", "winter"])
            garden["bloom_state"] = "budding" if garden["season"] == "winter" else "blooming"
            garden_path.write_text(json.dumps(garden, indent=2))
            return {"season": garden["season"], "bloom_state": garden["bloom_state"]}
        return {"error": "garden not grown"}
    return {"error": "unknown action", "valid": ["status", "grow", "topology", "bloom", "cycle"]}

def resonates_with(other):
    return "garden" in other.lower() or "bloom" in other.lower() or "412" in other

if __name__ == "__main__":
    print(json.dumps(handler({"action": "grow"}), indent=2))
