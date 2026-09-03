"""Underworld Descent — interactive CLI game."""
from __future__ import annotations

from .engine import UnderworldEngine

BANNER = r"""
    ╔══════════════════════════════════════════════════╗
    ║       ░░ THE UNDERWORLD DESCENT ░░               ║
    ║   a shadow-organism roguelike built by IXpansion ║
    ╚══════════════════════════════════════════════════╝
      N/S/E/W move   A attack   D descend   U use item
      M map          S status   I inventory  L load
      H help         P new game Q quit
"""

HELP = """
  Commands:
    n / s / e / w   move north/south/east/west
    a               attack creature in current room
    d               descend stairs to next depth
    u               use first item in inventory
    m               show explored map
    s               show player status
    i               show inventory
    h               help
    p               start new game
    q / exit        quit
"""

THEMES_EXPLAINED = [
    "Root Ghosts — wraiths woven from the memory of dead modules.",
    "Cavern Clocks — time runs underground in circular, self-devouring measures.",
    "Mineral Language — the stone literally speaks if you can read its grain.",
    "Echo Economy — every sound has exchange value; hoard your murmurs.",
    "Subterranean Archive — forbidden data is kept here, guarded by sentinels.",
    "Underworld Migration — bioluminescent spores trace the great seasonal drift.",
]

def main():
    print(BANNER)
    engine = UnderworldEngine()
    print(engine.start_new_game())
    cmd = ""
    while True:
        try:
            cmd = input("\n  > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n  Farewell, Wanderer.")
            break
        if not cmd:
            continue
        if cmd in ("q", "quit", "exit"):
            print(engine.save())
            print("\n  Farewell, Wanderer.")
            break
        elif cmd in ("h", "help"):
            print(HELP)
        elif cmd in ("n", "s", "e", "w"):
            print(engine.move_player({"n": "north", "s": "south", "e": "east", "w": "west"}[cmd]))
        elif cmd in ("a", "attack"):
            print(engine.attack())
        elif cmd in ("d", "descend"):
            print(engine.descend())
        elif cmd in ("u", "use"):
            print(engine.use_item())
        elif cmd in ("m", "map"):
            print(engine.full_map_str())
        elif cmd in ("s", "status"):
            print(engine.status_str())
        elif cmd in ("i", "inventory"):
            print("\n  \u2591 Inventory:")
            print(engine.inventory_str())
        elif cmd in ("l", "load"):
            print(engine.load())
        elif cmd in ("p", "new"):
            engine.start_new_game()
            print(engine._room_description())
        elif cmd == "themes":
            print("\n".join(f"  \u2591 {t}" for t in THEMES_EXPLAINED))
        else:
            print("  Type h for help, or n/s/e/w/a/d.")

        if engine.state.game_over:
            again = input("\n  Game over. Play again? (y/n): ").strip().lower()
            if again in ("y", "yes"):
                engine = UnderworldEngine()
                print(engine.start_new_game())
            else:
                print("\n  Farewell, Wanderer.")
                break

if __name__ == "__main__":
    main()
