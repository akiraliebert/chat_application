from fastapi import FastAPI

from app.interfaces.rest.routers.auth_router import router as auth_router
from app.interfaces.rest.routers.user_router import router as users_router


def create_app() -> FastAPI:
    app = FastAPI(title="Chat Application Backend")

    app.include_router(auth_router)
    app.include_router(users_router)

    return app


app = create_app()