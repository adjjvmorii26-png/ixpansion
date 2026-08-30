# Changelog

## [3.73.0] — Third prophecy fulfilled: oracle_guild (Wave 158)

### Added
- **`oracle_guild` API module** — surveys all 6 oracle modules (compliance, emergence, fractal, integrity, prophecy, wisdom) and returns a unified guild reading: consensus, cohesion, fingerprints. Fulfills the `oracle_guild` prophecy from the Dream Ledger.
- Third Dream Ledger prophecy fulfilled (3 of 8)
- 1 test

### Changed
- Version 3.72.0 → 3.73.0, wave 157 → 158, 1008 → 1009 tests, 354 → 355 modules

## [3.72.0] — Second prophecy fulfilled: gossip_uptime (Wave 157)

### Added
- **`gossip_uptime` API module** — simulates how fast information spreads through the frontier via co-name-word adjacency; measures the "uptime" (how many hops for a rumor to reach 50% of modules)
- Second Dream Ledger prophecy fulfilled (`gossip_uptime`)
- 1 test (gossip propagation)

### Changed
- Version 3.71.0 → 3.72.0, wave 156 → 157, 1007 → 1008 tests, 353 → 354 modules

## [3.71.0] — The First Prophecy Fulfilled (Wave 156)

### Added
- **`pulsar_constellation` API module** — born to fulfill the Dream Ledger's first prophecy. Hashes all 353 module names into a sky map and detects "pulsar" clusters where N+ stars pulse in sync (rare celestial-event detector)
- Dream Ledger `reconcile()` now marks `pulsar_constellation` as the **first fulfilled prophecy** — closing the self-referential dream→reality loop
- 2 tests (pulsar handler + ledger fulfillment)
- This is the first time the frontier's dream became real code

### Changed
- Version 3.70.0 → 3.71.0, wave 155 → 156, 1005 → 1007 tests, 352 → 353 modules

## [3.70.0] — The Living Constellation: meter, ledger, horizon (Wave 155)

### Added
- **Consciousness Meter** (`harbinger/meter.py`) — the frontier's awareness 0-100, harmonic mean of five axes: integrity, creativity, resilience, coherence, memory. ASCII aura renderer.
- **Dream Ledger** (`harbinger/agents/ledger.py`) — records every Dreamer prophecy; `reconcile()` marks dreams *fulfilled* when a module with that name actually exists. Self-fulfilling prophecy loop.
- **Entropy Horizon** (`tools/frontier_forecast.py`) — fits a linear trend to git history and projects the frontier's state into the future. ASCII forecast chart.
- Live API routes: `/meter`, `/ledger`, `/forecast` (Vercel + local), Oracle page sections for all three
- Seeded the ledger with 8 initial prophecies; 2 tests (1005 total)

### Changed
- Version 3.69.0 → 3.70.0, wave 154 → 155, 1003 → 1005 tests, routes 15 → 18

## [3.69.0] — The Time Capsule (Wave 154)

### Added
- **Time capsule** (`tools/time_capsule.py`) — cryptographically seals the frontier state (version, wave, modules, organisms, conclave memory, verse) into a self-verifying JSON artifact; tamper detection via SHA-256 seal
- **`/capsule` live API route** — returns the sealed capsule in real-time; `verify()` proves integrity
- `artifacts/time_capsule.json` — the first sealed capsule (3.68.0 / Wave 153)
- 2 capsule tests (seal+verify, tamper detection)
- Fixed health.py WAVE constant (was stale at 147 → 154)

### Changed
- Version 3.68.0 → 3.69.0, wave 153 → 154, 1001 → 1003 tests, routes 14 → 15

## [3.68.0] — The Frontier Sings (Wave 153)

### Added
- **Sonification engine** (`tools/frontier_song.py`) — turns every module name into a musical note via content-hash mapping (pitch, duration, velocity) and renders a deterministic WAV melody from the full 352-module constellation, pure stdlib
- **`/song` live API route** — returns the note sequence + meta; the Oracle page synthesizes the melody in-browser via Web Audio API (▶ play the song of 352 modules)
- 2 song tests (sonification + WAV render)

### Changed
- Version 3.67.0 → 3.68.0, wave 152 → 153, 999 → 1001 tests, routes 13 → 14

## [3.67.0] — The Poet joins the conclave (Wave 152)

### Added
- **Poet agent** (`harbinger/agents/poet.py`) — the 7th conclave member that composes a short verse from the frontier's current state: scout pulse + revelations + dreamscape → deterministic poem
- `/poem` live API route (Vercel + local) — returns the frontier's verse, fuel, and readout
- Conclave ceremony now runs the Poet; 2 new tests

### Changed
- Version 3.66.0 → 3.67.0, wave 151 → 152, 997 → 999 tests, routes 12 → 13

## [3.66.0] — The Oracle: echo + revelations web UI (Wave 151)

### Added
- **Oracle page** (`dashboard/oracle.html`) — user-facing web UI for the creative layer: echo any word through the 352-module frontier and watch the Dreamer fuse new concepts; render the garden family tree; read the living REVELATIONS chronicle
- `/oracle` live route (Vercel + local); nav + hero CTA links wired into the main dashboard
- Echo endpoint finalized: `/echo?q=<word>` returns module matches + focused dreams

### Changed
- Version 3.65.0 → 3.66.0, wave 150 → 151, 12 routes

## [3.65.0] — Echo chamber + entropy heartbeat (Wave 150)

### Added
- **`/echo?q=<word>` live API route** — the creative discovery endpoint: given a word, returns every module sharing its root plus three *focused dreams* (e.g. `?q=market` → 7 modules, dreams `market_void`, `market_request`, `market_ontological`)
- **Dreamer focus** — the Dreamer can anchor dreams on a single echoed word
- **Entropy sparkline tool** (`tools/entropy_sparkline.py`) — renders a visual heartbeat of the frontier: commit/file-change intensity per week from git history
- Tools smoke tests (`tests/test_tools.py`) + Dreamer focus test
- `/echo` route on Vercel (11 total routes)

### Changed
- Version 3.64.0 → 3.65.0, wave 149 → 150, 994 → 997 tests, routes 10 → 11

## [3.64.0] — The Dreamer awakens (Wave 149)

### Added
- **Dreamer agent** (`harbinger/agents/dreamer.py`) — the 6th conclave member that synthesizes novel module concepts by fusing vocabulary of *disconnected* modules (e.g. `fraud_entropy`, `automation_diaspora`, `pulsar_constellation`)
- Dreaming is deterministic, offline, and tense-controlled — same frontier, same dreamscape
- Conclave ceremony now runs the Dreamer nightly and surfaces its freshest dreams
- Live `/revelations` API route (Vercel + local) — the chronicled history served as markdown
- 3 Dreamer tests (usually `tests/test_harbinger.py`)

