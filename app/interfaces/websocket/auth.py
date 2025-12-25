from fastapi import WebSocket, WebSocketException, status
from uuid import UUID

from app.infrastructure.security.jwt_service import JoseJWTService
from app.domain.value_objects.user_id import UserId
from app.infrastructure.database.repositories.user_repository import (
    PostgresUserRepository,
)
from app.infrastructure.database.db import AsyncSessionLocal

async def get_current_user_ws(
    websocket: WebSocket,
) -> UserId:
    """
    WS-authentication.
    Validates JWT and returns UserId.
    """

    token = websocket.query_params.get("token")

    if not token:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Missing token",
        )

    jwt_service = JoseJWTService()

    try:
        user_id: UUID = jwt_service.verify_access_token(token)
    except Exception:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Invalid token",
        )

    if not user_id:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Invalid token payload",
        )

    # проверка, что пользователь реально существует
    async with AsyncSessionLocal() as session:
        repo = PostgresUserRepository(session)
        user = await repo.get_by_id(UserId(user_id))

    if user is None or not user.is_active:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="User not found or inactive",
        )

    return user.id
