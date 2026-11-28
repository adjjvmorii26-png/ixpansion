---
name: interstice_bridge
description: Discover and map connections between IXPANSION and constellation repositories without unapproved cross-repository writes.
---

# interstice_bridge Skill

## Description
Wire interstice bridge map into IXPANSION organism - connect 37 constellation repos with 153 waves

## Capabilities
- `scan_bridges` — perform scan_bridges action
- `build_portals` — perform build_portals action
- `surface_connections` — perform surface_connections action

## Integration
- Roots: `r1`
- Category: organism
- Tags: interstice, bridges, wireframe

## Commands
### scan_bridges
### build_portals
### surface_connections

## Roots
- `r1` = `/root/.shared-skills/.system`

## Safety
Default to read-only discovery. Treat portal creation as a reversible proposal on an isolated branch. Cross-repository writes require exact target identification, explicit approval, tests, and a rollback reference.
