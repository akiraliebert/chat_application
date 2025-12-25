from uuid import UUID

from app.domain.value_objects.room_id import RoomId
from app.domain.value_objects.user_id import UserId

from app.application.use_cases.message.create_user_message import CreateUserMessageUseCase
from app.application.use_cases.message.create_system_message import CreateSystemMessageUseCase
from app.application.messaging.event_bus import EventBus

from app.infrastructure.database.db import AsyncSessionLocal
from app.infrastructure.database.uow.sqlalchemy_uow import SQLAlchemyUnitOfWork
from app.infrastructure.database.repositories.message_repository import (
    PostgresMessageRepository,
)
from app.infrastructure.database.repositories.room_repository import (
    PostgresRoomRepository,
)


async def handle_join_room(
    *,
    event_bus: EventBus,
    manager,
    user_id: UserId,
    payload: dict,
) -> None:
    room_id_raw = payload.get("room_id")
    if not room_id_raw:
        return

    room_id = RoomId(UUID(room_id_raw))
    manager.join_room(
        room_id=room_id.value,
        user_id=user_id.value,
    )

    # SYSTEM message: user joined
    async with AsyncSessionLocal() as session:
        uow = SQLAlchemyUnitOfWork(session)
        message_repo = PostgresMessageRepository(session)

        use_case = CreateSystemMessageUseCase(
            uow=uow,
            message_repository=message_repo,
        )

        message = await use_case.execute(
            room_id=room_id,
            content=f"User {user_id.value} joined the room",
        )

    await event_bus.publish({
        "channel": "ws_events",
        "message": {
            "type": "system_message",
            "payload": {
                "id": str(message.id.value),
                "room_id": str(room_id.value),
                "content": message.content.value,
                "created_at": message.created_at.isoformat(),
            },
        },
    })


async def handle_leave_room(
    *,
    event_bus: EventBus,
    manager,
    user_id: UserId
) -> None:
    for room_id in manager.room_online_memberships(user_id.value):
        async with AsyncSessionLocal() as session:
            uow = SQLAlchemyUnitOfWork(session)
            message_repo = PostgresMessageRepository(session)

            use_case = CreateSystemMessageUseCase(
                uow=uow,
                message_repository=message_repo,
            )

            message = await use_case.execute(
                room_id=RoomId(room_id),
                content=f"User {user_id.value} left the room",
            )

        await event_bus.publish({
            "channel": "ws_events",
            "message": {
                "type": "system_message",
                "payload": {
                    "id": str(message.id.value),
                    "room_id": str(room_id),
                    "content": message.content.value,
                    "created_at": message.created_at.isoformat(),
                },
            },
        })


async def handle_send_message(
    *,
    event_bus: EventBus,
    user_id: UserId,
    payload: dict,
) -> None:
    room_id_raw = payload.get("room_id")
    content = payload.get("content")

    if not room_id_raw or not content:
        return

    room_id = RoomId(UUID(room_id_raw))

    async with AsyncSessionLocal() as session:
        uow = SQLAlchemyUnitOfWork(session)

        message_repo = PostgresMessageRepository(session)
        room_repo = PostgresRoomRepository(session)

        use_case = CreateUserMessageUseCase(
            uow=uow,
            message_repository=message_repo,
            room_repository=room_repo,
        )

        message = await use_case.execute(
            room_id=room_id,
            sender_id=user_id,
            content=content,
        )

    await event_bus.publish({
        "channel": "ws_events",
        "message": {
            "type": "new_message",
            "payload": {
                "id": str(message.id.value),
                "room_id": str(message.room_id.value),
                "sender_id": str(message.sender_id.value),
                "content": message.content.value,
                "created_at": message.created_at.isoformat(),
            },
        },
    })


async def handle_typing(
    *,
    event_bus: EventBus,
    user_id: UserId,
    payload: dict,
) -> None:
    room_id_raw = payload.get("room_id")
    if not room_id_raw:
        return

    room_id = UUID(room_id_raw)

    await event_bus.publish({
        "channel": "ws_events",
        "message": {
            "type": "typing",
            "payload": {
                "room_id": str(room_id),
                "user_id": str(user_id.value),
            },
        },
    })