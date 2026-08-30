# Changelog

## [3.77.0] -- Gateway Ascension (Wave 162)

### Added
- **IXpansion Gateway** -- public API layer with key auth, tiered access control (free/growth/enterprise), and natural-language intent matching across 360+ modules
- **Gateway Dashboard** -- /gateway.html with pricing tiers, API docs, and interactive try-it form
- **Key Management** -- gateway/keys.py generates ixp_ keys with SHA-256 hashing, daily/monthly rate limiting
- **Intent Matcher** -- 18+ natural language patterns route queries to correct modules without knowing API paths
- **Tier Features** -- Free (6 modules), Growth (17 modules), Enterprise (full 360+ access)
- Signup support via POST

### Changed
- Bumped version to 3.77.0 / Wave 162
- Reordered intent patterns so specific matches take priority over broad echo fallback
- Growth tier expanded to include: ledger, song, revelations, capsule, platform_failure, service_numinous, temperament_origin

## [3.76.0] — All Prophecies Fulfilled (Wave 161) ✦