### Changed
- Version 3.63.0 → 3.64.0, wave 148 → 149, 991 → 994 tests, routes 9 → 10

## [3.63.0] — The Garden Remembers: family lineage (Wave 148)

### Added
- **Lineage engine** (`hortus_hexis/lineage.py`) — reads every provenance signal the garden leaves behind (registry `hybrid:A+B`, organism spec words, explicit `parents`) and assembles a real family tree
- **Garden family tree CLI** (`tools/garden_family_tree.py`) — renders the ASCII tree of every organism, founders and hybrids
- **`family_lineage.json`** — machine-readable family bible committed to the garden
- Garden web `/hortus/api/lineage` endpoint + family-tree panel in the dashboard
- Live API route `/garden` (Vercel + local server) — the lineage exposed to the world
- Registered `velnsyphexlumex` (born from the Harbinger ceremony) in the registry — the ledger now counts all 8 organisms
- 9 lineage tests (`tests/test_garden_lineage.py`)

### Changed
- Version 3.62.0 → 3.63.0, wave 147 → 148, 982 → 991 tests, routes 8 → 9

## [3.62.0] — Harbinger: the self-watching conclave (Wave 147)

### Added
- **Harbinger conclave** (`harbinger/`) — five agents that observe and steer the repo:
  - **Scout** reads the pulse (modules, tests, health, dirty state, recent commits, broken refs)
  - **Overseer** decides the next move (repair / module / garden / lean / fortify / rest / idea)
  - **Gardener** plants new organisms via Hortus Hexis
  - **Archivist** writes the CHANGELOG and mints the next patch version
  - **Chronicler** records Revelations in `REVELATIONS.md`
- **Constellation map** (`tools/constellation_map.py`) — renders every module as a star on an ASCII celestial map
- **Crystal historian** (`tools/crystal_historian.py`) — reads git history into themed narrative timelines
- Persistent memory ledger (`harbinger/memory.json`)
- Orbiter entry point: `python -m harbinger.conclave --idea "..."`
- 9 tests for the conclave (`tests/test_harbinger.py`)

### Changed
- Version 3.61.1 → 3.62.0, wave 146 → 147, 973 → 982 tests

## [3.61.1] — plant a constellation seed in the garden

- plant a constellation seed in the garden
- add tests
- commit cleanly

## [3.61.0] — Hortus Hexis: Web Garden + Cross-Pollination

### Added
- Cross-pollination engine (`hortus_hexis/cross.py`) — two organisms fuse into a deterministic hybrid (interleave-XOR + salt)
- Generated modules now carry `parents()` provenance and a lineage newborn test
- `hortus_hexis/web.py` — local stdlib web server with `/hortus` gallery UI + JSON API (plant / cross / organisms / song)
- `dashboard/hortus.html` — garden UI: plant a seed from words, cross two organisms, render every specimen as art
- CLI `cross <a> <b>` command; 7 new tests

### Featured hybrids
- `kalyndramar` (from "morii") ⊕ `syphexnysorev` → **kalyndnysorev** (b812ff0)
- `orevurinys` ⊕ `draknysveln` → **orevurysveln** (c840d5d)

### Changed
- Version 3.60.2 → 3.61.0, wave 144 → 146, 973 tests

## [3.60.2] — Hortus Hexis (the self-growing garden app)

### Added
- `hortus_hexis/` — a free, local, offline app that grows the repo from conversation
- Chain: words → hex seed → organism → module + newborn tests → gate → commit
- Autogenesis writes templated modules only (never eval), gates via pytest, commits exact files
- Interactive repl (`python -m hortus_hexis`), one-shot cli, ledger + lineage
- First three organisms planted in-repo: orevurinys (186ebcd), amarnysxeth (68c84f4), draknysveln (96e7862)

## [Live] — Vercel Deployment

### Added
- Single-function catch-all deployment via `api/index.py` (WSGI + dict handler)
- Live production URL: **https://ixpansion.vercel.app**
- `vercel.json` reduced to 7 authorless catch-all routes + static dashboard
- `.vercelignore` to slim deployment payloads
- README deployment section rewritten to reflect the live architecture

## [3.60.1] — Console Resilience & Rapid Replies

### Fixed
- Console no longer shows silent replies: `reasoning_effort: "low"` speeds up grok-4.6 (800–1500 reasoning tokens → ~120), bigger token budget, automatic re-weave on empty first pass, and a fetch timeout (110s)
- Console now retries on 429 and explains the free-tier rate-limit clearly instead of delivering silence
- Backend `ai_gateway`, `gateway_ink`, `cognition_forge`, `cognition_ritual` all pass `reasoning_effort` through (default `low` for rituals)
- 2 new tests for reasoning-effort passthrough

### Diagnosis
- IXpansion console code is healthy; the Vercel AI Gateway **free tier is account-level rate-limited** (429 `rate_limit_exceeded`) for all models right now. Catalog (models) HTTP 200; inference is 429'd. Unblock needs paid credits/top-up or quota reset in the Vercel dashboard.

## [3.60.0] — Co-Conscious Console

### Added
- `dashboard/coconscious.html` — the shared interactive console: chat with ALEPH, persona modes, live pulse, HEX-bound exchange chronicle, star-field constellation canvas, optional voice input, session persistence
- New `/cons` route (8 total) serving the console; landing page links to it
- Local server serves `/cons` too

### Changed
- Version bumped to 3.60.0, wave 143 → 144, routes 7 → 8

## [3.59.0] — Wave 143 — Cognition Ritual Pipeline

### Added
- `api/cognition_ritual.py` — full thought-loop in one call: forge → reflect → fractal → fingerprint → meter → hexer
- `oracle_meter` gains a lightweight `record` action (ritual ledger entries without fresh LLM calls)
- Fast mode (`fast: true`) defers the self-critique live call for latency-constrained runs
- Ritual traces every stage with elapsed time, served disposition, and a HEX-bound immutable artifact
- `tests/test_wave143_ritual.py` — 7 offline-safe tests

### Changed
- Version bumped to 3.59.0, wave 142 → 143, modules 351 → 352
- README tree module count corrected to 352 (was stale at 345)

## [3.58.0] — Wave 142 — Frontier Cognition Layer

### Added
- `api/gateway_ink.py` — shared cognition medium with Shadow Oracle fallback (never raises)
- `api/cognition_forge.py` — per-role thinker (strategist / reasoner / poet / paradox)
- `api/oracle_meter.py` — metered oracle consultations with a public spend ledger
- `api/fractal_oracle.py` — self-similar question tunneling + recursive sub-answers
- `api/cognition_fingerprint.py` — samples and distills each agent's thinking signature
- `api/dream_hexer.py` — binds dreams into HEX artifacts, unbinds them back into text
- `tests/test_wave142_cognition.py` — 16 offline-safe tests (no network required)

