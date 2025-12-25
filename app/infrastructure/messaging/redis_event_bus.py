import json
import redis.asyncio as redis
from app.application.messaging.event_bus import EventBus

class RedisEventBus(EventBus):
    def __init__(self, redis_url: str):
        self._redis = redis.from_url(redis_url)

    async def init(self):
        await self._redis.ping()  # проверяем соединение

    async def publish(self, event: dict) -> None:
        await self._redis.publish(event["channel"], json.dumps(event))

    async def subscribe(self, channel: str):
        pubsub = self._redis.pubsub()
        await pubsub.subscribe(channel)
        async for raw_message in pubsub.listen():
            if raw_message["type"] != "message":
                continue
            yield json.loads(raw_message["data"])
