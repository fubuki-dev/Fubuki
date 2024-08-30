import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
import json
from typing import Any, Optional

from redis import asyncio as aioredis

class BaseCacheHandler:
    async def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError

    async def set(self, key: str, value: Any, ttl: int) -> None:
        raise NotImplementedError

    async def delete(self, key: str) -> None:
        raise NotImplementedError

class InMemoryCacheHandler(BaseCacheHandler):
    def __init__(self):
        self.cache = {}
        self.locks = defaultdict(asyncio.Lock)
        self.ttl = {}

    async def get(self, key: str) -> Optional[Any]:
        async with self.locks[key]:
            if key in self.ttl and self.ttl[key] < datetime.utcnow():
                del self.cache[key]
                del self.ttl[key]
                return None
            
            data = self.cache.get(key)
            if data:
                return json.loads(data)
            return None

    async def set(self, key: str, value: Any, ttl: int) -> None:
        async with self.locks[key]:
            self.cache[key] = json.dumps(value)
            self.ttl[key] = datetime.utcnow() + timedelta(seconds=ttl)

    async def delete(self, key: str) -> None:
        async with self.locks[key]:
            if key in self.cache:
                del self.cache[key]
            if key in self.ttl:
                del self.ttl[key]

class RedisCacheHandler(BaseCacheHandler):
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