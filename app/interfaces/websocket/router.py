import json
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.interfaces.websocket.auth import get_current_user_ws
from app.interfaces.websocket.handlers import handle_join_room, handle_typing, handle_send_message, handle_leave_room

from app.domain.value_objects.user_id import UserId


router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # 1. WS auth
    user_id: UserId = await get_current_user_ws(websocket)

    # 2. Register connection
    manager = websocket.app.state.ws_manager
    await manager.connect(user_id.value, websocket)

    event_bus = websocket.app.state.redis_bus

    try:
        while True:
            raw_data = await websocket.receive_text()
            data = json.loads(raw_data)

            event_type = data.get("type")
            payload = data.get("payload", {})

            if event_type == "join_room":
                await handle_join_room(
                    event_bus=event_bus,
                    manager=manager,
                    user_id=user_id,
                    payload=payload,
                )

            elif event_type == "send_message":
                await handle_send_message(
                    event_bus=event_bus,
                    user_id=user_id,
                    payload=payload,
                )

            elif event_type == "typing":
                await handle_typing(
                    event_bus=event_bus,
                    user_id=user_id,
                    payload=payload,
                )

            else:
                await websocket.send_json(
                    {
                        "type": "error",
                        "payload": {"message": "Unknown event type"},
                    }
                )

    except WebSocketDisconnect:
        await handle_leave_room(
            event_bus=event_bus,
            manager=manager,
            user_id=user_id,
        )
        manager.disconnect(user_id.value, websocket)
