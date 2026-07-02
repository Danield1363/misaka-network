from typing import Any

IGNORED_APPS = ["jogos", "loja", "promoção", "shopping", "ads", "recompensa diária", "game", "store"]

IMPORTANT_APPS = ["whatsapp", "discord", "gmail", "google calendar", "telefone", "mensagens", "banco", "bank"]

CRITICAL_KEYWORDS = ["urgente", "emergência", "socorro", "agora", "me liga", "responde", "caiu", "erro crítico", "urgent", "emergency"]

SENSITIVE_KEYWORDS = ["código", "senha", "token", "2fa", "verificação", "autenticação", "code", "password"]

IMPORTANT_KEYWORDS = ["importante", "prazo", "pagamento", "banco", "faculdade", "trabalho", "entrevista", "reunião", "me responde", "servidor caiu"]


def get_importance_rules() -> dict[str, Any]:
    return {
        "ignored_apps": IGNORED_APPS,
        "important_apps": IMPORTANT_APPS,
        "critical_keywords": CRITICAL_KEYWORDS,
        "sensitive_keywords": SENSITIVE_KEYWORDS,
        "important_keywords": IMPORTANT_KEYWORDS
    }