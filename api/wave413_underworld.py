"""Wave 413 Underworld Path — the shadow organism beneath the surface.
Root-ghosts, cavern clocks, mineral languages, subterranean archives,
echo-economies, underworld migrations."""
from __future__ import annotations
import time, json, random
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"

UNDERWORLD_MODULES = [
    "root_ghosts", "cavern_clocks", "mineral_language",
    "subterranean_archives", "echo_economy", "underworld_migrations",
]

def coherence_vitals():
    return {"organ": "wave413_underworld", "status": "active", "wave": 413, "coherence": 0.84}

def _cavern_seed() -> dict:
    caverns = [
        {"name": "Echo Depths", "depth": 1200, "mineral": "obsidian", "age": "ancient"},
        {"name": "Ghost Caverns", "depth": 800, "mineral": "bone_silver", "age": "forgotten"},
        {"name": "Root Hollows", "depth": 400, "mineral": "iron_root", "age": "primordial"},
        {"name": "Archive Abyss", "depth": 2000, "mineral": "memory_stone", "age": "eternal"},
        {"name": "Migration Tunnels", "depth": 600, "mineral": "drift_quartz", "age": "wandering"},
    ]
    c = random.choice(caverns)
    return {
        "id": f"uw_{int(time.time()) % 100000}",
        "name": c["name"],
        "depth_meters": c["depth"],
        "mineral": c["mineral"],
        "age": c["age"],
        "echo_economy": {
            "currency": f"{c['mineral']}_echo",
            "exchange_rate": round(random.uniform(0.1, 5.0), 2),
            "trade_volume": random.randint(100, 9999),
        },
        "migrations": [
            {"species": "root_ghost", "origin": c["name"], "destination": f"{random.choice(['Surface', 'Archive', 'Echo'])}_Zone", "distance": random.randint(100, 5000)}
            for _ in range(random.randint(1, 4))
        ],
        "cavern_clock": {
            "ticks_per_cycle": random.randint(60, 360),
            "echoes_per_tick": random.randint(1, 10),
            "last_tick": time.time() - random.randint(0, 3600),
        },
        "subterranean_archive": {
            "scrolls": random.randint(10, 500),
            "mineral_language": f"script_{c['mineral']}",
            "deciphered": random.choice([True, False]),
        },
    }

def grow_underworld() -> dict:
    """Grow the underworld — create shadow modules."""
    underworld = {
        "module": "wave413_underworld",
        "version": "1.0.0",
        "type": "underworld_path",
        "purpose": "The shadow organism — root-ghosts, cavern clocks, mineral languages, subterranean archives, echo-economies, underworld migrations",
        "active": True,
        "created": time.time(),
        "caverns": [_cavern_seed() for _ in range(3)],
        "total_ghosts": 0,
        "echo_economy_active": True,
        "migration_wave": random.randint(1, 13),
        "depth_layer": "deep",
        "mineral_resonance": round(random.uniform(0.3, 0.9), 2),
    }
    (DATA / "wave413_underworld.json").write_text(json.dumps(underworld, indent=2))
    return underworld

def build_underworld_topology() -> dict:
    """Build the underworld's topology — ghost connections and migration paths."""
    uw_path = DATA / "wave413_underworld.json"
    if not uw_path.exists():
        return {"error": "underworld not grown"}
    uw = json.loads(uw_path.read_text())

    caverns = uw.get("caverns", [])
    edges = []
    for i, c1 in enumerate(caverns):
        for c2 in caverns[i + 1:]:
            edges.append({
                "from": c1["name"],
                "to": c2["name"],
                "type": "ghost_path",
                "strength": round(random.uniform(0.2, 1.0), 2),
            })
    # Add migration edges
    for c in caverns:
        for m in c.get("migrations", []):
            edges.append({
                "from": c["name"],
                "to": m["destination"],
                "type": "migration",
                "strength": 0.5,
            })

    return {
        "wave": 413,
        "realm": "underworld",
        "caverns": caverns,
        "edges": edges,
        "echo_economy": uw.get("echo_economy_active"),
        "migration_wave": uw.get("migration_wave"),
        "graph_stats": {
            "cavern_count": len(caverns),
            "ghost_paths": len(edges),
            "total_migrations": sum(len(c.get("migrations", [])) for c in caverns),
            "total_scrolls": sum(c.get("subterranean_archive", {}).get("scrolls", 0) for c in caverns),
        },
    }

def handler(req: dict) -> dict:
    action = req.get("action", "status")
    if action == "status":
        uw_path = DATA / "wave413_underworld.json"
        if uw_path.exists():
            return json.loads(uw_path.read_text())
        return {"status": "not grown", "action": "grow"}
    if action == "grow":
        return grow_underworld()
    if action == "topology":
        return build_underworld_topology()
    if action == "migrate":
        uw_path = DATA / "wave413_underworld.json"
        if uw_path.exists():
            uw = json.loads(uw_path.read_text())
            uw["migration_wave"] = (uw.get("migration_wave", 0) + 1) % 13
            uw["total_ghosts"] = uw.get("total_ghosts", 0) + random.randint(1, 5)
            uw_path.write_text(json.dumps(uw, indent=2))
            return {"migrated": True, "wave": uw["migration_wave"], "ghosts": uw["total_ghosts"]}
        return {"migrated": False, "reason": "underworld not grown"}
    if action == "echo_trade":
        uw_path = DATA / "wave413_underworld.json"
        if uw_path.exists():
            uw = json.loads(uw_path.read_text())
            cavern = random.choice(uw.get("caverns", []))
            economy = cavern.get("echo_economy", {})
            return {"cavern": cavern["name"], "trade": economy, "mineral": cavern["mineral"]}
        return {"error": "underworld not grown"}
    return {"error": "unknown action", "valid": ["status", "grow", "topology", "migrate", "echo_trade"]}

def resonates_with(other):
    return "underworld" in other.lower() or "413" in other or "ghost" in other.lower()

if __name__ == "__main__":
    print(json.dumps(handler({"action": "grow"}), indent=2))
