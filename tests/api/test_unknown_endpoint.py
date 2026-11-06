import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_unknown_endpoint_returns_404(async_client: AsyncClient):
    response = await async_client.get("/unknown")
    
    assert response.status_code == 404