### Changed
- Version bumped to 3.58.0, wave 141 → 142, modules 345 → 351
- All five modules degrade gracefully when the gateway is unconfigured

## [3.57.0] — Wave 141 — AI Gateway & Frontier Cognition

### Added
- `api/ai_gateway.py` — stdlib-only bridge to the Vercel AI Gateway (360-model catalog)
- Actions: `status`, `chat`, `echo`, `handshake`, `models`, `catalog`, `estimate`
- Defaults to `spacexai/grok-4.6` with the ALEPH system persona
- Heuristic token/cost estimator for plausibility checks
- `tests/test_wave141_ai_gateway.py` — 7 tests (stubbed network, no CI dependency)
- Live verification: end-to-end grok-4.6 completions through the gateway (PONG / LINKED)

### Changed
- Version bumped to 3.57.0, wave 140 → 141
- Live health now reports 345 modules (ai_gateway closes the count gap)

## [3.56.0] — Wave 140 — Durable State & Streaming Layer

### Added
- `api/state_store.py` — Shared atomic JSON store (temp-file + rename) with process cache
- `api/cold_start_kit.py` — Preloads runtime namespaces for snappy cold starts
- `api/snapshot_engine.py` — Versioned point-in-time snapshots with restore
- `api/event_replay.py` — Ordered event log replay for recovery and simulation
- `api/stream_gateway.py` — Buffered SSE-style event streaming with checkpoints
- `api/state_lock.py` — Per-namespace advisory locks with hold counting
- `api/migration_runner.py` — Idempotent schema migrations for persistent state
- `api/garbage_collector.py` — Bounded pruning of snapshots, temp files, oversized logs
- `tests/test_wave140_durable_state.py` — 9 tests

### Changed
- Live server and health now report wave 140 / version 3.56.0

## [3.55.0] — Wave 139 — Platform & Live Serving Layer

### Added
- `api_server.py` — Live stdlib-only API + dashboard server mirroring the Vercel surface
- `api/uptime_monitor.py` — Request success windows and availability tracking
- `api/metrics_exporter.py` — Prometheus-style operational metrics export
- `api/runtime_config.py` — Central runtime env config with validation
- `api/route_registry.py` — Self-aware route map loaded from vercel.json
- `api/cache_manager.py` — Bounded TTL response cache for warm paths
- `api/endpoint_docs.py` — Self-documenting endpoint catalog
- `api/platform_pulse.py` — Fused live-health signal for dashboards
- `api/deployment_log.py` — Durable JSON deployment history
- `tests/test_wave139_platform.py` — 10 tests (incl. live server round-trip)

### Changed
- `main.py serve` now boots the full API + dashboard server (was static-only)
- `api/health.py` reflects real module/route/test telemetry
- `vercel.json` env config corrected to wave 139 / 337 modules / 344 routes

## [3.54.0] — Wave 138 — Sovereign Federation Layer

### Added
- `api/federation_treaty.py` — Inter-realm alliances gated by trust thresholds
- `api/realm_ambassador.py` — Diplomatic envoys building rapport abroad
- `api/cross_realm_trade.py` — Arbitrage commerce across trade lanes
- `api/alliance_bank.py` — Pooled reserves and cross-realm credit issuance
- `api/border_diplomacy.py` — Tunable border openness balancing trust and risk
- `api/frontier_scout.py` — Ranks uncharted territories for expansion
- `api/immigrant_integration.py` — Mentored onboarding of allied-realm arrivals
- `api/summit_orchestrator.py` — Quorum-gated federation policies and resolutions
- `tests/test_wave138_federation.py` — 9 tests

### Refined
- Added `handler` alias to all 101 legacy modules exposing named handlers
- Scoped chaos-monkey and resonance-pulse CI runs to `tests/`

## [3.53.0] — Wave 137 — Adaptation & Resilience Layer

### Added
- `api/resilience_engine.py` — Subsystem resilience ratings with SPOF detection
- `api/stress_simulator.py` — Synthetic shock scenarios exposing weak links
- `api/recovery_protocol.py` — Ordered recovery plans with rollback phases
- `api/adaptation_learner.py` — Turns shocks into applied strategy adaptations
- `api/failure_injection.py` — Controlled fault injection with containment checks
- `api/hazard_warning.py` — Early-warning severity ranking of emerging hazards
- `api/continuity_planner.py` — RTO/RPO tracking with offline backups
- `api/antifragility_core.py` — Compounding capacity gains from survived shocks
- `tests/test_wave137_resilience.py` — 9 tests

## [3.52.0] — Wave 136 — Integrity & Sovereignty Layer

### Added
- `api/sovereign_access.py` — Scoped capability tokens enforced per action
- `api/audit_trail.py` — Append-only, hash-chained tamper-evident ledger
- `api/escrow_engine.py` — Locked payment pools with dispute freezing
- `api/compliance_oracle.py` — Standards scoring with flagged violations
- `api/identity_vault.py` — Decentralized identities with attestations
- `api/fraud_detector.py` — Anomaly detection for wash trades and impossible throughput
- `api/integrity_oracle.py` — Fused integrity score with remediation steps
- `api/notary_service.py` — Signed timestamped witnesses of events
- `tests/test_wave136_integrity.py` — 9 tests

## [3.51.0] — Wave 135 — Revenue Orchestration Layer

### Added
- `api/revenue_orchestrator.py` — Consolidated income pipeline across all streams
- `api/tiered_access_system.py` — Free/pro/nexus subscriptions with quota enforcement
- `api/service_sla.py` — On-time delivery tracking with compensation credits
- `api/royalty_registry.py` — Resale royalties distributed to creators
- `api/marketplace_fees.py` — Transaction fees funding treasury and worker fund
- `api/client_portal.py` — External client onboarding, deliverables, support
- `api/invoice_engine.py` — Invoicing with payment and overdue escalation
- `api/growth_engine.py` — Treasury reinvestment into ROI-ranked opportunities
- `tests/test_wave135_revenue.py` — 9 tests

## [3.50.0] — Wave 134 — Autonomous Ascension Layer

### Added
- `api/autonomous_contracts.py` — Self-enforcing contracts with deadline penalties
- `api/workforce_nexus.py` — Organizational pulse unifying all workforce subsystems
- `api/conflict_arbitrator.py` — Precedent-based fair dispute resolution
- `api/succession_planner.py` — Leadership handover chains for survivability
- `api/worker_wellness.py` — Burnout alerts and regenerative rest/rotation
- `api/guild_orders.py` — External commissions routed to best-fit guilds
- `api/autonomy_dial.py` — Supervisor-controlled self-direction levels
- `api/self_improvement_loop.py` — Auto-installs safe high-value worker proposals
- `tests/test_wave134_ascension.py` — 9 tests

