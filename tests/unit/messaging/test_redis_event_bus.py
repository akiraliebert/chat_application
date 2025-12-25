import json
import pytest
from unittest.mock import AsyncMock, Mock

from app.infrastructure.messaging.redis_event_bus import RedisEventBus


@pytest.mark.asyncio
async def test_publish_sends_event_to_redis():
    redis_mock = AsyncMock()
    redis_mock.publish = AsyncMock()

    bus = RedisEventBus("redis://test")
    bus._redis = redis_mock

    event = {
        "channel": "chat",
        "type": "message_sent",
        "payload": {"text": "hello"},
    }

    await bus.publish(event)

    redis_mock.publish.assert_awaited_once_with(
        "chat",
        json.dumps(event),
    )

@pytest.mark.asyncio
async def test_subscribe_yields_only_message_events():
    pubsub_mock = AsyncMock()

    async def listen():
        yield {"type": "subscribe"}
        yield {
            "type": "message",
            "data": json.dumps(
                {"channel": "chat", "payload": {"text": "hi"}}
            ),
        }
        yield {"type": "unsubscribe"}

    pubsub_mock.listen = listen
    pubsub_mock.subscribe = AsyncMock()

    redis_mock = Mock()
    redis_mock.pubsub.return_value = pubsub_mock

    bus = RedisEventBus("redis://test")
    bus._redis = redis_mock

    events = []

    async for event in bus.subscribe("chat"):
        events.append(event)
        break

    pubsub_mock.subscribe.assert_awaited_once_with("chat")

    assert events == [
        {
            "channel": "chat",
            "payload": {"text": "hi"},
        }
    ]
