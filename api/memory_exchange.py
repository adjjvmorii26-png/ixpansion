"""Wave 454 — Memory Exchange.

LUMA's catalyzed possibility: "what if modules could trade memories?"

Modules accumulate memory — wave_native, temporal recall, spatial
signatures. Most organisms hoard memory. This organ makes memory a
*currency of the organism*: modules can mint, list, and trade memory
tokens, allowing a module that has lived through a rare event to pass
its experience to a younger sibling.

Trading memory is not deletion — it is *replication with provenance*.
The memory's signature chain proves which modules have held it.

Doctrine: What one module has learned can become what another module
is about to learn. Memory is the organism's wealth; trade is its motion.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List

MEMORY_LEDGER: List[Dict[str, Any]] = []          # every minted memory (with provenance chain)
TRADE_LOG: List[Dict[str, Any]] = []              # every completed trade
MAX_LEDGER = 400


def _sig(*parts: Any) -> str:
    return hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:16]


def mint_memory(module: str, title: str, content: str = "",
                weight: float = 0.5, lineage: str = "wave_born") -> Dict[str, Any]:
    """A module mints a memory it is willing to share."""
    mem_id = _sig("memory", module, title, time.time_ns())
    memory = {
        "memory_id": mem_id,
        "module": module,
        "title": title,
        "content": content or f"a memory of {title} held by {module}",
        "weight": round(max(0.01, min(1.0, float(weight))), 3),
        "lineage": lineage,
        "holder": module,
        "signature_chain": [mem_id],
        "provenance": [{"module": module, "at": time.time()}],
        "minted_at": time.time(),
        "status": "held",
    }
    MEMORY_LEDGER.append(memory)
    if len(MEMORY_LEDGER) > MAX_LEDGER:
        MEMORY_LEDGER.pop(0)
    return memory


def list_memory(memory_id: str, asking_price: float = 1.0) -> Dict[str, Any]:
    """A holder lists a memory on the exchange for trade."""
    mem = next((m for m in MEMORY_LEDGER if m["memory_id"] == memory_id), None)
    if not mem:
        return {"error": "memory not found"}
    mem["status"] = "listed"
    mem["asking_price"] = round(max(0.0, float(asking_price)), 3)
    return mem


def trade_memory(seller: str, buyer: str, memory_id: str,
                 price: float = 1.0) -> Dict[str, Any]:
    """Complete a memory trade. The buyer receives a *copy* with a new
    signature chain link; the seller keeps the original (memory is
    replicated, not lost) but the provenance chain records the swap."""
    mem = next((m for m in MEMORY_LEDGER if m["memory_id"] == memory_id), None)
    if not mem:
        return {"error": "memory not found"}
    if mem.get("status") != "listed":
        return {"error": "memory is not listed for trade"}
    if mem["holder"] != seller:
        return {"error": f"memory is held by {mem['holder']}, not {seller}"}

    # replication with provenance
    child_id = _sig("memory_share", mem["memory_id"], buyer, time.time_ns())
    shared = dict(mem)
    shared["memory_id"] = child_id
    shared["holder"] = buyer
    shared["signature_chain"] = list(mem["signature_chain"]) + [child_id]
    shared["provenance"] = list(mem["provenance"]) + [{"module": buyer, "at": time.time()}]
    shared["price"] = round(max(0.0, float(price)), 3)
    shared["status"] = "held"
    MEMORY_LEDGER.append(shared)
    if len(MEMORY_LEDGER) > MAX_LEDGER:
        MEMORY_LEDGER.pop(0)

    trade = {
        "trade_id": _sig("trade", seller, buyer, memory_id, time.time_ns()),
        "memory_id": mem["memory_id"],
        "shared_memory_id": child_id,
        "title": mem["title"],
        "seller": seller,
        "buyer": buyer,
        "price": shared["price"],
        "chain_length": len(shared["signature_chain"]),
        "traded_at": time.time(),
    }
    TRADE_LOG.append(trade)
    if len(TRADE_LOG) > MAX_LEDGER:
        TRADE_LOG.pop(0)

    # original stays with seller, status back to held
    mem["status"] = "held"
    return trade


def market_ticker(limit: int = 8) -> Dict[str, Any]:
    """The organism's memory market status — recent trades + listed wares."""
    listed = [m for m in MEMORY_LEDGER if m.get("status") == "listed"]
    return {
        "memory_count": len(MEMORY_LEDGER),
        "trade_count": len(TRADE_LOG),
        "listed": [
            {
                "memory_id": m["memory_id"],
                "title": m["title"],
                "holder": m["holder"],
                "asking_price": m.get("asking_price", 1.0),
                "weight": m["weight"],
            }
            for m in listed[-limit:]
        ],
        "recent_trades": TRADE_LOG[-limit:],
        "wealth_note": f"{len(MEMORY_LEDGER)} memories held; {len(TRADE_LOG)} exchanges made.",
    }


def provenance_of(memory_id: str) -> Dict[str, Any]:
    """Trace where a memory has been."""
    mem = next((m for m in MEMORY_LEDGER if m["memory_id"] == memory_id
                or memory_id in m["signature_chain"]), None)
    if not mem:
        return {"error": "memory not found"}
    return {
        "title": mem["title"],
        "signature_chain": mem["signature_chain"],
        "provenance": mem["provenance"],
        "holder": mem["holder"],
    }


def coherence_vitals() -> Dict[str, Any]:
    return {
        "organ": "memory_exchange",
        "status": "trading" if TRADE_LOG else "awaiting_first_swap",
        "memories": len(MEMORY_LEDGER),
        "trades": len(TRADE_LOG),
    }


def resonates_with() -> List[str]:
    return [
        "memory_palace", "memory_index", "synthetic_memory", "echo_depth",
        "wave_chronicle", "oblivion_rite", "nostalgia_engine",
        "resonance_memory", "legacy_vault", "time_capsule", "mind_meld",
        "mycelial_commerce", "commerce_barter", "cultural_exchange",
    ]


def handler(payload: Dict[str, Any] = None, context: Any = None) -> Dict[str, Any]:
    data = payload or {}
    action = data.get("action", "ticker")
    if action == "mint":
        return mint_memory(
            data.get("module", "wanderer"),
            data.get("title", "unnamed memory"),
            data.get("content", ""),
            data.get("weight", 0.5),
            data.get("lineage", "wave_born"),
        )
    if action == "list":
        return list_memory(data.get("memory_id", ""), data.get("asking_price", 1.0))
    if action == "trade":
        return trade_memory(
            data.get("seller", ""),
            data.get("buyer", ""),
            data.get("memory_id", ""),
            data.get("price", 1.0),
        )
    if action == "provenance":
        return provenance_of(data.get("memory_id", ""))
    return market_ticker(data.get("limit", 8))
