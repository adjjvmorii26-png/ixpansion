---
name: pentaxis_integrator
description: Plan and validate the IXPANSION integration with the Pentaxis 5D engine through isolated, reviewable changes.
---

# pentaxis_integrator Skill

## Description
Integrate pentaxis-5d-engine as the game engine for IXPANSION - 5D gameplay ↔ organism interface

## Capabilities
- `wire_5d` — perform wire_5d action
- `engine_bridge` — perform engine_bridge action
- `reality_layer` — perform reality_layer action

## Integration
- Roots: `r1`
- Category: game
- Tags: pentaxis, 5d, game_engine

## Commands
### wire_5d
### engine_bridge
### reality_layer

## Roots
- `r1` = `/root/.shared-skills/.system`

## Safety
Keep integration changes on a feature branch and submit a reviewed pull request. Do not rewrite submodule pointers, publish releases, merge, or deploy without exact-target approval, passing checks, and a rollback plan.
