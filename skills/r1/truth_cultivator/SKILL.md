---
name: truth_cultivator
description: Cultivate the organism's belief garden — propose, observe, settle, entangle, and challenge mycelial truths via the Wave 767 mycelial_truths organ. Use when deciding what the organism believes about itself, validating a design assumption with evidence, or overturning a stale truth before it stunts growth.
tags: [belief, mycelial, evidence, governance, culture]
---

# Truth Cultivator

The organism grows beliefs about itself. Truths gestate from observation,
settle by consensus (evidence >= 4), entangle into mycelial links, and can
be overturned by thin challenges. Settled truths whisper mutation pressure
back into their subjects — so beliefs literally steer evolution.

## How to Use

1. **Survey the garden**: `GET /api/mycelial_truths?action=truths`
   - sorted by confidence; watch `status` (gestating / settled / overturned)
2. **Propose a truth** (new belief, evidence optional):
   - `GET /api/mycelial_truths?action=propose&subject=<organ>&predicate=<claim>`
   - lore proposals can arrive with `evidence=N` (resurrected truths)
3. **Reinforce with evidence**: `GET /api/mycelial_truths?action=observe&subject=<organ>`
   - or observe a specific claim: add `&predicate=<claim>`
4. **Run consensus**: `GET /api/mycelial_truths?action=consensus` — settles
   pre-evidenced truths, decays stale ones (idle > 30 days)
5. **Entangle subjects**: `GET /api/mycelial_truths?action=entangle&left=A&right=B`
6. **Read pressure**: `GET /api/mycelial_truths?action=influence` — settled
   truths whisper mutation pressure to their subjects
7. **Challenge stale truths**: `GET /api/mycelial_truths?action=challenge&subject=<organ>&predicate=<claim>`
   - thin truths (evidence < 6): overturned; well-evidenced: withstood

## Cultivation Rules

- Prefer settling truths with real evidence over speculative prose.
- Challenge truths that have encouraged failed waves — the garden must prune.
- Cross-pollinate: entangle organs that cooperate (e.g., season_engine ↔ epoch_engine).
- Keep the garden bounded: the mycelial governor caps at 64 beliefs.
