# Skill Systems Foundry

Offline prototype for five experimental quality engines:
1. dependency graph and missing-edge/cycle detection;
2. deterministic instruction-fuzz case generation;
3. proposal-only self-healing patch plans;
4. static Gem/portable compatibility lint;
5. SHA-256 drift checks for pinned seed/export snapshots.

## Run

```bash
python -m unittest discover -s tests -v
python scripts/skill_lab.py scan --root skills
python scripts/skill_lab.py graph --root skills
python scripts/skill_lab.py fuzz --file skills/example/SKILL.md --seed 1337 --count 24
python scripts/skill_lab.py compat --file skills/example/SKILL.md --profile gem
python scripts/skill_lab.py drift --export-dir skills/example
```

The fuzz command generates test cases; it does not execute a skill or call external tools. The repair-plan command proposes changes only. Drift checks compare local snapshots, not live Notion content. Refresh the seed snapshot only after fetching the canonical Notion page and reviewing the diff. Compatibility is static lint, not proof of runtime integration.

No network calls, secrets, automatic file rewrites, destructive actions, activation, merge, or deployment.
