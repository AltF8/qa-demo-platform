import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_expected_response(async_client: AsyncClient):
    response = await async_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "qa-demo-platform",
    }
    assert response.headers["content-type"] == "application/json"
