from typing import Dict, Set
from uuid import UUID

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        # user_id -> set[WebSocket]
        self._user_connections: Dict[UUID, Set[WebSocket]] = {}

        # room_id -> set[user_id]
        self._room_members: Dict[UUID, Set[UUID]] = {}

    # ---------- Connection lifecycle ----------

    async def connect(
        self,
        user_id: UUID,
        websocket: WebSocket,
    ) -> None:
        await websocket.accept()

        if user_id not in self._user_connections:
            self._user_connections[user_id] = set()

        self._user_connections[user_id].add(websocket)

    def disconnect(
        self,
        user_id: UUID,
        websocket: WebSocket,
    ) -> None:
        connections = self._user_connections.get(user_id)
        if not connections:
            return

        connections.discard(websocket)

        if not connections:
            del self._user_connections[user_id]

        # также удаляем пользователя из всех комнат
        for members in self._room_members.values():
            members.discard(user_id)

    # ---------- Room membership ----------

    def join_room(
        self,
        *,
        room_id: UUID,
        user_id: UUID,
    ) -> None:
        if room_id not in self._room_members:
            self._room_members[room_id] = set()

        self._room_members[room_id].add(user_id)

    def leave_room(
        self,
        *,
        room_id: UUID,
        user_id: UUID,
    ) -> None:
        members = self._room_members.get(room_id)
        if not members:
            return

        members.discard(user_id)

        if not members:
            del self._room_members[room_id]

    # ---------- Messaging ----------

    async def send_to_user(
        self,
        *,
        user_id: UUID,
        message: dict,
    ) -> None:
        connections = self._user_connections.get(user_id, set())
        for websocket in connections:
            await websocket.send_json(message)

    async def broadcast_to_room(
        self,
        *,
        room_id: UUID,
        message: dict,
        exclude_user_id: UUID | None = None,
    ) -> None:
        members = self._room_members.get(room_id, set())

        for user_id in members:
            if exclude_user_id and user_id == exclude_user_id:
                continue

            await self.send_to_user(
                user_id=user_id,
                message=message,
            )

    # ---------- Introspection ----------

    def is_user_online(self, user_id: UUID) -> bool:
        return user_id in self._user_connections

    def room_online_members(self, room_id: UUID) -> Set[UUID]:
        return self._room_members.get(room_id, set())

    def room_online_memberships(self, user_id: UUID) -> set[UUID]:
        return {
            room_id
            for room_id, members in self._room_members.items()
            if user_id in members
        }
