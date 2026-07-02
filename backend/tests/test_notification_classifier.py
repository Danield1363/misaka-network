import pytest
from app.notifications.classifier import NotificationClassifier


@pytest.fixture
def classifier():
    yield NotificationClassifier()


def test_normal_notification(classifier):
    result = classifier.classify({"app_name": "Gmail", "title": "Newsletter", "content": "Novidades da semana"})
    assert result["importance"] == "normal"
    assert result["should_alert"] is False


def test_urgent_notification(classifier):
    result = classifier.classify({"app_name": "WhatsApp", "title": "João", "content": "Urgente me responde"})
    assert result["importance"] == "critical"
    assert result["should_alert"] is True


def test_sensitive_notification(classifier):
    result = classifier.classify({"app_name": "SMS", "title": "Seu código é 123456", "content": "Use para verificar"})
    assert result["is_sensitive"] is True
    assert "123456" not in result["summary"]


def test_ignored_app(classifier):
    result = classifier.classify({"app_name": "Game Store", "title": "Promoção", "content": "50% off"})
    assert result["importance"] == "ignored"
    assert result["should_alert"] is False


def test_important_whatsapp(classifier):
    result = classifier.classify({"app_name": "WhatsApp", "title": "Mãe", "content": "Você tem um prazo amanhã"})
    assert result["importance"] == "important"
    assert result["should_alert"] is True


def test_discord_mention(classifier):
    result = classifier.classify({"app_name": "Discord", "title": "Menção", "content": "@you urgente"})
    assert result["should_alert"] is True


def test_summary_no_code(classifier):
    result = classifier.classify({"app_name": "SMS", "title": "Código 654321", "content": "verificação"})
    assert "654321" not in result["summary"]
    assert "segurança" in result["summary"].lower()


def test_category_detection(classifier):
    result = classifier.classify({"app_name": "Telefone", "title": "Chamada perdida", "content": ""})
    assert result["category"] == "call"


def test_finance_category(classifier):
    result = classifier.classify({"app_name": "Banco do Brasil", "title": "Transferência", "content": "R$ 100"})
    assert result["category"] == "finance"