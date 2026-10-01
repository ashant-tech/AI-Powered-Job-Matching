"""In-memory sliding-window rate limiting for sensitive endpoints.

Single-process by design (matches the current deployment). If the backend is
ever scaled to multiple workers, swap the store for Redis.
"""
import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()

    async def __call__(self, request: Request):
        key = self._client_key(request)
        now = time.monotonic()
        with self._lock:
            window = self._hits[key]
            while window and now - window[0] >= self.window_seconds:
                window.popleft()
            if len(window) >= self.max_requests:
                retry_after = int(self.window_seconds - (now - window[0])) + 1
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Please try again later.",
                    headers={"Retry-After": str(retry_after)},
                )
            window.append(now)

    @staticmethod
    def _client_key(request: Request) -> str:
        # Behind the Render frontend proxy (and Cloudflare) every request would
        # otherwise share the proxy's IP, so all users would share one limit
        # bucket and trip it together. Trust the leftmost forwarded hop.
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
