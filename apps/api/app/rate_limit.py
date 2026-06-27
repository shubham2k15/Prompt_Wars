import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._buckets: dict[str, deque[float]] = defaultdict(deque)

    def hit(self, key: str, limit: int, window_seconds: int) -> None:
        now = time.time()
        bucket = self._buckets[key]
        while bucket and bucket[0] <= now - window_seconds:
            bucket.popleft()
        if len(bucket) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again shortly.",
            )
        bucket.append(now)


rate_limiter = InMemoryRateLimiter()


def enforce_rate_limit(request: Request, bucket: str, limit: int, window_seconds: int) -> None:
    client_host = request.client.host if request.client else "unknown"
    rate_limiter.hit(f"{bucket}:{client_host}", limit, window_seconds)

