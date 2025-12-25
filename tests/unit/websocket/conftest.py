import pytest
from unittest.mock import AsyncMock

from app.infrastructure.websocket.manager import ConnectionManager

@pytest.fixture
def manager() -> ConnectionManager:
    return ConnectionManager()


@pytest.fixture
def websocket() -> AsyncMock:
    ws = AsyncMock()
    ws.accept = AsyncMock()
    ws.send_json = AsyncMock()
    return ws