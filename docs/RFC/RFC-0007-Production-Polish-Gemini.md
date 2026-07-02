# RFC-0007 — Production Polish + Gemini Online

Status: Proposed  
Version: 0.1 Genesis  
Owner: Daniel  
Architect: ChatGPT  
Developer Agent: Mimo v2.5  
Target: Misaka Core  

---

## 1. Objetivo

Preparar a Misaka Core para uso online no Northflank.

Esta RFC deve melhorar a experiência da API em produção, adicionar uma rota raiz, melhorar healthcheck, garantir funcionamento correto do Gemini 2.5 Pro e deixar o sistema pronto para próximas integrações.

---

## 2. Escopo

Implementar:

- Rota GET `/`
- Healthcheck melhorado
- Endpoint `/api/status`
- Ajustes de configuração para produção
- Validação de variáveis de ambiente
- Melhor tratamento de erro do LLM Gateway
- Logs seguros
- Teste real com `LLM_PROVIDER=mock`
- Suporte correto a `GEMINI_MODEL=gemini-2.5-pro`
- Atualização da documentação de deploy
- Correção do Action Log duplicado da RFC-0006

---

## 3. Fora do escopo

Não implementar ainda:

- Google Calendar real
- Voz
- Android
- Desktop
- Minecraft
- Dashboard
- Autenticação
- Webhooks externos

---

## 4. Rota raiz

Criar rota:

```text
GET /

Resposta esperada:

{
  "assistant": "Misaka",
  "status": "online",
  "version": "0.1 Genesis",
  "docs": "/docs",
  "health": "/api/health",
  "status_url": "/api/status"
}
5. Healthcheck

Manter:

GET /api/health

Resposta:

{
  "status": "ok",
  "assistant": "Misaka",
  "version": "0.1 Genesis"
}

Esse endpoint deve ser simples e rápido.

Não deve chamar Gemini, Supabase ou serviços externos.

6. Status completo

Criar:

GET /api/status

Resposta esperada:

{
  "assistant": "Misaka",
  "version": "0.1 Genesis",
  "environment": "production",
  "llm_provider": "mock",
  "llm_model": "gemini-2.5-pro",
  "memory_enabled": false,
  "calendar_enabled": false,
  "tools_enabled": true,
  "status": "online"
}

Nunca retornar secrets.

Não retornar:

GEMINI_API_KEY
SUPABASE_SERVICE_ROLE_KEY
tokens
senhas
7. Gemini

Garantir que o .env.example tenha:

APP_NAME=Misaka Core
APP_VERSION=0.1 Genesis
ENVIRONMENT=development

LLM_PROVIDER=mock
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-pro

SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
MEMORY_ENABLED=false

Em produção, o Northflank usará:

ENVIRONMENT=production
LLM_PROVIDER=gemini
GEMINI_MODEL=gemini-2.5-pro
GEMINI_API_KEY=<secret>
MEMORY_ENABLED=false
8. LLM Gateway

Melhorar tratamento de erro:

Se LLM_PROVIDER=gemini e GEMINI_API_KEY não existir, retornar erro claro no /api/chat, mas sem derrubar a aplicação.

Exemplo:

{
  "response": "O provedor Gemini está configurado, mas a chave de API não foi encontrada.",
  "agent": "conversation",
  "model": "gemini-2.5-pro",
  "metadata": {
    "llm_error": true,
    "provider": "gemini"
  }
}
9. Action Log hotfix

Corrigir o problema da RFC-0006:

Atualmente, o ActionEngine pode criar um action_log no início e outro no sucesso/erro.

Queremos apenas um registro por execução.

Tarefas:

log_action_start() deve retornar o action_id.
log_action_success(action_id, output, metadata=None) deve atualizar o mesmo registro.
log_action_error(action_id, error, metadata=None) deve atualizar o mesmo registro.
Se Supabase estiver desativado, manter fallback silencioso.
Atualizar ToolExecutor para usar o mesmo action_id.
10. Docker/Northflank

Confirmar que existe:

backend/Dockerfile
backend/requirements.txt

Dockerfile esperado:

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
11. Documentação

Criar ou atualizar:

docs/DEPLOY.md

Incluir:

Como rodar localmente
Como subir no Northflank
Build context correto: /backend
Dockerfile location: /Dockerfile
Porta: 8000
Variáveis obrigatórias
Aviso para nunca commitar .env
12. Testes obrigatórios

Criar ou atualizar testes:

/ retorna 200
/api/health retorna 200
/api/status retorna 200
/api/status não mostra secrets
/api/chat funciona com LLM_PROVIDER=mock
Gemini sem API key retorna erro controlado
Action Log não duplica registros
Todos os testes anteriores continuam passando
13. Critérios de aceitação

A RFC será aprovada quando:

/ funcionar no navegador
/api/health funcionar
/api/status funcionar
/docs continuar funcionando
/api/chat funcionar online
Gemini 2.5 Pro estiver configurável
Secrets não aparecerem em respostas
Action Log duplicado for corrigido
Docker continuar funcionando
Testes passarem
14. Comandos esperados

Rodar testes:

pytest

Rodar local:

uvicorn main:app --reload

Testar local:

GET /
GET /api/health
GET /api/status
POST /api/chat