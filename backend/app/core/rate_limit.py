"""
In-Memory Rate Limiting Middleware / Dependency
-----------------------------------------------
Protects authentication, inference, and GenAI report generation against abuse.
Provides standard HTTP 429 Too Many Requests responses with Retry-After headers.
"""

import time
from collections import defaultdict
from fastapi import Request, HTTPException, status
from app.core.config import settings

class RateLimiter:
    def __init__(self, requests_per_minute: int):
        self.rpm = requests_per_minute
        self.window_seconds = 60
        self.requests = defaultdict(list)

    def check(self, request: Request):
        if not settings.RATE_LIMIT_ENABLED:
            return

        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old timestamps
        recent_timestamps = [t for t in self.requests[client_ip] if t > window_start]
        self.requests[client_ip] = recent_timestamps

        if len(recent_timestamps) >= self.rpm:
            retry_after = int(self.window_seconds - (now - recent_timestamps[0])) + 1
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: Maximum {self.rpm} requests per minute. Try again in {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)}
            )

        self.requests[client_ip].append(now)

auth_limiter = RateLimiter(settings.RATE_LIMIT_AUTH_PER_MINUTE)
predict_limiter = RateLimiter(settings.RATE_LIMIT_PREDICT_PER_MINUTE)
report_limiter = RateLimiter(settings.RATE_LIMIT_REPORTS_PER_MINUTE)
