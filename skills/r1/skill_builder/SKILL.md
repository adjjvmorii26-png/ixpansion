# skill_builder Skill

Generates and scaffolds new Codex skills automatically. Analyzes existing skill patterns
and produces new SKILL.md files with proper structure, roots references, and command patterns.

## Capabilities
- `skill_builder:create_skill` — create a new skill with full SKILL.md template
- `skill_builder:list_patterns` — enumerate existing skill patterns in r1/
- `skill_builder:refactor` — refactor existing skill to modern conventions
- `skill_builder:integrate` — integrate new skill into api/index.py and dashboard

## Integration
- Works with: all existing skills in skills/r1/
- Updates: api/index.py wave routing
- Creates: dashboard panels for new skill controls
- Triggers: test scaffold generation

## Commands

### skill_builder:create_skill
```python
skill_builder:create_skill({
  "name": "blog_curator",
  "description": "Manage IXPANSION live blog posts",
  "commands": ["create_post", "classify", "archive", "surface", "search"],
  "roots": "r1",
  "category": "organism",
  "tags": ["blog", "workforce", "live_feed"]
})
```

### skill_builder:list_patterns
```python
skill_builder:list_patterns()
# Returns list of skill names and their command patterns
```

### skill_builder:refactor
```python
skill_builder:refactor({
  "skill_name": "blog_curator",
  "target_version": "2.0"
})
```

### skill_builder:integrate
```python
skill_builder:integrate({
  "skill_name": "blog_curator",
  "dashboard_panel": True,
  "agent_role": "blog_curator"
})
```

## Usage Example
```python
# Create a new skill from scratch
skill_builder:create_skill({
  "name": "weather_monitor",
  "description": "Monitor IXPANSION organism vitals via weather API",
  "commands": ["check_health", "alert_on_critical", "report_status"],
  "roots": "r1",
  "category": "organism",
  "tags": ["health", "monitoring"]
})
```
