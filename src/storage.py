import time
import asyncio
from abc import ABC, abstractmethod

class RateLimitStorage(ABC):
    @abstractmethod
    async def allow(self, key: str) -> bool:
        """
        Return True if request is allowed, False otherwise.
        """
        pass


class InMemoryStorage(RateLimitStorage):
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = {}
        self.timestamps = {}
        self.lock = asyncio.Lock()

    async def allow(self, key: str) -> bool:
        async with self.lock:
            now = time.monotonic()

            last = self.timestamps.get(key, now)
            tokens = self.tokens.get(key, self.capacity)

            tokens += (now - last) * self.refill_rate
            tokens = min(tokens, self.capacity)

            if tokens < 1:
                self.tokens[key] = tokens
                self.timestamps[key] = now
                return False

            self.tokens[key] = tokens - 1
            self.timestamps[key] = now
            return True