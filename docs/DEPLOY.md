# Deployment Guide — Misaka v0.3

## Backend (Northflank / Docker)

### Local Development
```bash
cd backend
cp .env.example .env
# Edit .env with your keys
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Docker
```bash
cd backend
docker build -t misaka-backend .
docker run -p 8000:8000 --env-file .env misaka-backend
```

### Northflank
1. Connect GitHub repository
2. Set buildpack to Python
3. Add environment variables in Northflank dashboard
4. Deploy

## Dashboard (Cloudflare Pages)

### Local
```bash
cd dashboard
python -m http.server 3000
```

### Cloudflare Pages
1. Connect GitHub repository
2. Build command: (none — static files)
3. Output directory: `dashboard`
4. Deploy

## Desktop App

### Development
```bash
cd desktop
npm install
npm start
```

### Build .exe
```bash
cd desktop
npm install
npm run dist
# Output: desktop/dist/
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | For Gemini | Gemini API key |
| `SUPABASE_URL` | For DB features | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | For DB features | Supabase service key |
| `NOTIFICATION_INGEST_TOKEN` | For bridge | Bridge auth token |
| `MISAKA_API_BASE_URL` | Desktop only | Backend API URL |
| `MISAKA_DASHBOARD_URL` | Desktop only | Dashboard URL |

## CORS Configuration

Backend allows requests from:
- `http://localhost:3000`
- `http://localhost:8000`
- `https://*.pages.dev`
- `https://*.code.run`
- `https://*.northflank.app`
