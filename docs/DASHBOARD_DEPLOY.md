# Dashboard Deploy - Cloudflare Pages

## Overview

A Misaka Dashboard é uma interface web estática que pode ser hospedada na Cloudflare Pages e consumir a API do Misaka Core hospedada no Northflank.

## Architecture

```
Cloudflare Pages (dashboard)  →  Northflank (Misaka Core API)
     Static files                    FastAPI + Supabase
```

## Deploy na Cloudflare Pages

### 1. Preparar o repositório

A pasta `dashboard/` contém os arquivos estáticos:
- `index.html`
- `style.css`
- `config.js`
- `app.js`

### 2. Criar projeto no Cloudflare

1. Acesse [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Vá para **Workers & Pages**
3. Clique em **Create** → **Pages**
4. Conecte ao repositório GitHub
5. Configure:
   - **Production branch:** `main`
   - **Build command:** (vazio - arquivos estáticos)
   - **Build output directory:** `/dashboard`

### 3. Configurar a URL da API

**IMPORTANTE:** Cloudflare Pages **NÃO injeta variáveis de ambiente** em sites estáticos sem build step. A URL da API deve estar hardcoded em `config.js`.

Para atualizar a URL da API:

1. Edite `dashboard/config.js`
2. Atualize `API_BASE_URL` com a URL do seu backend
3. Faça commit e push

```javascript
const MISAKA_CONFIG = {
    API_BASE_URL: window.location.hostname === 'localhost'
        ? 'http://127.0.0.1:8000/api'
        : 'https://p01--misaka-network--nf5wq7twf8xg.code.run/api'
};
```

### 4. Deploy automático

Cada push para `main` atualiza o site automaticamente.

## Configuração da API

### config.js

```javascript
const MISAKA_CONFIG = {
    API_BASE_URL: window.location.hostname === 'localhost'
        ? 'http://127.0.0.1:8000/api'
        : 'https://p01--misaka-network--nf5wq7twf8xg.code.run/api',
    APP_NAME: 'Misaka Dashboard',
    VERSION: '0.1 Genesis'
};
```

## CORS

O Misaka Core aceita:
- `https://*.pages.dev`
- `https://*.code.run`
- `https://*.northflank.app`
- `http://localhost:*`

## URLs

| Ambiente | Dashboard | API |
|----------|-----------|-----|
| Local | http://localhost:3000 | http://localhost:8000 |
| Produção | https://misaka.pages.dev | https://p01--misaka-network--*.code.run |

## Endpoints consumidos

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/status` | GET | Status do sistema |
| `/api/chat` | POST | Enviar mensagem |
| `/api/persona` | GET | Perfil da Misaka |
| `/api/ui-config` | GET | Config visual |

## Segurança

- **NUNCA** coloque chaves de API no frontend
- **NUNCA** commite `.env` ou chaves secretas
- O backend (Northflank) deve ter as chaves secretas
- A dashboard apenas lê dados públicos

## Troubleshooting

### CORS errors

1. Verifique se a URL do dashboard está no CORS do backend
2. Verifique se a API está rodando

### API não responde

1. Verifique se o Misaka Core está online no Northflank
2. Teste o endpoint `/api/health` diretamente

### Variáveis não atualizam

1. Faça rebuild no Cloudflare Pages
2. Verifique o cache do navegador
3. Lembre: variáveis de ambiente do Cloudflare não funcionam para sites estáticos