import hashlib
import time
from typing import Any


class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = {}

    def is_allowed(self, device_id: str) -> bool:
        now = time.time()
        cutoff = now - self.window_seconds

        if device_id not in self._requests:
            self._requests[device_id] = []

        self._requests[device_id] = [
            t for t in self._requests[device_id] if t > cutoff
        ]

        if len(self._requests[device_id]) >= self.max_requests:
            return False

        self._requests[device_id].append(now)
        return True

    def get_retry_after(self, device_id: str) -> int:
        if device_id not in self._requests or not self._requests[device_id]:
            return 0
        oldest = min(self._requests[device_id])
        return max(1, int(self.window_seconds - (time.time() - oldest)))


class Deduplicator:
    def __init__(self, window_seconds: int = 300) -> None:
        self.window_seconds = window_seconds
        self._seen: dict[str, float] = {}

    def is_duplicate(self, notification: dict[str, Any]) -> bool:
        now = time.time()
        cutoff = now - self.window_seconds

        self._seen = {k: v for k, v in self._seen.items() if v > cutoff}

        notification_hash = self._compute_hash(notification)

        if notification_hash in self._seen:
            return True

        self._seen[notification_hash] = now
        return False

    def _compute_hash(self, notification: dict[str, Any]) -> str:
        parts = [
            str(notification.get("package_name", "")),
            str(notification.get("title", "")),
            str(notification.get("content", ""))
        ]
        raw = "|".join(parts)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


rate_limiter = RateLimiter()
deduplicator = Deduplicator()