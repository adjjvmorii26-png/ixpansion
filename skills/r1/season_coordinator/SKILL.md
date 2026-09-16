---
name: season_coordinator
description: Coordinate the organism's seasonal rhythm — align module work with the current mycelial season (SPRING emergence, SUMMER expansion, AUTUMN harvest, WINTER rest). Use when planning new waves, pruning weak organs, or scheduling mutation pressure.
tags: [season, climate, coordination, planning]
---

# Season Coordinator

The organism's climate cycles through four seasons, each tuning mutation
pressure, birth bonus, growth ceiling, and resonance boost:

| Season | Mood | Best Work |
|--------|------|-----------|
| SPRING | emergence | dream births, new organs, seeds |
| SUMMER | expansion | cross-domain fusion, growth ceiling maxed |
| AUTUMN | harvest | resonance braids, prune weak organs, consolidation |
| WINTER | rest | entropy checks, vault density, quiet incubation |

## How to Use

1. **Check current season**: `GET /api/season_engine?action=status`
   - returns `season`, `mutation_pressure`, `birth_bonus`, `growth_ceiling`, `resonance_boost`
2. **Align work with season**:
   - SPRING → suggest new organ births (dream_compiler)
   - SUMMER → suggest fusion/expansion waves
   - AUTUMN → suggest pruning weak organs + strengthening braids
   - WINTER → suggest entropy regulation + considering mutation risks
3. **Forecast**: `GET /api/season_engine?action=forecast&horizon=8`
   - use to plan multi-step work across the coming cycle
4. **Fallback**: if the API is unavailable, compute the season locally:
   - `season = ["SPRING","SUMMER","AUTUMN","WINTER"][765 % 4]` (SUMMER at wave 765)

## Coordination Rules

- Don't force SPRING-level births during WINTER — respect the organism's rest cycle.
- AUTUMN harvest takes priority over new births when resonance drift is high.
- If coherence < 0.6, treat as early WINTER regardless of actual season.