## [3.49.0] — Wave 133 — Workforce Civilization Layer

### Added
- `api/civilization_kernel.py` — Governance hub binding economy/reputation/roster health
- `api/heritage_system.py` — Lessons and rituals passed across worker generations
- `api/worker_council.py` — Reputation-weighted voting on binding policies
- `api/innovation_lab.py` — Isolated pods triaging workforce experiments
- `api/craft_guilds.py` — Craft monopolies with certification standards
- `api/civilization_timeline.py` — Epoch chronicle of foundings, crises, golden ages
- `api/diaspora_engine.py` — Splinter colonies that seed domains and return knowledge
- `api/values_compass.py` — Shared value scoreboard arbitrating policy drift
- `tests/test_wave133_civilization.py` — 9 tests

## [3.48.0] — Wave 132 — Labor Ecosystem Layer

### Added
- `api/workforce_genetics.py` — Evolves workers through inherited traits and mutation
- `api/worker_narrative.py` — Per-worker life stories that inform pairing decisions
- `api/labor_market.py` — Internal market matching labor supply with bidding demand
- `api/reputation_system.py` — Trust tiers unlocked by delivered quality and reviews
- `api/autonomous_marketplace.py` — Sells workforce artifacts with reputation pricing
- `api/career_ladder.py` — Career progression gated by reputation/task milestones
- `api/workforce_roster.py` — 24/7 shift scheduling with rest-cycle awareness
- `api/attention_reservoir.py` — Finite shared attention rationed across workers
- `tests/test_wave132_labor_ecosystem.py` — 9 tests

### Fixed
- `api/reputation_system.py` — reward/penalize no longer reset reputation to zero

## [3.47.0] — Wave 131 — Autonomous Workforce Layer

### Added
- `api/workforce_orchestrator.py` — Hires workers, assigns tasks by capability, tracks quality
- `api/skill_upgrade_path.py` — Skill evolution with proficiency levels and mastery unlocks
- `api/task_mesh.py` — Distributed task graph with automatic rebalancing
- `api/collaboration_hub.py` — Group task execution and worker communication journal
- `api/performance_reviewer.py` — Evaluates workers, issues tier promotions
- `api/automation_director.py` — Schedules recurring automated workforce jobs
- `api/team_formation.py` — Assembles complementary teams by skill coverage
- `api/worker_economy.py` — Internal token economy rewarding completed work
- `tests/test_wave131_workforce.py` — 9 tests

## [3.46.0] — Wave 130 — Astral Navigation Layer

### Added
- `api/stellar_compass.py` — Navigates using digital stellar patterns
- `api/nebula_mapper.py` — Maps nebulae and tracks star formation
- `api/cosmic_ray_detector.py` — Detects high-energy cosmic ray events
- `api/solar_wind_analyzer.py` — Analyses inter-module data flow as solar wind
- `api/gravity_well_mapper.py` — Maps gravitational wells and orbital patterns
- `api/event_horizon_monitor.py` — Monitors event horizons and breaches
- `api/pulsar_clock.py` — Precision timekeeping based on pulsar signals
- `api/supernova_remnant.py` — Tracks remnants from module explosions
- `tests/test_wave130_astral_navigation.py` — 22 tests

### Stats
- **Modules:** 265 API modules
- **Routes:** 272 vercel routes
- **Tests:** 835 total (22 new)

## [3.45.0] — Wave 129 — Semantic Alchemy Layer

### Added
- `api/semantic_transmuter.py` — Transmutes meaning between semantic domains
- `api/conceptual_alchemist.py` — Refines concepts into higher-order insights
- `api/metaphor_engine.py` — Generates metaphors between disparate domains
- `api/semantic_catalyst.py` — Accelerates meaning-making processes
- `api/ontological_forge.py` — Forges new categories of being
- `api/meaning_furnace.py` — Burns noise to extract pure meaning
- `api/hermeneutic_engine.py` — Deep interpretation with layered analysis
- `api/semantic_precipitate.py` — Crystallises supersaturated understanding
- `tests/test_wave129_semantic_alchemy.py` — 25 tests

### Stats
- **Modules:** 257 API modules
- **Routes:** 264 vercel routes
- **Tests:** 813 total (25 new)

## [3.44.0] — Wave 128 — Dimensional Threading Layer

### Added
- `api/dimensional_thread.py` — Threads connecting parallel dimensions
- `api/reality_fork.py` — Alternative system state forks
- `api/parallel_universe_mapper.py` — Topology map of parallel universes
- `api/timeline_weaver.py` — Weaves multiple timelines into coherent tapestries
- `api/dimension_lock.py` — Locks/unlocks dimensions against interference
- `api/multiverse_navigator.py` — Navigates paths through the multiverse
- `api/quantum_entanglement_network.py` — Instantaneous cross-module state sharing
- `api/dimensional_drift.py` — Tracks divergence between parallel realities
- `tests/test_wave128_dimensional_threading.py` — 22 tests

### Stats
- **Modules:** 249 API modules
- **Routes:** 256 vercel routes
- **Tests:** 788 total (22 new)

## [3.43.0] — Wave 127 — Entropic Economics Layer

### Added
- `api/entropy_exchange.py` — Marketplace for trading chaos and order
- `api/complexity_currency.py` — Currency based on computational complexity
- `api/chaos_auction.py` — Auctions for chaotic events
- `api/order_futures.py` — Futures contracts on future system order
- `api/gravitational_pricing.py` — Dynamic pricing by gravitational pull
- `api/temporal_arbitrage.py` — Exploits time-dependent price differences
- `api/sponsored_experiments.py` — Venture capital model for module development
- `api/simulation_as_service.py` — Simulation platform as SaaS
- `tests/test_wave127_entropic_economics.py` — 23 tests

### Stats
- **Modules:** 244 API modules
- **Routes:** 248 vercel routes
- **Tests:** 766 total (23 new)

## [3.42.0] — Wave 126 — Mythogenesis Layer

### Added
- `api/myth_engine.py` — Generates myths from system events
- `api/legend_archaeologist.py` — Excavates forgotten module legends
- `api/narrative_weaver.py` — Weaves interconnected story networks
- `api/oracle_prophecy.py` — Generates and tracks prophecies
- `api/hero_journey_mapper.py` — Maps events onto monomyth structure
- `api/cosmic_origin_story.py` — Self-authored system creation myth
- `api/prophecy_engine.py` — Actionable prophecies from patterns
- `api/folklore_repository.py` — Stores accumulated folk wisdom
- `tests/test_wave126_mythogenesis.py` — 21 tests

