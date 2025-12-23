import pytest
from httpx import AsyncClient
from uuid import UUID


@pytest.mark.asyncio
async def test_create_room_requires_auth(client: AsyncClient):
    response = await client.post(
        "/rooms",
        json={
            "name": "Public room",
            "room_type": "public",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_public_room_success(
    client: AsyncClient,
    auth_tokens,
):
    response = await client.post(
        "/rooms",
        json={
            "name": "Public room",
            "room_type": "public",
        },
        headers={
            "Authorization": f"Bearer {auth_tokens['access_token']}",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Public room"
    assert data["room_type"] == "public"
    assert isinstance(UUID(data["id"]), UUID)
    assert len(data["members"]) == 1


@pytest.mark.asyncio
async def test_create_private_room_without_second_user(
    client: AsyncClient,
    auth_tokens,
):
    response = await client.post(
        "/rooms",
        json={
            "name": "Private chat",
            "room_type": "private",
            "second_user_id": None,
        },
        headers={
            "Authorization": f"Bearer {auth_tokens['access_token']}",
        },
    )

    assert response.status_code == 422  # second_user_id обязателен


@pytest.mark.asyncio
async def test_create_private_room_and_conflict(
    client: AsyncClient,
    auth_tokens,
):
    second_user = {
        "email": "private@test.com",
        "password": "strong-password",
    }

    register_resp = await client.post("/auth/register", json=second_user)
    assert register_resp.status_code == 201

    login_resp = await client.post("/auth/login", json=second_user)
    second_user_tokens = login_resp.json()

    # создаём private room
    response = await client.post(
        "/rooms",
        json={
            "name": "Private chat",
            "room_type": "private",
            "second_user_id": register_resp.json()["id"],
        },
        headers={
            "Authorization": f"Bearer {auth_tokens['access_token']}",
        },
    )

    assert response.status_code == 201

    # пытаемся создать такой же private room
    conflict = await client.post(
        "/rooms",
        json={
            "name": "Private chat duplicate",
            "room_type": "private",
            "second_user_id": register_resp.json()["id"],
        },
        headers={
            "Authorization": f"Bearer {second_user_tokens['access_token']}",
        },
    )

    assert conflict.status_code == 409


@pytest.mark.asyncio
async def test_join_room_flow(
    client: AsyncClient,
    auth_tokens,
):
    # создаём комнату
    create_resp = await client.post(
        "/rooms",
        json={
            "name": "Joinable room",
            "room_type": "public",
        },
        headers={
            "Authorization": f"Bearer {auth_tokens['access_token']}",
        },
    )

    room_id = create_resp.json()["id"]

    # регистрируем второго пользователя
    second_user = {
        "email": "joiner@test.com",
        "password": "strong-password",
    }
    reg = await client.post("/auth/register", json=second_user)
    login = await client.post("/auth/login", json=second_user)
    second_token = login.json()["access_token"]

    # join
    join_resp = await client.post(
        f"/rooms/{room_id}/join",
        headers={
            "Authorization": f"Bearer {second_token}",
        },
    )

    assert join_resp.status_code == 204

    # повторный join
    repeat_join = await client.post(
        f"/rooms/{room_id}/join",
        headers={
            "Authorization": f"Bearer {second_token}",
        },
    )

    assert repeat_join.status_code == 409


@pytest.mark.asyncio
async def test_get_room_access_control(
    client: AsyncClient,
    auth_tokens,
):
    # создаём комнату
    create_resp = await client.post(
        "/rooms",
        json={
            "name": "Protected room",
            "room_type": "public",
        },
        headers={
            "Authorization": f"Bearer {auth_tokens['access_token']}",
        },
    )
    room_id = create_resp.json()["id"]

    # сторонний пользователь
    outsider = {
        "email": "outsider@test.com",
        "password": "strong-password",
    }
    await client.post("/auth/register", json=outsider)
    login = await client.post("/auth/login", json=outsider)
    outsider_token = login.json()["access_token"]

    # не участник → 404
    forbidden = await client.get(
        f"/rooms/{room_id}",
        headers={
            "Authorization": f"Bearer {outsider_token}",
        },
    )
    assert forbidden.status_code == 404

    # владелец → 200
    ok = await client.get(
        f"/rooms/{room_id}",
        headers={
            "Authorization": f"Bearer {auth_tokens['access_token']}",
        },
    )

    assert ok.status_code == 200
    data = ok.json()
    assert data["id"] == room_id
