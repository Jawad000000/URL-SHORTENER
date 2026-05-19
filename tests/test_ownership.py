import pytest
from fastapi import status


pytestmark = pytest.mark.asyncio

API_BASE_URL = "/api/v1/shorten"
PASSWORD = "strongpassword"


async def register_and_login(client, username: str, email: str) -> str:
    signup_response = await client.post(
        "/api/v1/signup",
        json={"username": username, "email": email, "password": PASSWORD},
    )
    assert signup_response.status_code == status.HTTP_201_CREATED

    login_response = await client.post(
        "/api/v1/login",
        json={"email": email, "password": PASSWORD},
    )
    assert login_response.status_code == status.HTTP_200_OK

    token = login_response.json()["access_token"]
    assert token
    return token


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def create_short_url(client, token: str, payload: dict):
    response = await client.post(
        API_BASE_URL,
        json=payload,
        headers=auth_headers(token),
    )
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


async def test_authenticated_user_can_create_short_url(test_client, test_url_payload):
    token = await register_and_login(test_client, "owner", "owner@example.com")

    data = await create_short_url(test_client, token, test_url_payload)

    assert data["url"] == test_url_payload["url"]
    assert len(data["short_code"]) == 6


async def test_anonymous_user_cannot_create_short_url(test_client, test_url_payload):
    response = await test_client.post(API_BASE_URL, json=test_url_payload)

    assert response.status_code in {
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    }


async def test_non_owner_cannot_get_url(test_client, test_url_payload):
    owner_token = await register_and_login(test_client, "owner", "owner@example.com")
    other_token = await register_and_login(test_client, "other", "other@example.com")
    data = await create_short_url(test_client, owner_token, test_url_payload)

    response = await test_client.get(
        f"{API_BASE_URL}/{data['short_code']}",
        headers=auth_headers(other_token),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_owner_can_update_and_delete_own_url(
    test_client,
    test_url_payload,
    updated_url_payload,
):
    token = await register_and_login(test_client, "owner", "owner@example.com")
    data = await create_short_url(test_client, token, test_url_payload)

    update_response = await test_client.patch(
        f"{API_BASE_URL}/{data['short_code']}",
        json=updated_url_payload,
        headers=auth_headers(token),
    )
    assert update_response.status_code == status.HTTP_200_OK
    assert update_response.json()["url"] == updated_url_payload["url"]

    delete_response = await test_client.delete(
        f"{API_BASE_URL}/{data['short_code']}",
        headers=auth_headers(token),
    )
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT


async def test_public_redirect_still_works_without_login(test_client, test_url_payload):
    token = await register_and_login(test_client, "owner", "owner@example.com")
    data = await create_short_url(test_client, token, test_url_payload)

    response = await test_client.get(f"/{data['short_code']}", follow_redirects=False)

    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