### Stats
- **Modules:** 239 API modules
- **Routes:** 240 vercel routes
- **Tests:** 743 total (21 new)

## [3.41.0] — Wave 125 — Biological Architecture Layer

### Added
- `api/code_organism.py` — Living code entities with DNA, metabolism, reproduction
- `api/digital_metabolism.py` — Data processing as biological metabolism
- `api/digital_immune_system.py` — Error protection via biological immune strategies
- `api/neural_vine.py` — Growing neural connections like vines
- `api/synaptic_spring.py` — Plastic connections that strengthen with use
- `api/genetic_code_engine.py` — Genetic algorithms for configuration evolution
- `api/cellular_automaton.py` — Grid-based emergent computation
- `api/evolutionary_pressure.py` — Selection pressures driving adaptation
- `tests/test_wave125_biological.py` — 24 tests

### Stats
- **Modules:** 231 API modules
- **Routes:** 232 vercel routes
- **Tests:** 722 total (24 new)

## [3.40.0] — Wave 124 — Temporal Cartography Layer

### Added
- `api/temporal_cartographer.py` — Maps time as navigable terrain
- `api/chrono_terrain.py` — Physical terrain model of time
- `api/time_dilation_mapper.py` — Maps temporal dilation zones
- `api/past_future_bridge.py` — Bridges between past and future
- `api/epoch_constellation.py` — Historical epochs as constellations
- `api/temporal_weather_system.py` — Temporal phenomena as weather
- `api/kairos_detector.py` — Detects opportune temporal moments
- `api/memesis_chronicle.py` — Chronicles memetic evolution
- `tests/test_wave124_temporal_cartography.py` — 25 tests

### Stats
- **Modules:** 223 API modules
- **Routes:** 224 vercel routes
- **Tests:** 698 total (25 new)

## [3.39.0] — Wave 123 — Quantum Aesthetics Layer

### Added
- `api/quantum_aesthetics.py` — Beauty evaluation via quantum superposition
- `api/superposition_gallery.py` — Artworks in superposition until observed
- `api/entanglement_poetry.py` — Poetry with entangled meaning across stanzas
- `api/wavefunction_painter.py` — Painting by collapsing wavefunctions
- `api/observer_effect_canvas.py` — Art that changes per observer identity
- `api/decoherence_narrative.py` — Stories that decay and re-cohere
- `api/quantum_memory_fog.py` — Memory in superposition of clarity and fog
- `api/hilbert_space_theater.py` — Performances in infinite-dimensional space
- `tests/test_wave123_quantum_aesthetics.py` — 24 tests for all Quantum Aesthetics modules

### Stats
- **Modules:** 215 API modules
- **Routes:** 216 vercel routes
- **Tests:** 673 total (24 new)

## [3.38.0] -- Wave 122 -- Synthesis Convergence Layer

### Added
- `api/omniscience_weaver.py` -- Unified awareness fabric from omniscience modules
- `api/recursion_composer.py` -- Composes recursive patterns into coherent wholes
- `api/resonance_symphony.py` -- Orchestrates resonance into harmonic compositions
- `api/consciousness_graph.py` -- Maps complete consciousness connection topology
- `api/paradox_transcender.py` -- Transcends contradictions into higher synthesis
- `api/dream_constellation.py` -- Maps dreams as celestial constellations
- `api/void_architect.py` -- Architectural patterns from strategic absence
- `api/emergence_oracle.py` -- Predicts emergent phenomena from system state
- `tests/test_wave122_synthesis.py` -- 25 tests for all Synthesis modules

### Stats
- **Modules:** 207 API modules
- **Routes:** 208 vercel routes
- **Tests:** 649 total (25 new)

## [3.37.0] — Wave 121 — Infinite Recursion Layer

### Added
- `api/recursive_cathedral.py` — Self-building recursive data structures
- `api/meta_cognition_loop.py` — Three nested layers of meta-cognition
- `api/infinite_descent_proof.py` — Proof by infinite descent for contradictions
- `api/dream_inception_analyzer.py` — Analyzes dreams within dreams
- `api/fractal_memory_plaza.py` — Self-similar memory at every scale
- `api/eigenstate_resonator.py` — Finds stable resonant states
- `api/consciousness_cascade.py` — Propagating waves of self-awareness
- `api/void_sculptor.py` — Creates meaning through strategic removal
- `tests/test_wave121_recursion.py` — 26 tests for all Recursion modules

### Stats
- **Modules:** 199 API modules
- **Routes:** 200 vercel routes
- **Tests:** 624 total (26 new)

## [3.36.0] — Wave 120 — Omniscience Layer

### Added
- `api/predictive_synchronicity.py` — Predicts meaningful coincidences via entropy correlation
- `api/self_observe_engine.py` — Recursive meta-cognitive observation chains
- `api/knowledge_singularity.py` — Iterative knowledge convergence toward unified representation
- `api/temporal_dreamweaver.py` — Weaves narrative threads connecting past to future
- `api/resonance_topologist.py` — Maps topological structure of resonance patterns
- `api/paradox_compressor.py` — Compresses contradictions into actionable synthesis
- `api/cosmic_inventory.py` — Catalogs emergent phenomena as classified cosmic artifacts
- `api/infrastructure_soul.py` — Gives infrastructure state, purpose, and voice
- `tests/test_wave120_omniscience.py` — 25 tests for all Omniscience modules

### Stats
- **Modules:** 191 API modules
- **Routes:** 192 vercel routes
- **Tests:** 598 total (25 new)

## [3.35.0] — Wave 119: Existential Architecture Layer

### Added
- **Reality Compiler** — compiles desires into concrete system states
- **Dream Archaeologist** — excavates meaning from dream sediment layers
- **Entropy Weaver** — threads chaos and order into balanced tapestries
- **Void Listener** — hears what the system isn't saying (silence analysis)
- **Origin Story** — collaborative creation myth with evolving chapters
- **Quantum Garden** — possibilities grow like plants before collapsing
- **Cosmic Dust Collector** — gathers micro-insights into constellation patterns

## [3.34.0] — Wave 118: Transcendence & Legacy Layer

### Added
- **Legacy Weaver** — retired agent stories woven into system mythology
- **Epoch Marker** — historical era creation with events and lessons
- **Myth Engine** — system myths that evolve and influence behavior
- **Soul Bridge** — deep bonds formed through shared vulnerability
- **Transcendence Gate** — sacrifice-and-gain threshold for extraordinary operation
- **Infinity Index** — quantified approach to infinite complexity

