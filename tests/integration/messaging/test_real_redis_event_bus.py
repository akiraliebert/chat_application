import asyncio
import uuid
import pytest

from app.infrastructure.messaging.redis_event_bus import RedisEventBus
from app.config.settings import settings


@pytest.mark.asyncio
async def test_publish_and_subscribe_event():
    bus = RedisEventBus(settings.redis_url)
    await bus.init()

    channel = "test_ws_events"
    event = {
        "channel": channel,
        "message": {
            "type": "test_event",
            "payload": {
                "id": str(uuid.uuid4()),
                "value": "hello",
            },
        },
    }

    received_event = None

    async def subscriber():
        nonlocal received_event
        async for e in bus.subscribe(channel):
            received_event = e
            break

    subscriber_task = asyncio.create_task(subscriber())

    # даём подписчику время реально подписаться
    await asyncio.sleep(0.1)

    await bus.publish(event)

    # ждём получения события
    await asyncio.wait_for(subscriber_task, timeout=2)

    assert received_event is not None
    assert received_event["channel"] == channel
    assert received_event["message"]["type"] == "test_event"
    assert received_event["message"]["payload"]["value"] == "hello"
