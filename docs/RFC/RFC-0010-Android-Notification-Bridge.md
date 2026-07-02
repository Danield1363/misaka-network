# RFC-0010 — Android Notification Bridge

Status: Proposed  
Version: 0.1 Genesis  
Owner: Daniel  
Architect: ChatGPT  
Developer Agent: Mimo v2.5  
Target: Misaka Core + Misaka Mobile  

---

## 1. Objetivo

Criar a ponte entre o Android e a Misaka Core para receber notificações reais do dispositivo.

A Misaka deve ser capaz de:
- Receber notificações do Android via API
- Classificar e filtrar notificações automaticamente
- Alertar Daniel apenas sobre notificações importantes
- Futuramente responder ou interagir com notificações

---

## 2. Escopo

Implementar:

- Android Notification Listener Service
- Notification Bridge API
- Notification Queue persistente
- Notification Deduplication
- Notification Rate Limiting
- Notification History
- Dashboard de notificações
- Testes

---

## 3. Fora do escopo

Não implementar ainda:

- Resposta automática a notificações
- Ação em notificações (marcar como lida, etc)
- Leitura de tela
- Controle total do Android
- Voz
- Automações avançadas
- Integração com Tasker/Automate

---

## 4. Arquitetura

Fluxo esperado:

```text
Android Notification Listener
  ↓
POST /api/notifications/ingest
  ↓
NotificationBridge
  ↓
Notification Deduplication
  ↓
Notification Rate Limiter
  ↓
Notification Queue
  ↓
NotificationEngine (RFC-0009)
  ↓
NotificationClassifier
  ↓
Important Alert Queue
```

---

## 5. Android Notification Listener

### Service

O app Android deve rodar um `NotificationListenerService` que:

1. Captura todas as notificações recebidas
2. Extrai: app_name, package_name, title, content, sender, timestamp
3. Envia para a Misaka Core via API

### Permissões necessárias

- `BIND_NOTIFICATION_LISTENER_SERVICE`
- `READ_EXTERNAL_STORAGE` (opcional)

### Formato de envio

```json
{
  "app_name": "WhatsApp",
  "package_name": "com.whatsapp",
  "title": "João",
  "content": "Oi, tudo bem?",
  "sender": "João",
  "channel": "messages",
  "received_at": "2026-07-03T10:30:00Z",
  "device_id": "android-001",
  "metadata": {
    "android_version": "14",
    "app_version": "2.24.13.78"
  }
}
```

---

## 6. Notification Bridge

### Responsabilidades

- Receber notificações do Android
- Validar dados
- Deduplicar notificações repetidas
- Aplicar rate limiting
- Encaminhar para NotificationEngine

### Deduplication

Notificações são deduplicadas por:
- `package_name` + `title` + `content` (hash)
- Janela de 5 minutos

Se a mesma notificação chegar novamente dentro de 5 minutos, é descartada.

### Rate Limiting

- Máximo 100 notificações por minuto por device
- Se exceder, retornar erro 429

---

## 7. Notification Queue

### Fila persistente

Notificações devem ser salvas em:

```sql
CREATE TABLE notification_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id TEXT NOT NULL,
    app_name TEXT NOT NULL,
    package_name TEXT,
    title TEXT,
    content TEXT,
    sender TEXT,
    channel TEXT,
    received_at TIMESTAMPTZ NOT NULL,
    processed_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'pending',
    hash TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_notification_queue_hash ON notification_queue(hash);
CREATE INDEX idx_notification_queue_status ON notification_queue(status);
CREATE INDEX idx_notification_queue_device ON notification_queue(device_id);
```

---

## 8. API Bridge

### POST /api/notifications/bridge

Recebe notificação do Android e processa.

**Request:**
```json
{
  "app_name": "WhatsApp",
  "package_name": "com.whatsapp",
  "title": "João",
  "content": "Oi, tudo bem?",
  "sender": "João",
  "channel": "messages",
  "received_at": "2026-07-03T10:30:00Z",
  "device_id": "android-001"
}
```

**Response (200):**
```json
{
  "status": "received",
  "notification_id": "uuid",
  "duplicate": false
}
```

**Response (429):**
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 60
}
```

### GET /api/notifications/bridge/status

Status da ponte.

**Response:**
```json
{
  "bridge_status": "online",
  "connected_devices": 1,
  "last_notification": "2026-07-03T10:30:00Z",
  "notifications_today": 42
}
```

### GET /api/notifications/bridge/history

Histórico de notificações.

**Query:** `?device_id=android-001&limit=50`

**Response:**
```json
{
  "notifications": [...],
  "total": 42
}
```

---

## 9. Device Management

### Registrar device

POST /api/notifications/bridge/devices

```json
{
  "device_id": "android-001",
  "device_name": "Pixel 8 Pro",
  "android_version": "14"
}
```

### Listar devices

GET /api/notifications/bridge/devices

```json
{
  "devices": [
    {
      "device_id": "android-001",
      "device_name": "Pixel 8 Pro",
      "last_seen": "2026-07-03T10:30:00Z",
      "status": "online"
    }
  ]
}
```

---

## 10. Dashboard de Notificações

Adicionar à dashboard uma seção de notificações:

- Lista de notificações recebidas
- Filtro por app, importância, status
- Alertas importantes destacados
- Estatísticas do dia

---

## 11. Segurança

### API Key

O Android deve enviar uma API key válida:

```
Authorization: Bearer <api-key>
```

### Rate Limiting

- 100 req/min por device
- 1000 req/hora por device

### Validação

- Validar `app_name` não vazio
- Validar `received_at` válido
- Validar `device_id` registrado

---

## 12. SQL

```sql
CREATE TABLE IF NOT EXISTS notification_bridge_devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id TEXT UNIQUE NOT NULL,
    device_name TEXT,
    android_version TEXT,
    api_key_hash TEXT,
    last_seen TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'online',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS notification_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id TEXT NOT NULL,
    app_name TEXT NOT NULL,
    package_name TEXT,
    title TEXT,
    content TEXT,
    sender TEXT,
    channel TEXT,
    received_at TIMESTAMPTZ NOT NULL,
    processed_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'pending',
    hash TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_notification_queue_hash ON notification_queue(hash);
CREATE INDEX idx_notification_queue_status ON notification_queue(status);
CREATE INDEX idx_notification_bridge_devices_device_id ON notification_bridge_devices(device_id);
```

---

## 13. Testes

- Bridge recebe notificação válida
- Bridge rejeita rate limit
- Deduplication funciona
- Notificação duplicada é descartada
- Histórico retorna notificações
- Device é registrado
- Status da bridge retorna dados
- API key é validada
- Dashboard carrega notificações

---

## 14. Critérios de aceitação

- Android Notification Listener existe (documentação)
- Bridge API funciona
- Deduplication funciona
- Rate limiting funciona
- Queue persistente existe
- Device management funciona
- Dashboard mostra notificações
- Testes passam
- /api/chat continua funcionando
- Segurança implementada

---

## 15. Próximos passos

Após esta RFC:

1. Criar app Android com NotificationListenerService
2. Implementar envio automático de notificações
3. Adicionar respostas automáticas (futuro)
4. Integração com Tasker/Automate