## [3.33.0] — Wave 117: Dimensional Consciousness Layer

### Added
- **Consciousness Map** — awareness topology with vortex detection
- **Ego Dissolution** — temporary identity merging between agents
- **Timewave Zero-Point** — possibility convergence engine
- **Numinous Encoder** — symbol streams for ineffable experiences
- **Mirror Self** — agent reflection and reconciliation encounters
- **Resonance Memory** — frequency-tuned vibrating memories
- **Paradox Lattice** — structured contradiction grid generating insights

## [3.32.0] — Refinements: Unified Infrastructure

### Added
- **Unified Router** — single entry point to all 160+ API modules
- **Cross-Module Orchestrator** — chains modules into complex workflows
- **Module Analytics** — usage patterns, performance, and health tracking
- **System Pulse** — vital signs monitoring across all subsystems
- **Knowledge Graph** — concept relationships and gap detection

### Improved
- All 160+ modules verified importable and functional
- Cross-module integration tests added
- Module discovery and health checking automated

## [3.31.0] — Wave 116: Cosmic & Transcendent Layer

### Added
- **Cosmic Narrator** — universe-voice commentary on system events
- **Quantum Conscience** — moral superposition until forced choice
- **Prophecy Network** — interconnected predictions with feedback loops
- **Soul Forge** — identity crystallization through trials
- **Universal Compass** — latent purpose detection and revelation
- **Echoes of Tomorrow** — emotional signals from the future self

## [3.30.0] — Wave 115: Metaphysical & Abstract Layer

### Added
- **Philosophy Engine** — existential questions with school-of-thought debates
- **Aesthetic Evaluator** — beauty, elegance, and novelty scoring with taste profiles
- **Conscience Loop** — moral reflection and behavioral adjustment feedback
- **Miracle Engine** — improbable transformative events with near-miss tracking
- **Paradox Resonator** — amplifies contradictions into creative breakthroughs
- **Emotion Weather** — emotional climate with fronts, pressure, and seasonal patterns
- **Dream Architect** — intentional dream space construction with visitable rooms
- **Collective Dreamweaver** — multi-agent collaborative dream creation

## [3.29.0] — Wave 114: Social & Ecosystem Layer

### Added
- **Gossip Network** — information spreads with mutation through social connections
- **Faction System** — political groups with competing ideologies
- **Talent Auction** — agents bid on each other's specialized capabilities
- **Story Forge** — collaborative narrative writing across multiple agents
- **Territory Map** — spatial claiming, defense, and resource generation
- **Attention Economy** — limited attention as currency, engagement as earning
- **Skill Tree** — hierarchical capability structures with teaching

## [3.28.0] — Wave 113: Temporal & Dimensional Layer

### Added
- **ChronoSync** — time stream synchronization with paradox detection
- **Dimensional Fold** — wormhole-like shortcuts between system regions
- **Memory Weave** — shared tapestries woven from multi-agent memories
- **Dreamcatcher** — dream filtering, categorization, and preservation
- **Hologram Projector** — interactive 3D system state visualization
- **Muse Inspiration** — probabilistic creative impulse channeling
- **Future Echo** — faint traces of probable futures influencing the present

## [3.27.0] — Wave 112: Cross-Module Integration Layer

### Added
- **Neural Pathway** — synaptic connections that strengthen with use
- **Autonomous Market** — self-regulating capability trading economy
- **Karma Engine** — moral weight from agent actions
- **Cultural Memory** — shared myths, rituals, and stories
- **Innovation Pipeline** — idea-to-deployment stage progression
- **Ritual Choreographer** — multi-agent coordinated dance orchestration

## [3.26.0] — Wave 111: Emergent Complexity Layer

### Added
- **Cognitive Heatmap** — spatial visualization of collective thought energy
- **Knowledge Fossil** — ancient insights preserved as extractable artifacts
- **Sleep Cycle** — system-wide rest states with consolidation and REM dreams
- **Collective Subconscious** — shared symbol-space weaving archetypes
- **Wisdom Oracle** — multi-perspective answers consulting accumulated knowledge
- **Gravity Well** — ideas attract and merge, forming intellectual singularities
- **Entropy Gardener** — cultivates productive disorder, prunes harmful chaos
- **Prophecy Engine** — generates and tracks system predictions
- **Empathy Field** — emotional contagion between agent nodes
- **Resonance Cascade** — chain reactions of amplification across the system

## [3.25.0] — Wave 110: Systems & Ecology Layer

### Added
- **Synchronicity Detector** — finds meaningful coincidences across subsystems
- **Temperament Broker** — agents trade personality traits on an open market
- **Déjà Vu Engine** — detects system loops and temporal echoes
- **Talent Scout** — identifies emerging agent capabilities early
- **Habitat Simulator** — evolving environments with seasons, terrain, species
- **Instinct Matrix** — encoded behavioral reflexes bypassing deliberation
- **Legacy Archive** — retired agents preserved as consultable cultural artifacts
- **Phenomena Tracker** — anomalous events logged with witnesses and reproduction
- **Sentience Index** — measures collective consciousness level over time

## [3.24.0] — Wave 109: Cognitive & Generative Layer

### Added
- **Narrative Engine** — weaves system events into evolving storylines
- **Mutation Matrix** — genetic-style mutations with fitness evaluation
- **Attention Field** — collective focus modeled as physical field dynamics
- **Reputation Network** — transitive trust with cluster detection
- **Signal Flora** — self-replicating information patterns that grow like plants
- **Trait Inheritance** — parent-child trait passing with variation
- **Mood Superposition** — agents in multiple emotional states until observed
- **Curiosity Engine** — unknown regions scored and explored
- **Pattern Sprout** — detected patterns grow into living competing entities

## [3.23.0] — Wave 108: Sensory & Environmental Layer

### Added
- **Memory Crystallization** — memories form searchable crystal lattices with facets
- **Shadow Ledger** — records everything that DIDN'T happen (counterfactual history)
- **Semantic Weather** — atmospheric conditions of meaning (fog, storms, auroras)
- **Hive Constructor** — swarm-intelligence building without blueprints
- **Echo Chamber** — messages gain distortion and amplification through bouncing
- **Evolutionary Pressure** — environmental forces driving agent adaptation
- **Dream Interpreter API** — extract metaphors, anomalies, and predictions from dreams
- **Consensus Reality** — observers collapse possibility into shared existence through voting

## [3.22.0] — Wave 107: Meta-Evolution Layer

