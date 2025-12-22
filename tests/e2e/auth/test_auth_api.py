import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_me_requires_auth(client: AsyncClient):
    response = await client.get("/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_invalid_token(client: AsyncClient):
    response = await client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_valid_token(
    client: AsyncClient,
    auth_tokens,
):
    response = await client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {auth_tokens['access_token']}"
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert all(sub in data["email"] for sub in ("e2e", "@test.com"))  # проверяем не полностью, т.к у нас uuid стоит
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_refresh_returns_new_tokens(
    client: AsyncClient,
    auth_tokens,
):
    response = await client.post(
        "/auth/refresh",
        json={
            "refresh_token": auth_tokens["refresh_token"],
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data



@pytest.mark.asyncio
async def test_refresh_invalid_token(client: AsyncClient):
    response = await client.post(
        "/auth/refresh",
        json={
            "refresh_token": "invalid.refresh.token",
        },
    )

    assert response.status_code == 401
