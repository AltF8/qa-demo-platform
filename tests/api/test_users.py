from collections.abc import Iterator
from typing import Any

import pytest
import pytest_asyncio
from httpx import AsyncClient, Response

from app.api.users import User


@pytest.fixture(autouse=True)
def reset_users() -> Iterator[None]:
    User._users.clear()
    yield
    User._users.clear()


@pytest.fixture
def user_data() -> dict[str, Any]:
    return {
        "name": "Alice",
        "email": "alice@example.com",
        "age": 25,
        "is_active": True,
    }


@pytest_asyncio.fixture
async def create_user(async_client: AsyncClient, user_data: dict[str, Any]) -> Response:
    response = await async_client.post("/users", json=user_data)
    return response


def test_create_user(create_user: Response) -> None:
    assert create_user.status_code == 201

    body = create_user.json()
    assert body["name"] == "Alice"
    assert body["email"] == "alice@example.com"
    assert body["age"] == 25
    assert body["is_active"] is True
    assert isinstance(body["id"], int)


@pytest.mark.asyncio
async def test_get_user_by_id(async_client: AsyncClient, create_user: Response) -> None:
    user_id = create_user.json()["id"]

    response = await async_client.get(f"/users/{user_id}")

    assert response.status_code == 200
    assert response.json() == create_user.json()


@pytest.mark.asyncio
async def test_duplicate_email(
    async_client: AsyncClient, create_user: Response, user_data: dict[str, Any]
) -> None:
    assert create_user.status_code == 201

    response = await async_client.post("/users", json=user_data)

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Email already exists",
    }
    assert len(User._users) == 1


@pytest.mark.asyncio
async def test_duplicate_email_case_insensitive(
    async_client: AsyncClient, create_user: Response, user_data: dict[str, Any]
) -> None:
    assert create_user.status_code == 201
    user_data["email"] = user_data["email"].upper()
    response = await async_client.post(url="/users", json=user_data)

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Email already exists",
    }
    assert len(User._users) == 1


@pytest.mark.asyncio
async def test_get_unknown_user(async_client: AsyncClient) -> None:
    response = await async_client.get(url="/users/999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


@pytest.mark.parametrize(
    "field,invalid_value,expected_error",
    [
        ("name", "A", "string_too_short"),
        ("name", "", "string_too_short"),
        ("name", "A" * 51, "string_too_long"),
        ("email", "not-an-email", "value_error"),
        ("age", 17, "greater_than_equal"),
        ("age", 121, "less_than_equal"),
        ("age", "hello", "int_parsing"),
    ],
)
@pytest.mark.asyncio
async def test_create_user_validation(
    async_client: AsyncClient,
    user_data: dict[str, Any],
    field: str,
    invalid_value: Any,
    expected_error: str,
) -> None:
    user_data[field] = invalid_value
    response = await async_client.post(url="/users", json=user_data)

    assert response.status_code == 422

    errors = response.json()["detail"]

    assert len(errors) == 1
    assert errors[0]["loc"] == ["body", field]
    assert errors[0]["type"] == expected_error


@pytest.mark.parametrize(
    "field,value",
    [
        ("age", 18),
        ("age", 120),
        ("name", "AB"),
        ("name", "A" * 50),
    ],
)
@pytest.mark.asyncio
async def test_create_user_boundary_values(
    async_client: AsyncClient, user_data: dict[str, Any], field: str, value: Any
) -> None:
    user_data[field] = value
    response = await async_client.post(url="/users", json=user_data)

    assert response.status_code == 201
    assert response.json()[field] == value


@pytest.mark.asyncio
async def test_get_users_empty(async_client: AsyncClient) -> None:
    response = await async_client.get(url="/users")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_users_multiple(
    async_client: AsyncClient, create_user: Response, user_data: dict[str, Any]
) -> None:
    assert create_user.status_code == 201
    users = [create_user.json()]

    user_data["name"] = "Bob"
    user_data["email"] = "bob@example.com"
    user_data["age"] = 30

    create_response = await async_client.post(url="/users", json=user_data)
    assert create_response.status_code == 201
    users.append(create_response.json())

    list_response = await async_client.get(url="/users")
    assert list_response.status_code == 200

    actual_users = list_response.json()

    for user in users:
        assert user in actual_users
    assert len(users) == len(actual_users)


@pytest.mark.asyncio
async def test_delete_user(async_client: AsyncClient, create_user: Response) -> None:
    assert create_user.status_code == 201

    user_id = create_user.json()["id"]
    delete_response = await async_client.delete(url=f"/users/{user_id}")

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = await async_client.get(url=f"/users/{user_id}")

    assert get_response.status_code == 404
    assert get_response.json() == {"detail": "User not found"}


@pytest.mark.asyncio
async def test_delete_unknown_user(async_client: AsyncClient) -> None:
    response = await async_client.delete(url="/users/999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


@pytest.mark.asyncio
async def test_delete_user_twice(async_client: AsyncClient, create_user: Response) -> None:
    assert create_user.status_code == 201

    user_id = create_user.json()["id"]
    first_delete_response = await async_client.delete(url=f"/users/{user_id}")

    assert first_delete_response.status_code == 204
    assert first_delete_response.content == b""

    second_delete_response = await async_client.delete(url=f"/users/{user_id}")

    assert second_delete_response.status_code == 404
    assert second_delete_response.json() == {"detail": "User not found"}
