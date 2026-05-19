import pytest
from fastapi import status


pytestmark = pytest.mark.asyncio

API_BASE_URL = "/api/v1/shorten"


async def register_user(client, username: str, email: str, password: str):
    payload = {"username": username, "email": email, "password": password}
    return await client.post("/api/v1/signup", json=payload)


async def login_user(client, email: str, password: str) -> str:
    resp = await client.post("/api/v1/login", json={"email": email, "password": password})
    return resp.json().get("access_token")


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def create_user_and_login(client) -> str:
    password = "strongpassword"
    signup_response = await register_user(
        client,
        "owner",
        "owner@example.com",
        password,
    )
    assert signup_response.status_code == status.HTTP_201_CREATED

    token = await login_user(client, "owner@example.com", password)
    assert token
    return token


async def test_health_check(test_client):
    response = await test_client.get("/health")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}


async def test_create_short_url(test_client, test_url_payload):
    token = await create_user_and_login(test_client)

    response = await test_client.post(
        API_BASE_URL,
        json=test_url_payload,
        headers=auth_headers(token),
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["url"] == test_url_payload["url"]
    assert len(data["short_code"]) == 6
    assert data["short_url"].endswith(data["short_code"])


async def test_get_created_url(test_client, test_url_payload):
    token = await create_user_and_login(test_client)

    create_response = await test_client.post(
        API_BASE_URL,
        json=test_url_payload,
        headers=auth_headers(token),
    )
    short_code = create_response.json()["short_code"]

    response = await test_client.get(
        f"{API_BASE_URL}/{short_code}",
        headers=auth_headers(token),
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["url"] == test_url_payload["url"]
    assert data["short_code"] == short_code


async def test_missing_url_returns_404(test_client):
    token = await create_user_and_login(test_client)

    response = await test_client.get(
        f"{API_BASE_URL}/missing",
        headers=auth_headers(token),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "URL not found"}


async def test_invalid_url_returns_422(test_client):
    token = await create_user_and_login(test_client)

    response = await test_client.post(
        API_BASE_URL,
        json={"url": "not-a-url"},
        headers=auth_headers(token),
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
