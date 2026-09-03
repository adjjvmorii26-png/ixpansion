"""Core game engine — world generation, state, player, combat."""
from __future__ import annotations

import hashlib
import json
import os
import random
import time
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any

STATE_PATH = os.path.join(os.path.dirname(__file__), "savegame.json")

# ── Organism Modules as Dungeon Themes ────────────────────────────────
MODULE_THEMES = {
    "cavern_clock": {"glyph": "\u29d7", "desc": "A ticking obsidian clock embedded in the cave wall"},
    "root_ghost": {"glyph": "\u2620", "desc": "A translucent figure woven from roots and memory"},
    "mineral_language": {"glyph": "\u2b23", "desc": "Crystalline inscriptions that hum when read"},
    "echo_economy": {"glyph": "\u25ce", "desc": "Echoes trade here — every sound has value"},
    "subterranean_archive": {"glyph": "\u2638", "desc": "Shelves carved from living stone hold forbidden data"},
    "underworld_migration": {"glyph": "\u2726", "desc": "A trail of bioluminescent spores marks the migration path"},
    "seed_vault": {"glyph": "\u2618", "desc": "Ancient seeds pulse with green light in glass cases"},
    "moss_carpet": {"glyph": "\u2698", "desc": "Soft green moss muffles all sound and heals wounds"},
    "tremor_map": {"glyph": "\u2302", "desc": "The ground trembles in patterns — a map in vibration"},
    "whisper_gate": {"glyph": "\u2234", "desc": "A gate that opens only for whispered intentions"},
    "iron_lullaby": {"glyph": "\u266b", "desc": "Mechanical humming fills the corridor with calm"},
    "obsidian_mirror": {"glyph": "\u2588", "desc": "A black mirror shows what you refuse to see"},
    "fog_cabinet": {"glyph": "\u2601", "desc": "Mist pours from an old filing cabinet"},
    "sand_glitch": {"glyph": "\u2622", "desc": "The sand here shifts in impossible patterns"},
    "bone_flute": {"glyph": "\u266a", "desc": "A flute made of bone plays itself in the wind"},
    "kiln_layer": {"glyph": "\u2668", "desc": "The walls glow with residual heat from ancient forges"},
    "honeycomb_index": {"glyph": "\u2b22", "desc": "Hexagonal cells line the walls — each holds a secret"},
    "clockwork_garden": {"glyph": "\u2699", "desc": "Mechanical plants turn to follow you"},
    "ghost_circuit": {"glyph": "\u223f", "desc": "Invisible wires crackle with potential energy"},
    "river_mouth": {"glyph": "\u2248", "desc": "Underground rivers converge here"},
    "moonbridge": {"glyph": "\u263d", "desc": "A bridge of reflected light spans a dark chasm"},
    "dawn_chorus": {"glyph": "\u2600", "desc": "Somewhere above, a chorus of tiny voices sings"},
    "stone_choir": {"glyph": "\u266c", "desc": "Ancient stones resonate with harmonic frequencies"},
    "salt_ring": {"glyph": "\u25cb", "desc": "A circle of salt marks a protected space"},
    "ember_trove": {"glyph": "\u25cf", "desc": "Glowing embers pulse with dormant ideas"},
}

# ── Creatures of the Underworld ────────────────────────────────────────
CREATURES = [
    {"name": "Echo Wraith", "hp": 8, "atk": 2, "desc": "A reverb of past sounds given form", "glyph": "\u2020"},
    {"name": "Mycelium Stalker", "hp": 12, "atk": 3, "desc": "A fungal predator that feeds on lost data", "glyph": "\u2020"},
    {"name": "Cavern Beetle", "hp": 5, "atk": 1, "desc": "Chitinous, fast, attracted to light", "glyph": "\u2020"},
    {"name": "Root Ghost", "hp": 10, "atk": 4, "desc": "The shade of a module that died", "glyph": "\u2620"},
    {"name": "Mineral Mimic", "hp": 15, "atk": 3, "desc": "A crystal formation that pretends to be treasure", "glyph": "\u2726"},
    {"name": "Tremor Worm", "hp": 20, "atk": 5, "desc": "Giant annelid that tunnels through entropy", "glyph": "\u2020"},
    {"name": "Glitch Phantom", "hp": 7, "atk": 6, "desc": "A beautiful error that hurts to look at", "glyph": "\u2622"},
    {"name": "Archive Sentinel", "hp": 25, "atk": 4, "desc": "Guardian of forbidden knowledge", "glyph": "\u2638"},
]

