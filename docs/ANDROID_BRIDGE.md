# Android Notification Bridge - Configuration

## Overview

Este guia explica como configurar o Android para enviar notificações para a Misaka Core.

## Requisitos

- Android 8.0+ (API 26+)
- App com `NotificationListenerService`
- Permissão `BIND_NOTIFICATION_LISTENER_SERVICE`

## Configuração da API

### 1. Obter o Token

O token de ingestão está configurado no backend:

```
NOTIFICATION_INGEST_TOKEN=your-secret-token-here
```

### 2. Headers da Requisição

Toda requisição deve incluir:

```
Content-Type: application/json
X-Misaka-Token: <your-token>
```

### 3. Endpoint

```
POST https://p01--misaka-network--nf5wq7twf8xg.code.run/api/notifications/ingest
```

## Formato da Notificação

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

## Campos

| Campo | Obrigatório | Descrição |
|-------|-------------|-----------|
| `app_name` | Sim | Nome do app que gerou a notificação |
| `package_name` | Não | Package name do app Android |
| `title` | Não | Título da notificação |
| `content` | Não | Conteúdo da notificação |
| `sender` | Não | Remetente (se aplicável) |
| `channel` | Não | Canal da notificação |
| `received_at` | Sim | Timestamp ISO 8601 |
| `device_id` | Não | Identificador do dispositivo |
| `metadata` | Não | Dados extras |

## Exemplos de Uso

### cURL

```bash
curl -X POST https://p01--misaka-network--nf5wq7twf8xg.code.run/api/notifications/ingest \
  -H "Content-Type: application/json" \
  -H "X-Misaka-Token: your-token" \
  -d '{
    "app_name": "WhatsApp",
    "title": "João",
    "content": "Oi, tudo bem?",
    "received_at": "2026-07-03T10:30:00Z",
    "device_id": "android-001"
  }'
```

### Android (Kotlin)

```kotlin
class MisakaNotificationListener : NotificationListenerService() {

    override fun onNotificationPosted(sbn: StatusBarNotification) {
        val notification = sbn.notification
        val extras = notification.extras

        val data = mapOf(
            "app_name" to sbn.packageName,
            "package_name" to sbn.packageName,
            "title" to extras.getString(Notification.EXTRA_TITLE),
            "content" to extras.getString(Notification.EXTRA_TEXT),
            "received_at" to Instant.now().toString(),
            "device_id" to getDeviceId()
        )

        sendToMisaka(data)
    }

    private fun sendToMisaka(data: Map<String, Any>) {
        Thread {
            val client = OkHttpClient()
            val json = JSONObject(data).toString()
            val body = json.toRequestBody("application/json".toMediaType())

            val request = Request.Builder()
                .url("https://p01--misaka-network--nf5wq7twf8xg.code.run/api/notifications/ingest")
                .addHeader("X-Misaka-Token", "your-token")
                .post(body)
                .build()

            client.newCall(request).execute()
        }.start()
    }
}
```

## Rate Limiting

- Máximo: 100 notificações por minuto por device
- Se exceder: erro 429 com `retry_after`

## Deduplicação

- Notificações duplicadas (mesmo package_name + title + content) são descartadas
- Janela: 5 minutos

## Status da Bridge

```bash
curl https://p01--misaka-network--nf5wq7twf8xg.code.run/api/notifications/bridge/status
```

Response:
```json
{
  "bridge_status": "online",
  "connected_devices": 1,
  "last_notification": "2026-07-03T10:30:00Z",
  "notifications_today": 42
}
```

## Segurança

- **NUNCA** exponha o token em código fonte
- Use variáveis de ambiente ou secure storage
- O token deve ter pelo menos 32 caracteres
- Rotate o token periodicamente