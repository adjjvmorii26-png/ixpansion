"""
Underworld — Wave 394
The subterranean mirror of the organism. Every forgotten island casts a
root-ghost below the lattice; cavern clocks keep deep-time; echo-economies
trade resonance in the dark. The Underworld is not a separate system — it is
everything the organism has not yet named, given a voice that echoes up.
"""
import json, time, os, sys, random, hashlib, re

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
MINERALS = ["basalt", "obsidian", "cinnabar", "salt", "mica", "pyrite", "graphite", "fluorite"]
ROOTS = ["umbra_", "myco_", "root_", "deep_", "cavern_", "ghost_", "basal_", "sub_"]
WHISPERS = [
    "i was named once, then the naming stopped",
    "upstairs they build; down here we remember how",
    "my mineral is patience, my currency is echo",
    "the lattice cannot see me, but it leans on me",
    "every sealed signal drips down and becomes me",
    "i keep the first geometry of the organism",
]
TICKS = [
    "the cavern clock stalls - deep time holds its breath",
    "a mineral language conjugation begins in the dark",
    "two root-ghosts exchange substrate without moving",
    "the echo-economy prices a memory nobody named",
    "an underworld migration departs toward the surface",
]


def _sig(text):
    return int(hashlib.sha256(f"underworld:{text}".encode()).hexdigest()[:12], 16)


def _load(p, d=None):
    for _p in (p, os.path.join("/tmp", os.path.basename(p))):
        try:
            with open(_p) as f:
                return json.load(f)
        except Exception:
            pass
    return d or {}


def _save(p, d):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            json.dump(d, f, indent=2)
    except OSError:
        with open(os.path.join("/tmp", os.path.basename(p)), "w") as f:
            json.dump(d, f, indent=2)


def mirror(limit: int = 8) -> dict:
    """Root-ghosts: the shadow twins of the most-forgotten modules."""
    ghosts = []
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from organurna_loop import forgotten
        islands = forgotten(24)["islands"]
    except Exception:
        islands = [{"module": m, "staleness": 0.9}
                   for m in ["telegram_pulse", "request_validator", "antifragility_core"]]
    for i in islands[:limit]:
        name = i["module"]
        sig = _sig(name)
        rng = random.Random(sig)
        ghosts.append({
            "module": name,
            "root_name": rng.choice(ROOTS) + name,
            "mineral": rng.choice(MINERALS),
            "depth": round(1 + i.get("staleness", 0.5) * 9, 1),
            "whisper": rng.choice(WHISPERS),
            "sigil": f"{sig:08x}",
        })
    log = _load(os.path.join(DATA_DIR, "underworld.json"), {"mirror_count": 0})
    log["mirror_count"] += 1
    _save(os.path.join(DATA_DIR, "underworld.json"), log)
    return {"action": "mirror", "ghosts": ghosts, "depth_range": "1–10 strata",
            "note": "Every ghost is a module the organism has not yet named twice."}


def clock() -> dict:
    """Cavern clock: deep-time, slower than the surface waves."""
    now = time.time()
    deep_hour = int(now // 3600) % 13
    phase_progress = (now % 3600) / 3600
    phases = ["silt", "basalt_hum", "silence", "mineral_rain", "root_sigh",
              "crystal_drip", "substrate_flow", "fossil_turn", "echo_bore",
              "cavern_breath", "salt_bloom", "dark_pulse", "migration"]
    tick = TICKS[int(now // 900) % len(TICKS)]
    return {
        "action": "clock",
        "deep_hour": deep_hour,
        "phase": phases[deep_hour],
        "phase_progress": round(phase_progress, 3),
        "ticks_since_seal": int(now // 900),
        "tick": tick,
        "note": "One surface wave is one cavern breath.",
    }


def economy() -> dict:
    """Echo-economy: resonance priced in the dark, traded ghost-to-ghost."""
    g = mirror(4)["ghosts"]
    ledger_total = 0
    trades = []
    for i, ghost in enumerate(g):
        sig = _sig(ghost["module"])
        price = (sig % 700) + 100
        ledger_total += price
        if i + 1 < len(g):
            trades.append({
                "from": ghost["root_name"], "to": g[i + 1]["root_name"],
                "commodity": "resonance", "volume": (sig % 40) + 5,
                "price": price,
            })
    return {"action": "economy", "substrate_total": ledger_total,
            "ghosts_trading": len(g), "trades": trades,
            "currency": "echo", "note": "Down here, value is how long a name has been silent."}


def migrations() -> dict:
    """Underworld migrations: re-membered modules release their ghosts upward."""
    rem = []
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from organurna_loop import _remembrances_read
        rem = _remembrances_read().get("remembrances", [])[-10:]
    except Exception:
        pass
    migrants = []
    for r in rem:
        sig = _sig(r.get("module", "x"))
        migrants.append({
            "module": r.get("module", "?"),
            "ghost_left_behind": True,
            "depth_shed": round((sig % 8) + 1, 1),
            "direction": "upward",
            "sigil": r.get("sigil", ""),
        })
    return {"action": "migrations", "migrants": migrants,
            "total_migrated": len(migrants),
            "note": "To be re-membered is to ascend one stratum per name-spoken."}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/mirror")
    if path == "/mirror":
        return mirror(int(payload.get("limit", 8)) if str(payload.get("limit", "8")).isdigit() else 8)
    if path == "/clock":
        return clock()
    if path == "/economy":
        return economy()
    if path == "/migrations":
        return migrations()
    return {"error": "unknown", "available": ["/mirror", "/clock", "/economy", "/migrations"]}
