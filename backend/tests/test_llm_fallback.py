import pytest
from unittest.mock import patch, MagicMock
from app.llm.providers.gemini import GeminiProvider


@pytest.fixture
def provider():
    with patch("app.llm.providers.gemini.get_settings") as mock_settings:
        mock_settings.return_value = MagicMock(
            GEMINI_API_KEY="test-key",
            GEMINI_MODEL="gemini-2.5-pro",
            GEMINI_FALLBACK_MODEL="gemini-2.5-flash",
            GEMINI_SECONDARY_FALLBACK_MODEL="gemini-2.5-flash-lite",
            GEMINI_MAX_CONTEXT_CHARS=12000,
            GEMINI_MAX_OUTPUT_TOKENS=1024,
            GEMINI_RATE_LIMIT_COOLDOWN_SECONDS=60,
        )
        yield GeminiProvider()


def test_model_chain_order(provider):
    models = [
        provider.settings.GEMINI_MODEL,
        provider.settings.GEMINI_FALLBACK_MODEL,
        provider.settings.GEMINI_SECONDARY_FALLBACK_MODEL,
    ]
    assert models == ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite"]


def test_is_available(provider):
    assert provider.is_available() is True


def test_is_not_available():
    with patch("app.llm.providers.gemini.get_settings") as mock_settings:
        mock_settings.return_value = MagicMock(GEMINI_API_KEY="")
        p = GeminiProvider()
        assert p.is_available() is False


def test_cooldown_set(provider):
    provider._set_cooldown("gemini-2.5-pro")
    assert provider._is_cooling_down("gemini-2.5-pro") is True
    provider._cooldowns.clear()


def test_cooldown_not_set(provider):
    provider._cooldowns.clear()
    assert provider._is_cooling_down("gemini-2.5-pro") is False


def test_get_status_returns_metadata(provider):
    provider._cooldowns.clear()
    status = provider.get_status()
    assert "provider" in status
    assert status["provider"] == "gemini"
    assert "primary_model" in status
    assert "fallback_model" in status
    assert "secondary_fallback_model" in status
    assert "gemini_configured" in status
    assert "cooldowns" in status


def test_detect_error_type_rate_limit(provider):
    error_type = provider._detect_error_type(Exception("429 Too Many Requests"))
    assert error_type == "rate_limit"


def test_detect_error_type_quota(provider):
    error_type = provider._detect_error_type(Exception("RESOURCE_EXHAUSTED"))
    assert error_type == "quota_exceeded"


def test_detect_error_type_daily_limit(provider):
    error_type = provider._detect_error_type(Exception("daily limit exceeded"))
    assert error_type == "daily_limit"


def test_detect_error_type_invalid_key(provider):
    error_type = provider._detect_error_type(Exception("Invalid API key"))
    assert error_type == "invalid_api_key"


def test_detect_error_type_model_not_found(provider):
    error_type = provider._detect_error_type(Exception("Model not found"))
    assert error_type == "model_not_found"


def test_detect_error_type_network(provider):
    error_type = provider._detect_error_type(Exception("Connection timeout"))
    assert error_type == "network_error"


def test_is_quota_error(provider):
    assert provider._is_quota_error("rate_limit") is True
    assert provider._is_quota_error("quota_exceeded") is True
    assert provider._is_quota_error("daily_limit") is True
    assert provider._is_quota_error("unknown") is False
