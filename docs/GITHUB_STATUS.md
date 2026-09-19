# GitHub Status · 2026-09-18

## Main
| Item | State |
|------|--------|
| **HEAD** | Stable terminal (#138) + co-pilots (#137) on main |
| **Council** | `make council` · AEGIS · HELIX · QUILL |
| **Shell** | `make shell` · `source scripts/ix_shell.sh` |

## Open PRs (priority)
1. **#135** — CI pulse summary / chaos timeout fixes (scheduled red noise)
2. **Tooling PR** — local dashboard + Codespaces + status snapshot + live council pulse
3. **#136** — wave768 hush_compass (lab organ)
4. **#134** — VS Code + Copilot pack

## Local commands
```bash
git pull origin main
make shell
ix-council
ix-snapshot
ix-dashboard   # http://127.0.0.1:8765/
```

## Heartbeat
- `docs/LAB_HEARTBEAT.json` — updated by QUILL
- `docs/LAB_STATUS.json` / `docs/LAB_STATUS.md` — `make snapshot`
- Workflow: **Lab Council Pulse** (path-filtered + daily cron)

Caption: `status · council · shell · dashboard`