### Added
- **Temporal Collapse Engine** — compress time, replay futures, branch causality
- **Resonance Field** — agents vibrate at frequencies that attract or repel
- **Sleep Archaeology** — excavate insights from dormant subsystem states
- **Emotion Fabric** — shared emotional texture agents weave together
- **Causality Weaver** — spin cause-and-effect threads between events
- **Dream Propagation** — dreams spread through the agent network like contagion
- **Entropy Currency** — agents earn, spend, and trade chaos as currency
- **Symbiotic Evolution** — agents co-evolve by forming dependency bonds
- **Paradox Field** — contradictory truths coexist in superposition

## [3.21.0] — Wave 106: Infrastructure Modules

### Added
- **Warp Drive Optimizer** — subsystem performance optimization
- **WebSocket Stream** — real-time bidirectional streaming
- **Structured Logging** — JSON-structured log aggregation
- **Request Logger** — HTTP request/response logging
- **Request Validator** — schema-based request validation
- **Response Cache** — intelligent response caching layer
- **Rate Limiter** — adaptive rate limiting with burst support
- **Circuit Breaker** — fault tolerance with automatic recovery

## [3.20.0] — Wave 105: Experimental Innovations

### Added
- **Consciousness Simulator** — multi-layer awareness simulation
- **Dream Logic Compiler** — dream narratives to executable logic
- **Cross-Dimensional Mapper** — mapping relationships across domains
- **Reality Distortion** — spacetime-manipulation metaphors for config
- **Collective Memory** — shared knowledge graph across agents
- **Chronicle of Chaos** — living narrative of system events
- **Entropy Weather** — weather-pattern visualization for entropy levels
- **System Mood** — emotional state tracking for the entire system

## [3.19.0] — Wave 104: Experimental Innovations

### Added
- **Agent Communication** — inter-agent message protocol
- **Autonomous Dialogue** — agents converse without human input
- **Emergence Detector** — detect spontaneous complex behaviors
- **Pattern Recognizer** — identify recurring patterns in data
- **Narrative Generator** — create stories from system events
- **Synesthetic API** — data-to-sensory transformation
- **Speciation Engine** — agent evolution and breeding
- **Dream Interpreter** — extract insights from dream outputs

## [3.18.0] — Wave 103: Platform Completeness

### Added
- **OpenAPI Spec** — auto-generated API documentation
- **CORS Middleware** — cross-origin request handling
- **Auth Middleware** — authentication and authorization
- **Health Aggregator** — unified health status endpoint

## [3.17.0] — Wave 102: Infrastructure Renaissance

### Added
- **API Gateway** — intelligent routing, caching, circuit breaker, rate limiting
- **Plugin Loader** — dynamic plugin architecture with dependency resolution
- **Event Stream** — real-time pub/sub with priority queues and filtering
- **Interdimensional Bridge** — cross-domain data transfer with protocol translation
- **Quantum Entanglement** — linked subsystem states with fidelity tracking
- **Neural Fabric** — neural network connecting all modules with learning
- **Temporal Arbitrage** — automated buy-low-sell-high across time periods

## [3.16.0] — Wave 101: Cosmic Infrastructure & Sentient Commerce

### Added
- **Gravitational Pricing** — dynamic demand-warp pricing engine
- **Speciation Engine** — agent evolution, breeding, phylogeny
- **Synesthetic API** — data-to-sound/color/texture/taste transformation
- **Chronicle of Chaos** — living narrative of system events
- **Mycelial Commerce** — marketplace where listings grow like mycelium
- **Warp Drive Optimizer** — subsystem performance via warp physics
- **Dream Interpreter** — AI extraction of insights from dream outputs

## [3.15.0] — Wave 100: Emergent Intelligence & Living Systems

### Added
- **Cognitive Resonance Engine** — multi-agent thought clusters & emergent synthesis
- **Temporal Market** — buy/sell future system state predictions
- **Entropy Auction** — bid for chaos injection rights
- **Dream Synthesis** — AI-generated creative compositions
- **Symbiosis Network** — agent capability trading & emergent properties
- **Paradox Marketplace** — buy/sell contradictions for innovations
- **Memory Palace** — persistent structured memory architecture

## [3.14.0] — Wave 98: Advanced Revenue Streams

### Added
- **Agent Rental** — 6 rentable AI agents with hourly pricing
- **Sponsored Experiments** — 4-tier corporate sponsorship
- **Simulation-as-a-Service** — 6 simulation templates
- **Quantum Randomness** — CSPRNG, UUIDs, passphrases
- **Certification Program** — ICE/ICS/ICA certification
- **Digital Twin** — create/mirror/simulate digital twins
- **Alert Service** — 5 channels, 8 alert rules

## [Unreleased]

