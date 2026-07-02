# Deploy Guide - Misaka Core

## Local Development

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

API available at: http://127.0.0.1:8000
Docs: http://127.0.0.1:8000/docs

## Docker

```bash
cd backend
docker build -t misaka-core .
docker run -p 8000:8000 misaka-core
```

## Northflank Deployment

### Configuration

- **Build context:** `/backend`
- **Dockerfile location:** `/Dockerfile`
- **Port:** `8000`

### Environment Variables

Set these in Northflank:

```
ENVIRONMENT=production
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-api-key
GEMINI_MODEL=gemini-2.5-pro
MEMORY_ENABLED=false
LOG_LEVEL=INFO
```

### Important Notes

- **Never commit .env files** to the repository
- **Never log secrets** (API keys, service role keys)
- **MEMORY_ENABLED=false** by default (no Supabase required)
- **LLM_PROVIDER=mock** for development, **gemini** for production

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root endpoint |
| `/api/health` | GET | Health check |
| `/api/status` | GET | System status |
| `/api/chat` | POST | Chat with Misaka |
| `/docs` | GET | Swagger UI |

## Troubleshooting

### Gemini not working

1. Verify `LLM_PROVIDER=gemini`
2. Verify `GEMINI_API_KEY` is set
3. Check logs for errors

### Memory/Calendar disabled

Set `MEMORY_ENABLED=true` and configure Supabase:
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`