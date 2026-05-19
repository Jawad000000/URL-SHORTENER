from fastapi import Depends, Request, status
from fastapi.exceptions import HTTPException
from src.urls.cache import redis_client
from src.config import Config


async def rate_limit(request: Request) -> None:
    """
    Fixed-window rate limiter backed by Redis.
    Uses the client IP as the key.
    Raises HTTP 429 when the request count exceeds RATE_LIMIT_MAX
    within a RATE_LIMIT_WINDOW-second window.
    """
    client_ip = request.client.host if request.client else "unknown"
    key = f"rate_limit:{client_ip}:{request.url.path}"

    count = await redis_client.incr(key)

    # Only set TTL on the first request in the window
    if count == 1:
        await redis_client.expire(key, Config.RATE_LIMIT_WINDOW)

    if count > Config.RATE_LIMIT_MAX:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {Config.RATE_LIMIT_WINDOW} seconds.",
        )
