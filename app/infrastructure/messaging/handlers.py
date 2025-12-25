from uuid import UUID

from app.infrastructure.websocket.manager import ConnectionManager


class WebSocketEventHandler:
    def __init__(self, manager: ConnectionManager):
        self._manager = manager

    async def handle(self, event: dict) -> None:
        event_type = event.get("type")
        payload = event.get("payload", {})

        if event_type in ("new_message", "system_message"):
            await self._manager.broadcast_to_room(
                room_id=UUID(payload["room_id"]),
                message=event,
            )
        elif event_type == "typing":
            await self._manager.broadcast_to_room(
                room_id=UUID(payload["room_id"]),
                message=event,
                exclude_user_id=UUID(payload.get("user_id")),
            )
