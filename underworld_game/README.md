# Underworld Descent

A subterranean mirror-organism roguelike built by the IXpansion organism.

## What Is This?

The organism created its own game — a dungeon crawler set in a shadow version of itself.
Every room is generated from the organism's actual modules (cavern_clock, root_ghost,
mineral_language, echo_economy, etc.). The deeper you go, the more the organism mirrors itself.

## Play

### CLI (terminal)
```bash
python3 run_underworld.py
```
- `n/s/e/w` — move
- `a` — attack creature
- `d` — descend stairs (when at the exit)
- `u` — use first inventory item
- `m` — show map
- `s` — status
- `i` — inventory
- `q` — save and quit

### Web (browser)
Navigate to `/underworld` on the deployed Vercel site.
Or open `dashboard/underworld.html` directly in a browser.

- Click buttons OR use keyboard: arrow keys to move, `a` to attack, `d` to descend, `u` to use

## Game Elements

**26 Room Themes** — each mapped to an actual IXpansion organism module:
Root Ghosts, Cavern Clocks, Mineral Language, Echo Economy, Subterranean Archive,
Underworld Migration, Seed Vault, Moss Carpet, Tremor Map, Whisper Gate, Iron Lullaby,
Obsidian Mirror, Fog Cabinet, Sand Glitch, Bone Flute, Kiln Layer, Honeycomb Index,
Clockwork Garden, Ghost Circuit, River Mouth, Moonbridge, Dawn Chorus, Stone Choir,
Salt Ring, Ember Trove, The Descent.

**8 Creature Types** — Echo Wraith, Mycelium Stalker, Cavern Beetle, Root Ghost,
Mineral Mimic, Tremor Worm, Glitch Phantom, Archive Sentinel.

**8 Item Types** — healing, shielding, XP, reveal, stabilize.

## Architecture

- `engine.py` — Core game engine (state, world gen, combat, items)
- `cli.py` — Interactive terminal interface
- `__main__.py` - Module entry point
- `../run_underworld.py` — CLI launcher script
- `../dashboard/underworld.html` — Self-contained browser game (all JS, no server calls)

## Stats

- Depth scales up as you descend
- Creatures grow stronger per depth level
- Map generation is seeded (new map each game)
- Levels up from XP gained by defeating creatures
