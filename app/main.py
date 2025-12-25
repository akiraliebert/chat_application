from fastapi import FastAPI
import asyncio
from contextlib import asynccontextmanager

from app.infrastructure.websocket.manager import ConnectionManager
from app.infrastructure.messaging.redis_event_bus import RedisEventBus
from app.infrastructure.messaging.handlers import WebSocketEventHandler

from app.interfaces.rest.routers.auth_router import router as auth_router
from app.interfaces.rest.routers.user_router import router as user_router
from app.interfaces.rest.routers.room_router import router as room_router
from app.interfaces.rest.routers.message_router import router as message_router
from app.interfaces.websocket.router import router as ws_router


from app.config.settings import settings


async def listen_redis(redis_bus: RedisEventBus, handler: WebSocketEventHandler):
    async for event in redis_bus.subscribe("ws_events"):
        await handler.handle(event['message'])


@asynccontextmanager
async def lifespan(app: FastAPI):
    manager = ConnectionManager()
    handler = WebSocketEventHandler(manager)
    redis_bus = RedisEventBus(redis_url=settings.redis_url)

    await redis_bus.init()

    # сохраняем в state
    app.state.ws_manager = manager
    app.state.ws_event_handler = handler
    app.state.redis_bus = redis_bus


    task = asyncio.create_task(listen_redis(redis_bus, handler))

    try:
        yield
    finally:
        task.cancel()


def create_app() -> FastAPI:
    app = FastAPI(title="Chat Application Backend", lifespan=lifespan)

    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(room_router)
    app.include_router(message_router)
    app.include_router(ws_router)


    return app


app = create_app()