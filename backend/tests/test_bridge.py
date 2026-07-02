import pytest
from app.bridge.rate_limit import RateLimiter, Deduplicator


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