import json
from typing import Any, Optional

from redis import asyncio as aioredis

class CacheHandler:
    async def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError

    async def set(self, key: str, value: Any, ttl: int) -> None:
        raise NotImplementedError

    async def delete(self, key: str) -> None:
        raise NotImplementedError

class RedisCacheHandler(CacheHandler):
    def __init__(self, redis_url='redis://localhost:6379'):
        self.client = aioredis.from_url(redis_url)

    async def get(self, key: str) -> Optional[Any]:
        data = await self.client.get(key)
        if data:
            return json.loads(data)
        return None

    async def set(self, key: str, value: Any, ttl: int) -> None:
        await self.client.set(key, value, ex=ttl)

    async def delete(self, key: str) -> None:
        await self.client.delete(key)