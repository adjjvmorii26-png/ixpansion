# IXPANSION

**Multi-agent organism** — governed plugins, evidence-led CI, dual-track lab/main, compact context memory.

> Agents load `pack(budget)`, never chat history. Silence is a product surface.

[![CI](https://github.com/adjjvmorii26-png/ixpansion/actions/workflows/ci.yml/badge.svg)](https://github.com/adjjvmorii26-png/ixpansion/actions/workflows/ci.yml)
[![Live](https://img.shields.io/badge/live-ixpansion--live.vercel.app-black)](https://ixpansion-live.vercel.app)

| Surface | Link |
|---------|------|
| **Prod** | [ixpansion-live.vercel.app](https://ixpansion-live.vercel.app) |
| **Repo** | [adjjvmorii26-png/ixpansion](https://github.com/adjjvmorii26-png/ixpansion) |
| **Context pack** | `context/compact.py` · `context/ledger.jsonl` |
| **Field guide** | dashboard / docs wiki (see open PRs for handbook) |

## What it is now

- **Monorepo** with ALEPH (main) vs lab tracks
- **CI** pinned to `ubuntu-24.04`, CORS allowlist, usage bearer auth
- **Compact context** — typed artifacts (`seed` / `receipt` / `contract` / `pulse` / `pointer` / `residue`) packed under a token budget
- **Draft spine** (not yet on main): root workspace → plugin fabric → runtime → identity gate

## Quick start

```bash
# Context pack for agents
python -m context.compact
pytest tests/test_context_compact.py -q

# Full suite (as in CI)
python -m pytest tests/ -q
```

## Doctrine (short)

1. Evidence before merge — no drafts that still say “tests not run”
2. Compact memory — one fact per ledger line
3. Dual-track — lab experiments stay off main until green
4. Leave the board healthier than you found it

## Connect

- GitHub: [adjjvmorii26-png/ixpansion](https://github.com/adjjvmorii26-png/ixpansion)
- Live: [ixpansion-live.vercel.app](https://ixpansion-live.vercel.app)
- Archive / merge target: [solid-organism](https://github.com/adjjvmorii26-png/solid-organism) (idle)

---

*Wave history and deep lore remain in git history; this surface stays current and compact.*
