from fastapi import Request, HTTPException, status
from .storage import InMemoryStorage

class RateLimiter:
    """
    FastAPI dependency for rate limiting requests.
    """
    def __init__(
        self,
        requests: int,
        per_seconds: int,
        key_func=None,
    ):
        self.capacity = requests
        self.refill_rate = requests / per_seconds
        self.key_func = key_func or self.default_key
        self.storage = InMemoryStorage(
            capacity=self.capacity,
            refill_rate=self.refill_rate,
        )

    async def default_key(self, request: Request) -> str:
        return request.client.host if request.client else "anonymous"

    async def __call__(self, request: Request):
        key = await self.key_func(request)

        allowed = await self.storage.allow(key)

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too Many Requests",
            )
