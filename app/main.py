from fastapi import FastAPI

from app.interfaces.rest.routers.auth_router import router as auth_router
from app.interfaces.rest.routers.user_router import router as user_router
from app.interfaces.rest.routers.room_router import router as room_router
from app.interfaces.rest.routers.message_router import router as message_router


def create_app() -> FastAPI:
    app = FastAPI(title="Chat Application Backend")

    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(room_router)
    app.include_router(message_router)

    return app


app = create_app()