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

### 3. Configurar variáveis de ambiente

No painel do Cloudflare Pages, adicione:

```
MISAKA_API_BASE_URL = https://misaka-core.seu-dominio.com/api
```

**IMPORTANTE:** A `config.js` já tem fallback para localhost em desenvolvimento.

### 4. Deploy automático

Cada push para `main` atualiza o site automaticamente.

## Configuração da API

### config.js

```javascript
const MISAKA_CONFIG = {
    API_BASE_URL: window.location.hostname === 'localhost'
        ? 'http://127.0.0.1:8000/api'
        : 'https://seu-app.northflank.app/api'
};
```

### Para produção

Edite `config.js` ou use variável de ambiente:

```javascript
const MISAKA_CONFIG = {
    API_BASE_URL: 'https://misaka-core.seu-dominio.com/api'
};
```

## CORS

O Misaka Core já está configurado para aceitar:
- `https://*.pages.dev`
- `https://*.northflank.app`
- `http://localhost:*`

## URLs esperadas

| Ambiente | Dashboard | API |
|----------|-----------|-----|
| Local | http://localhost:3000 | http://localhost:8000 |
| Produção | https://misaka.pages.dev | https://misaka-core.northflank.app |

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
- Use variáveis de ambiente no Cloudflare
- O backend (Northflank) deve ter as chaves secretas

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