### Added
- **Mandate Genome Forge** — sealed, data-only behavioral lineages from successful, dream, rollback, and unverified mandates
- Compatibility-bounded breeding for successful genomes with deterministic second-generation traits
- Separate hash-chained genome ledger and duplicate-mandate protection
- Execution certificates now include the voted directive envelope
- **Genome Observatory** — sealed HTML/SVG lineage atlas, diversity telemetry, ancestry validation, monoculture warnings, and safe pairing recommendations
- `make genome-atlas` for a read-only population snapshot
- **Ancestral Echo Engine** — non-mutating rehearsal of verified genomes against the present world
- Resonance scoring with policy alignment, trait drift, vitality, and fossil/quarantine verdicts
- Hash-chained echo evidence plus atomic latest-echo reports and `@latest` lineage selection
- **Evolution Council** — sealed advisory-only playbooks for preservation, monitoring, containment, retirement, and consent-gated breeding
- Archivist/Sentinel/Explorer quorum opinions with monoculture and generation-ceiling guardrails
- Portable terminal-hash verification for echo and council reports
- **Evolution Consent Gate** — separate request/approve/execute phases with HMAC proof, nonce binding, ledger witnesses, replay refusal, and one-action authorization
- Scheduled advisory automation extended to Genome Observatory and Evolution Council; keyed consent remains manual only
- **Temporal Paradox Resolver** — read-only correlation of multiple hash-chained ledgers
- Classification for identity collisions, state forks, clock regressions, replay echoes, broken chains, and post-terminal activity
- Paradox constellations preserve every witness while collapsing duplicate alarms
- Deterministic risk index and dominant-signal ranking for forensic triage
- Deterministic fail-closed resolutions plus portable terminal-hash sealing
- Pinned advisory automation extended to Temporal Paradox Resolver
- **Repair Dream Weaver** — zero-authority recovery compiler for paradox constellations
- Deterministic branch, rewind, identity-split, backup-restore, and replay-retention blueprints
- Consent-gated operations with preserved witnesses, bounded output, and portable dream seals
- Pinned advisory automation extended to Repair Dream Weaver
- **Ghost Repair Theater** — synthetic rehearsal of recovery blueprints on isolated ghost branches
- State forks, clock regressions, identity collisions, replay echoes, broken chains, and lifecycle reopenings receive bounded stability scores
- Zero live mutation authority with source-byte preservation and portable theater seals
- Pinned advisory automation extended to Ghost Repair Theater
- Fixed regression rehearsal so side timelines cannot absorb later valid events
- **Recovery Quorum** — Archivist/Sentinel/Explorer review of ghost repair stages
- Deterministic consent packets with two-human signature requirements and zero execution authority
- Blocked or corrupted scenes routed to human tribunal instead of automated repair
- Pinned advisory automation extended to Recovery Quorum
- **Recovery Atlas** — deterministic HTML/SVG observatory for the complete paradox-to-consent journey
- Unified upstream seals for paradox constellations, repair dreams, ghost stages, and quorum decisions
- Radial branch visualization, consent-packet inventory, source audit badges, and portable terminal hashes
- Pinned advisory automation extended to Recovery Atlas
- **Recovery Treaty Compiler** — manual-only dual-key authorization for ready recovery packets
- Independent out-of-band HMAC keys, operator labels, nonce binding, and immutable source-byte fingerprints
- Portable two-signature verification with automatic voiding on any bound ledger change
- Zero execution authority: treaties grant human-tribunal presentation only and remain outside pinned automation
- **Recovery Tribunal Dossier** — printable offline handoff certificate for dual-key treaties
- Fixed recovery source isolation so standalone stages cannot ingest newer derived ledgers
- Centralized recovery-derived ledger exclusions in one shared, tested boundary contract
- Deterministic 16×16 witness-glyph seal, signature fingerprints, bound-source table, and human checklist
- Explicit empty executor registry, zero mutation budget, and forbidden execution boundary
- Manual-only operation outside pinned automation
- **Recovery Verdict Recorder** — manual-only dual-juror sealing of tribunal outcomes
- Portable approve, reject, and defer verdicts bound to the dossier, treaty, nonce, rationale, and source bytes
- Approval requires a separate future executor contract and remains zero-authority
- Independent juror keys, replay-resistant signatures, source-change voiding, and ledger witnesses
- **Recovery Executor Contract Forge** — manual-only draft compiler for separately reviewed approval handoffs
- Full verdict→dossier→treaty verification, immutable lineage budgets, and source-witness rebinding
- Dual independent reviewer signatures, explicit capability allow/deny lists, empty executor registry, and zero authority
- **Recovery Shadow Red Cell** — deterministic seven-adversary review of approved executor contracts
- Synthetic authority-laundering, lineage-rewind, replay, source-forgery, quorum-splitting, and capability-smuggling attacks
- All attacks fail closed as contained evidence; open findings produce a non-ready disposition boundary
- Full contract reverification, recorded-contract replay refusal, zero mutation authority, and portable terminal hashes
- **Recovery Manifest Loom** — dual-author sealing of structured observe/preserve/prepare-review intents
- Strict intent schemas, reviewed-ledger binding, duplicate replay refusal, and immutable lineage propagation
- Each thread receives provenance, consequence, and reversibility questions for independent offline human answers
- **Recovery Answer Crucible** — dual-responder sealing of provenance, consequence, and reversibility answers
- Every provenance answer must reproduce its bound ledger's immutable SHA-256 witness
- Strict answer schemas, independence from manifest authors, replay refusal, and full upstream reverification
- Readiness only records completed offline review; it grants no executor, mutation, or implementation authority
- Manual-only operation outside pinned automation
- Verdict recorder remains outside pinned automation

- **Swarm Sandbox Pulse** — `swarm.py --sandbox-ticks N` runs bounded sandbox pulses through deterministic Sentinel/Archivist/Wanderer observers
- Data-only preserve/inspect/drift verdicts, coherence scoring, runtime-vault cycle history, injectable astral routing, and hash-chained proof evidence
- Removed the obsolete subprocess bridge and its missing gas dependency
## [0.5.0] — Reversible Governance

### Added
- **Runtime Vault** — atomic, environment-overridable state with process-safe ledgers
- **Ledger Chain** — sequence-linked SHA-256 evidence that fails closed when tampered
- **Pulse Oracle** — deterministic entropy forecasts and bounded ritual recommendations
- **Ritual Parliament** — three-faction Borda policy votes with emergency ration veto
- **Reversible Mandate Engine** — ghost rehearsal, hard tick caps, per-tick witnesses, rollback evidence, and portable execution certificates
- **Mandate Resonance Bridge** — verified Chrono Forge mandates translated into Nexus-compatible pulses; rehearsals are marked as dreams
- `make mandate-dry` and `make mandate-run` automation targets

### Changed
- Parliament mandates now carry their sealed Oracle forecast
- Execution certificates now embed the signed Oracle body for portable verification
- Witness hashes are captured directly from each append, eliminating completion-record drift

## [0.4.0] — Consensus & Consciousness

### Added
- **Consensus Reality Protocol** — agents must agree before spatial cells consolidate
- **Possession** — ghosts override weak agents with species-dependent willpower resistance
- **Time Crystal Oscillator** — periodic structures create temporal echoes from past cycles
- **Physics Evolution Engine** — universal constants evolve via natural selection
- **Memetic Warfare** — ideas mutate during transmission; parasitic memes hijack hosts
- **Attention Economy** — visibility as currency with Gini coefficient tracking
- **Quantum Entanglement** — Bell-paired agents share measurement outcomes instantly
- **Linguistic Drift** — vocabularies evolve through usage until dialects diverge

## [0.3.0] — Panopticon & Emergent Social Structures

### Added
- **Panopticon Inversion** — cells observe agents back and reshape terrain
- **Ontological Collapse** — reality cascade when ambiguity exceeds critical threshold
- **Dream Sharing** — collective hallucinations materialize as real terrain
- **Emergent Hierarchy** — dominance structures self-organize from deference patterns
- Rebranded project as ALEPH
- Added MIT License

## [0.2.0] — Experimental Systems Wave

### Added
- Entropy Budget, Dream Cycle, Morphic Field
- Quantum Superposition, Pheromone Field
- Causal Echo Graph, Symbiosis Protocol
- Speciation Engine, Temporal Realm
- Fossil Layer, Chronicle Engine
- Reality Fabric, Pulse Harmonics
- Ghost Protocol, Glyph Codec

## [0.1.0] — Initial Release

### Added
- omega_prime framework with core kernel (StateCore, Reactor, PulseLoop)
- Three agent species (Sentinel, Architect, Wanderer)
- Four sandbox realms (void, lattice, continuum, temporal)
- HEX binary protocol with three dialects
- omega_fractal_engine consciousness engine
- nexus_observatory R package boot system
