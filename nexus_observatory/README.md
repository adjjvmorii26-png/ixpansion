# Nexus Observatory

The original R/Bash boot system remains available through `./nexus_boot.sh`.
A zero-dependency Python/NPM layer now provides repeatable observatory rituals.

## Commands
```bash
npm run health                 # validate files, journal, latest resonance, telemetry
npm run quiet                  # cycle + journal + index
npm run watch -- 3 5000        # three cycles, five seconds apart
npm run index                  # rebuild JSON + Markdown report table
npm run journal                # show recent pulses
npm run dashboard              # render and save the ASCII dashboard
npm run compare                # compare the two newest pulses
npm run creative               # execute all Project Wave 9 experiments
npm run reliquary              # seal bus events into a hash-chain relic
npm run ci                     # health → cycle → index → relic → dashboard
```

Telemetry is generated under `telemetry/` and is intentionally not committed.
