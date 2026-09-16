"""Wave 733 — Skill Builder.

Automatically generates and scaffolds new Codex skills.
"""
import json, hashlib
from pathlib import Path
from typing import Any, Dict
import datetime

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "wave733_skill_builder.json"
WAVE = 733
NAME = "skill_builder"

def _load() -> dict:
    return json.loads(DATA_FILE.read_text()) if DATA_FILE.exists() else {"wave": WAVE, "name": NAME, "skills_catalog": {}, "generated": []}

def _save(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2))

def handler(req: dict) -> dict:
    action = req.get("action", "status")
    state = _load()

    if action == "create_skill":
        spec = req.get("spec", {})
        skill_name = spec.get("name", "")
        description = spec.get("description", "")
        commands = spec.get("commands", [])
        roots = spec.get("roots", "r1")
        category = spec.get("category", "organism")
        tags = spec.get("tags", [])

        skill_id = hashlib.md5(f"{skill_name}{datetime.datetime.now(datetime.UTC).isoformat()}".encode()).hexdigest()[:8]
        skill_entry = {
            "id": skill_id,
            "name": skill_name,
            "description": description,
            "commands": commands,
            "roots": roots,
            "category": category,
            "tags": tags,
            "wave": WAVE,
            "created_at": datetime.datetime.now(datetime.UTC).isoformat(),
            "status": "generated"
        }

        state["generated"].append(skill_entry)
        state["skills_catalog"][skill_name] = skill_entry
        _save(state)

        # Auto-generate SKILL.md file (YAML-frontmatter, install-compliant)
        skill_md = f'''---
name: {skill_name}
description: {description}
---

# {skill_name} Skill

## Description
{description}

## Capabilities
'''
        for cmd in commands:
            skill_md += f"- `{cmd}` — perform {cmd} action\n"

        skill_md += f'''
## Integration
- Roots: `{roots}`
- Category: {category}
- Tags: {", ".join(tags) if tags else "none"}

## Commands
'''
        for cmd in commands:
            skill_md += f'''### {cmd}
'''

        skill_md += f'''
## Roots
- `r1` = `/root/.shared-skills/.system`
'''

        # Write to skills directory
        skill_dir = Path(f"skills/r1/{skill_name.replace(' ', '_')}")
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(skill_md)

        return {"wave": WAVE, "action": "create_skill", "skill": skill_entry, "skill_md_path": f"skills/r1/{skill_name.replace(' ', '_')}/SKILL.md"}

    elif action == "list_patterns":
        return {"wave": WAVE, "skills_catalog": state["skills_catalog"]}

    elif action == "status":
        return {"wave": WAVE, "generated": len(state["generated"]), "status": "active"}

    return {"wave": WAVE, "action": action, "status": "ok"}

def coherence_vitals() -> dict:
    state = _load()
    return {"wave": WAVE, "name": NAME, "generated": len(state["generated"]), "status": "active"}

def resonates_with() -> list:
    return [720, 730, 731, 732]

if __name__ == "__main__":
    # Demo: create a test skill
    r = handler({"action": "create_skill", "spec": {
        "name": "weather_monitor",
        "description": "Monitor organism vitals via weather API",
        "commands": ["check_health", "alert_on_critical", "report_status"],
        "roots": "r1",
        "category": "health",
        "tags": ["health", "monitoring"]
    }})
    print(json.dumps(r, indent=2)[:600])