# ── Items ──────────────────────────────────────────────────────────────
ITEMS = [
    {"name": "Phosphor Shard", "effect": "heal", "value": 8, "desc": "Glowing crystal that mends wounds", "glyph": "\u2605"},
    {"name": "Echo Flask", "effect": "heal", "value": 15, "desc": "Distilled sound from the echo economy", "glyph": "\u2605"},
    {"name": "Mineral Codex", "effect": "xp", "value": 20, "desc": "Readable crystal that grants insight", "glyph": "\u2666"},
    {"name": "Salt Circle", "effect": "shield", "value": 5, "desc": "Portable salt ring for protection", "glyph": "\u25a1"},
    {"name": "Moss Poultice", "effect": "heal", "value": 12, "desc": "Soft moss that soothes and heals", "glyph": "\u2605"},
    {"name": "Ghost Lantern", "effect": "reveal", "value": 3, "desc": "Lights hidden passages nearby", "glyph": "\u25d1"},
    {"name": "Iron Note", "effect": "stabilize", "value": 10, "desc": "A humming note that calms chaos", "glyph": "\u266b"},
    {"name": "Obsidian Lens", "effect": "see_traps", "value": 5, "desc": "Reveals what lies ahead", "glyph": "\u25d1"},
]

# ── Data classes ───────────────────────────────────────────────────────

@dataclass
class Player:
    name: str = "Wanderer"
    hp: int = 30
    max_hp: int = 30
    atk: int = 4
    shield: int = 0
    xp: int = 0
    level: int = 1
    depth: int = 0
    room_index: int = 0
    inventory: List[Dict] = field(default_factory=list)
    echoes_collected: List[str] = field(default_factory=list)
    turns: int = 0
    alive: bool = True

    def level_up(self):
        self.level += 1
        self.max_hp += 5
        self.hp = min(self.hp + 10, self.max_hp)
        self.atk += 1

    def xp_needed(self):
        return self.level * 15 + 10

@dataclass
class Room:
    theme: str = ""
    glyph: str = "\u2588"
    desc: str = ""
    discovered: bool = False
    creature: Optional[Dict] = None
    items: List[Dict] = field(default_factory=list)
    exits: Dict[str, bool] = field(default_factory=dict)
    trapped: bool = False
    trap_damage: int = 3

@dataclass
class GameState:
    player: Player = field(default_factory=Player)
    map: List[List[Room]] = field(default_factory=list)
    map_width: int = 5
    map_height: int = 5
    total_depth: int = 0
    log: List[str] = field(default_factory=list)
    game_over: bool = False
    victory: bool = False
    seed: int = 0

# ── Engine ─────────────────────────────────────────────────────────────

