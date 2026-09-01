# IXpansion Toolkit

A Codex plugin + skill bundle for building waves of living organs in the
IXpansion organism.

## Contents

- **skill: ixpansion-wave-builder** — canonical conventions for building a
  new wave: the 14-step checklist (`references/checklist.md`), organ
  scaffolder, and version bumper.
- **scripts/broadcast/** — Telegram broadcast helpers (`send_organism_update.py`
  and `auto_telegram.py`) that push organism lifecycle events to a bot.

## Usage

Install from the personal marketplace:

```bash
codex plugin marketplace add https://example.com  # after hosting
codex plugin install ixpansion-toolkit
```

Or use locally:

```bash
# Scaffold a new organ
python3 skills/ixpansion-wave-builder/scripts/scaffold_organ.py my_organ --wave 215

# Bump version/wave across canonical files
python3 skills/ixpansion-wave-builder/scripts/bump_wave.py --version 4.03.0 --wave 215 --name "The Organism Teaches"

# Send / auto-complete Telegram broadcast
python3 scripts/broadcast/send_organism_update.py --event wave_birth --wave 215
```

## Install location (this machine)

- Plugin root: `~/.agents/plugins/marketplace.json` + `~/plugins/ixpansion-toolkit`
- Repo mirror: `codetools/plugins/ixpansion-toolkit`
