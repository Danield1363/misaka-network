import re
from typing import Any
from app.notifications.rules import (
    IGNORED_APPS, IMPORTANT_APPS, CRITICAL_KEYWORDS,
    SENSITIVE_KEYWORDS, IMPORTANT_KEYWORDS
)

CODE_PATTERN = re.compile(r"\b\d{4,6}\b")


class NotificationClassifier:
    def classify(self, notification: dict[str, Any]) -> dict[str, Any]:
        app_name = (notification.get("app_name") or "").lower()
        title = (notification.get("title") or "").lower()
        content = (notification.get("content") or "").lower()
        sender = (notification.get("sender") or "").lower()
        text = f"{title} {content} {sender}"

        is_sensitive = self._check_sensitive(text)
        importance = self._calculate_importance(app_name, text)
        category = self._detect_category(app_name, text)
        should_alert = importance in ("important", "critical")
        summary = self._generate_summary(notification, importance, is_sensitive)

        return {
            "importance": importance,
            "category": category,
            "is_sensitive": is_sensitive,
            "should_alert": should_alert,
            "summary": summary
        }

    def _check_sensitive(self, text: str) -> bool:
        if any(kw in text for kw in SENSITIVE_KEYWORDS):
            return True
        if CODE_PATTERN.search(text):
            return True
        return False

    def _calculate_importance(self, app_name: str, text: str) -> str:
        if any(ignored in app_name for ignored in IGNORED_APPS):
            return "ignored"

        if any(kw in text for kw in CRITICAL_KEYWORDS):
            return "critical"

        if any(important_app in app_name for important_app in IMPORTANT_APPS):
            if any(kw in text for kw in IMPORTANT_KEYWORDS):
                return "important"

        if any(kw in text for kw in IMPORTANT_KEYWORDS):
            return "important"

        return "normal"

    def _detect_category(self, app_name: str, text: str) -> str:
        if any(kw in app_name for kw in ["telefone", "phone", "call", "chamada"]):
            return "call"
        if any(kw in app_name for kw in ["banco", "bank", "finance"]):
            return "finance"
        if any(kw in app_name for kw in ["calendar", "agenda"]):
            return "calendar"
        if any(kw in text for kw in ["código", "senha", "token", "2fa"]):
            return "security"
        return "message"

    def _generate_summary(self, notification: dict[str, Any], importance: str, is_sensitive: bool) -> str:
        app_name = notification.get("app_name", "desconhecido")
        sender = notification.get("sender")
        title = notification.get("title")

        if is_sensitive:
            return f"Código de segurança recebido de {app_name}."

        if importance == "critical":
            return f"Notificação urgente recebida de {sender or app_name}."

        if importance == "important":
            return f"Mensagem importante recebida de {sender or title or app_name}."

        return f"Notificação de {app_name}."