# blog_curator Skill

Manages IXPANSION live blog posts.

## Capabilities
- `blog_curator:create_post` — create new posts with type/title/content/tags
- `blog_curator:classify` — auto-classify post types
- `blog_curator:archive` — archive historical posts
- `blog_curator:surface` — surface recent posts
- `blog_curator:search` — search posts

## Roots
- `r1` = `/root/.shared-skills/.system`

## Commands

### blog_curator:create_post
```python
blog_curator:create_post({
  "type": "wave_announcement",
  "title": "Wave 735 Launched",
  "content": "Organism evolved into new era.",
  "tags": ["wave", "announcement", "735"]
})
```

### blog_curator:classify
```python
blog_curator:classify({
  "content": "...",
  "title": "..."
})
```

### blog_curator:archive
```python
blog_curator:archive({
  "post_id": "..."
})
```

### blog_curator:surface
```python
blog_curator:surface({
  "limit": 10,
  "types": ["wave_announcement", "agent_dispatch"]
})
```

### blog_curator:search
```python
blog_curator:search({
  "query": "Wave 735",
  "tags": ["wave"]
})
```
