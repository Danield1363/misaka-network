# Advanced Web Actions — Misaka v0.3.5

## Overview

Misaka can understand natural language commands and execute real web actions: opening sites, searching YouTube/Google/GitHub/Reddit, and launching apps.

## Supported Sites

| Site | Search | Channel | Video |
|------|--------|---------|-------|
| YouTube | Yes | Yes | Yes |
| Google | Yes | - | - |
| GitHub | Yes | - | - |
| Reddit | Yes | - | - |
| Wikipedia | Yes | - | - |
| Twitch | Yes | - | - |
| Steam | Yes | - | - |
| CurseForge | Yes | - | - |
| Modrinth | Yes | - | - |
| NexusMods | Yes | - | - |

## Command Examples

### YouTube
- "abra o youtube" → Opens YouTube
- "abra o canal do alanzoka no YouTube" → Channel search
- "abra um vídeo do alanzoka de minecraft" → Video search
- "pesquise como instalar mods no YouTube" → Search
- "canal do M4rkim" → Channel search (context: YouTube)

### Google
- "pesquise wake on lan no Google" → Google search
- "pesquise X" → Google search (default)

### GitHub
- "pesquise misaka network no GitHub" → GitHub search

### Reddit
- "pesquise build de minecraft no Reddit" → Reddit search

### Mods/Games
- "procure cobblemon no Modrinth" → Modrinth search
- "procure mods no CurseForge" → CurseForge search
- "procure atm 10 no Nexus" → NexusMods search

## How It Works

1. User types/speaks a command
2. Web Action Engine parses entities (site, query, content type, creator)
3. URL is built from templates with proper encoding
4. Backend returns `client_action` metadata
5. Dashboard/Desktop executes the action

## Adding New Sites

Edit `backend/app/web_actions/url_templates.py`:

```python
NEW_SITE_SEARCH = "https://example.com/search?q={query}"

KNOWN_SITES["example"] = {
    "domains": ["example.com"],
    "templates": {"search": NEW_SITE_SEARCH},
}
```

## Security

- All URLs validated (http/https only)
- Query parameters URL-encoded
- No arbitrary shell execution
- App launcher uses strict allowlist
