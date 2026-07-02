import pytest
from unittest.mock import patch
from app.bridge.rate_limit import RateLimiter, Deduplicator
from app.bridge.engine import NotificationBridge


def test_rate_limiter_allows():
    limiter = RateLimiter(max_requests=5, window_seconds=60)
    assert limiter.is_allowed("device-1") is True


def test_rate_limiter_blocks():
    limiter = RateLimiter(max_requests=2, window_seconds=60)
    limiter.is_allowed("device-1")
    limiter.is_allowed("device-1")
    assert limiter.is_allowed("device-1") is False


def test_rate_limiter_different_devices():
    limiter = RateLimiter(max_requests=1, window_seconds=60)
    limiter.is_allowed("device-1")
    assert limiter.is_allowed("device-2") is True


def test_rate_limiter_retry_after():
    limiter = RateLimiter(max_requests=1, window_seconds=60)
    limiter.is_allowed("device-1")
    retry = limiter.get_retry_after("device-1")
    assert retry > 0


def test_deduplicator_new():
    dedup = Deduplicator(window_seconds=300)
    notification = {"package_name": "com.whatsapp", "title": "Test", "content": "Hello"}
    assert dedup.is_duplicate(notification) is False


def test_deduplicator_duplicate():
    dedup = Deduplicator(window_seconds=300)
    notification = {"package_name": "com.whatsapp", "title": "Test", "content": "Hello"}
    dedup.is_duplicate(notification)
    assert dedup.is_duplicate(notification) is True


def test_deduplicator_different():
    dedup = Deduplicator(window_seconds=300)
    n1 = {"package_name": "com.whatsapp", "title": "Test", "content": "Hello"}
    n2 = {"package_name": "com.whatsapp", "title": "Test", "content": "World"}
    dedup.is_duplicate(n1)
    assert dedup.is_duplicate(n2) is False


def test_verify_token_dev_allows_empty():
    with patch("app.bridge.engine.get_settings") as mock_settings:
        mock_settings.return_value.ENVIRONMENT = "development"
        mock_settings.return_value.NOTIFICATION_INGEST_TOKEN = ""
        bridge = NotificationBridge()
        assert bridge.verify_token(None) is True


def test_verify_token_production_requires_token():
    with patch("app.bridge.engine.get_settings") as mock_settings:
        mock_settings.return_value.ENVIRONMENT = "production"
        mock_settings.return_value.NOTIFICATION_INGEST_TOKEN = "secret-123"
        bridge = NotificationBridge()
        assert bridge.verify_token(None) is False


def test_verify_token_production_wrong_token():
    with patch("app.bridge.engine.get_settings") as mock_settings:
        mock_settings.return_value.ENVIRONMENT = "production"
        mock_settings.return_value.NOTIFICATION_INGEST_TOKEN = "secret-123"
        bridge = NotificationBridge()
        assert bridge.verify_token("wrong-token") is False


def test_verify_token_production_correct_token():
    with patch("app.bridge.engine.get_settings") as mock_settings:
        mock_settings.return_value.ENVIRONMENT = "production"
        mock_settings.return_value.NOTIFICATION_INGEST_TOKEN = "secret-123"
        bridge = NotificationBridge()
        assert bridge.verify_token("secret-123") is True


def test_verify_token_production_no_config_blocks():
    with patch("app.bridge.engine.get_settings") as mock_settings:
        mock_settings.return_value.ENVIRONMENT = "production"
        mock_settings.return_value.NOTIFICATION_INGEST_TOKEN = ""
        bridge = NotificationBridge()
        assert bridge.verify_token(None) is False
        assert bridge.verify_token("") is False


def test_bridge_status_includes_token_required():
    with patch("app.bridge.engine.get_settings") as mock_settings:
        mock_settings.return_value.ENVIRONMENT = "production"
        mock_settings.return_value.NOTIFICATION_INGEST_TOKEN = "secret"
        mock_settings.return_value.NOTIFICATIONS_ENABLED = False
        bridge = NotificationBridge()
        status = bridge.get_status()
        assert status["token_required"] is True


def test_bridge_status_dev_token_not_required():
    with patch("app.bridge.engine.get_settings") as mock_settings:
        mock_settings.return_value.ENVIRONMENT = "development"
        mock_settings.return_value.NOTIFICATION_INGEST_TOKEN = ""
        mock_settings.return_value.NOTIFICATIONS_ENABLED = False
        bridge = NotificationBridge()
        status = bridge.get_status()
        assert status["token_required"] is False