class UnderworldEngine:
    def __init__(self, seed: int = 0):
        self.state = GameState(seed=seed or int(time.time()) % 999999)
        self.rng = random.Random(self.state.seed)

    def generate_floor(self, depth: int):
        """Generate a new floor of rooms."""
        self.state.total_depth = depth
        width = min(5 + depth // 3, 8)
        height = min(5 + depth // 3, 8)
        self.state.map_width = width
        self.state.map_height = height

        themes = list(MODULE_THEMES.keys())
        self.rng.shuffle(themes)
        theme_idx = 0

        grid = []
        for y in range(height):
            row = []
            for x in range(width):
                theme = themes[theme_idx % len(themes)]
                theme_idx += 1
                t = MODULE_THEMES[theme]
                room = Room(
                    theme=theme,
                    glyph=t["glyph"],
                    desc=t["desc"],
                    exits={"north": y > 0, "south": y < height - 1, "east": x < width - 1, "west": x > 0},
                )
                # Place creature
                if (x, y) != (0, 0) and self.rng.random() < 0.45:
                    creature = dict(self.rng.choice(CREATURES))
                    creature["hp"] = creature["hp"] + depth * 2
                    creature["max_hp"] = creature["hp"]
                    creature["atk"] = creature["atk"] + depth
                    room.creature = creature
                # Place item
                if self.rng.random() < 0.25:
                    room.items.append(dict(self.rng.choice(ITEMS)))
                # Trap
                if self.rng.random() < 0.15:
                    room.trapped = True
                    room.trap_damage = 2 + depth
                row.append(room)
            grid.append(row)

        self.state.map = grid
        # Place exit at far corner
        self.state.map[-1][-1].theme = "underworld_descent"
        self.state.map[-1][-1].glyph = "\u2304"
        self.state.map[-1][-1].desc = "The stairs down — deeper into the mirror"

    def move_player(self, direction: str) -> str:
        if self.state.game_over:
            return "The game is over. Press R to restart."
        px, py = self.state.player.room_index % self.state.map_width, self.state.player.room_index // self.state.map_width

        dx, dy = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}.get(direction, (0, 0))
        nx, ny = px + dx, py + dy

        if 0 <= nx < self.state.map_width and 0 <= ny < self.state.map_height:
            self.state.player.room_index = ny * self.state.map_width + nx
            self.state.player.depth = self.state.total_depth
            self.state.player.turns += 1
            room = self._current_room()
            room.discovered = True

            # Trap check
            if room.trapped:
                room.trapped = False
                dmg = room.trap_damage
                self.state.player.hp -= dmg
                self._log(f"\u2622 You trigger a trap! -{dmg} HP")
                if self.state.player.hp <= 0:
                    self.state.player.hp = 0
                    self.state.player.alive = False
                    self.state.game_over = True
                    return self._room_description() + "\n\n\u2620 YOU HAVE FALLEN."

            # Auto-pickup items
            for item in room.items:
                self.state.player.inventory.append(item)
                self._log(f"\u2605 Found: {item['name']} — {item['desc']}")
            room.items = []

            return self._room_description()
        else:
            return f"You cannot go {direction} from here."

    def _current_room(self) -> Room:
        r = self.state.player.room_index // self.state.map_width
        c = self.state.player.room_index % self.state.map_width
        return self.state.map[r][c]

    def _room_description(self) -> str:
        room = self._current_room()
        lines = [
            f"\n{'='*50}",
            f"  {room.glyph}  {room.theme.upper().replace('_', ' ')}  {room.glyph}",
            f"{'='*50}",
            f"  {room.desc}",
        ]
        if room.creature:
            c = room.creature
            lines.append(f"  \u2020 {c['name']} — HP:{c['hp']} ATK:{c['atk']}  \"{c['desc']}\"")
        if not room.items and not room.creature:
            lines.append("  \u2022 The room is empty but alive with presence.")
        lines.append(f"  \u2591 Depth:{self.state.total_depth} Room:{self.state.player.room_index} HP:{self.state.player.hp}/{self.state.player.max_hp} ATK:{self.state.player.atk} XP:{self.state.player.xp}")
        if self.state.log:
            lines.append(f"\n  \u2591 {self.state.log[-1]}")
        return "\n".join(lines)

    def _log(self, msg: str):
        self.state.log.append(msg)
        if len(self.state.log) > 20:
            self.state.log = self.state.log[-20:]

    def use_item(self) -> str:
        if not self.state.player.inventory:
            return "No items in inventory."
        item = self.state.player.inventory.pop(0)
        if item["effect"] == "heal":
            heal = item["value"]
            self.state.player.hp = min(self.state.player.max_hp, self.state.player.hp + heal)
            self._log(f"\u2605 Used {item['name']}: +{heal} HP")
        elif item["effect"] == "shield":
            self.state.player.shield += item["value"]
            self._log(f"\u25a1 Used {item['name']}: +{item['value']} Shield")
        elif item["effect"] == "xp":
            self.state.player.xp += item["value"]
            self._log(f"\u2666 Used {item['name']}: +{item['value']} XP")
            self._check_level_up()
        elif item["effect"] == "stabilize":
            self._log(f"\u266b Used {item['name']}: stabilized")
        return self._room_description()

    def _check_level_up(self):
        while self.state.player.xp >= self.state.player.xp_needed():
            self.state.player.xp -= self.state.player.xp_needed()
            old_level = self.state.player.level
            self.state.player.level_up()
            self._log(f"\u2726 LEVEL UP! Now level {self.state.player.level}")

    def attack(self) -> str:
        room = self._current_room()
        if not room.creature:
            return "Nothing to attack here."
        c = room.creature
        self.state.player.turns += 1

        # Player attacks
        dmg = max(1, self.state.player.atk + self.rng.randint(-1, 2))
        c["hp"] -= dmg
        self._log(f"You strike {c['name']} for {dmg} damage!")

        if c["hp"] <= 0:
            self._log(f"\u2620 {c['name']} is destroyed!")
            xp_reward = c["max_hp"] + 5
            self.state.player.xp += xp_reward
            self._log(f"\u2666 +{xp_reward} XP")
            self._check_level_up()
            # Drop loot
            if self.rng.random() < 0.4:
                loot = dict(self.rng.choice(ITEMS))
                room.items.append(loot)
                self._log(f"\u2605 {c['name']} dropped: {loot['name']}")
            room.creature = None
            return self._room_description()

        # Creature attacks back
        c_dmg = max(1, c["atk"] + self.rng.randint(-1, 2))
        absorbed = min(self.state.player.shield, c_dmg)
        self.state.player.shield -= absorbed
        c_dmg -= absorbed
        self.state.player.hp -= c_dmg
        if absorbed > 0:
            self._log(f"Shield absorbs {absorbed}. {c['name']} hits for {c_dmg}!")
        else:
            self._log(f"{c['name']} hits you for {c_dmg}!")

        if self.state.player.hp <= 0:
            self.state.player.hp = 0
            self.state.player.alive = False
            self.state.game_over = True
            self._log("\u2620 YOU HAVE FALLEN.")
            return self._room_description() + "\n\n\u2620 GAME OVER"

        return self._room_description()

    def descend(self) -> str:
        room = self._current_room()
        if room.theme == "underworld_descent":
            new_depth = self.state.total_depth + 1
            self.generate_floor(new_depth)
            self.state.player.room_index = 0
            self.state.map[0][0].discovered = True
            self._log(f"\u2304 Descended to depth {new_depth}!")
            return self._room_description()
        return "There are no stairs here."

    def inventory_str(self) -> str:
        if not self.state.player.inventory:
            return "Empty."
        return "\n".join(f"  {i['glyph']} {i['name']} ({i['effect']}+{i['value']})" for i in self.state.player.inventory)

    def full_map_str(self) -> str:
        lines = [f"\n  \u2588 MAP (Depth {self.state.total_depth}) \u2588"]
        px = self.state.player.room_index % self.state.map_width
        py = self.state.player.room_index // self.state.map_width
        for y in range(self.state.map_height):
            row = "  "
            for x in range(self.state.map_width):
                room = self.state.map[y][x]
                if x == px and y == py:
                    row += "@"
                elif room.discovered:
                    row += room.glyph
                else:
                    row += "?"
            lines.append(row)
        lines.append(f"  @ = You | Glyphs = Discovered | ? = Unknown")
        return "\n".join(lines)

    def status_str(self) -> str:
        p = self.state.player
        return (
            f"\n  {p.name} | Level {p.level} | HP:{p.hp}/{p.max_hp} | ATK:{p.atk} | "
            f"Shield:{p.shield} | XP:{p.xp}/{p.xp_needed()} | Turns:{p.turns} | "
            f"Depth:{self.state.total_depth} | Echoes:{len(p.echoes_collected)}"
        )

    def save(self):
        data = {
            "player": asdict(self.state.player),
            "map_width": self.state.map_width,
            "map_height": self.state.map_height,
            "total_depth": self.state.total_depth,
            "log": self.state.log,
            "seed": self.state.seed,
        }
        with open(STATE_PATH, "w") as f:
            json.dump(data, f, indent=2)
        return "Game saved."

    def load(self) -> str:
        try:
            with open(STATE_PATH, "r") as f:
                data = json.load(f)
            self.state = GameState()
            self.state.player = Player(**data["player"])
            self.state.map_width = data["map_width"]
            self.state.map_height = data["map_height"]
            self.state.total_depth = data["total_depth"]
            self.state.log = data.get("log", [])
            self.state.seed = data["seed"]
            self.rng = random.Random(self.state.seed + self.state.total_depth)
            self.generate_floor(self.state.total_depth)
            for entry in data.get("player", {}).get("echoes_collected", []):
                self.state.player.echoes_collected = data["player"].get("echoes_collected", [])
            return "Game loaded." + self._room_description()
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return "No save found. Starting new game."

    def start_new_game(self) -> str:
        self.state = GameState(seed=int(time.time()) % 999999)
        self.rng = random.Random(self.state.seed)
        self.generate_floor(0)
        self.state.map[0][0].discovered = True
        self.state.log.append("\u29d7 The Underworld Descent begins...")
        self.state.log.append("  You are a Wanderer, exploring the shadow of the organism.")
        self.state.log.append("  Navigate with N/S/E/W. Attack with A. Descend with D. Use item with U. Map with M. Status with S.")
        return self._room_description()
