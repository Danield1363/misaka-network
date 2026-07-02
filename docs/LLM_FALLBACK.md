# LLM Fallback System

Misaka uses a 3-tier Gemini fallback system to handle quota exhaustion.

## Model Chain

1. **Primary**: `gemini-2.5-pro` — Default model
2. **Fallback**: `gemini-2.5-flash` — Used when Pro hits quota
3. **Secondary**: `gemini-2.5-flash-lite` — Last resort

## How It Works

1. Misaka tries the primary model first
2. If quota/rate limit is hit, it sets a cooldown for that model
3. It automatically retries with the next model in the chain
4. If all models fail, it returns a safe error message

## Error Detection

- 429 / RESOURCE_EXHAUSTED → Quota exceeded
- Daily limit reached → Daily quota
- Invalid API key → Key error
- Model not found → Model error
- Connection/timeout → Network error

## Cooldown

After a quota error, a model is placed in cooldown for 60 seconds (configurable via `GEMINI_RATE_LIMIT_COOLDOWN_SECONDS`).

## Environment Variables

```
GEMINI_MODEL=gemini-2.5-pro
GEMINI_FALLBACK_MODEL=gemini-2.5-flash
GEMINI_SECONDARY_FALLBACK_MODEL=gemini-2.5-flash-lite
GEMINI_MAX_CONTEXT_CHARS=12000
GEMINI_MAX_OUTPUT_TOKENS=1024
GEMINI_RATE_LIMIT_COOLDOWN_SECONDS=60
```

## API Status

`GET /api/llm/status` returns current model status, cooldowns, and error information.

## Dashboard Display

- "Gemini Pro ativo" — Primary model working
- "Usando Gemini Flash temporariamente" — Fallback active
- "Cota diária esgotada" — Daily limit reached
- "API key ausente/inválida" — Key issue
