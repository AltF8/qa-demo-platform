import pytest_asyncio
from collections.abc import AsyncIterator
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest_asyncio.fixture
async def async_client() -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
      transport=ASGITransport(app=app),
      base_url="http://test",
    ) as client:
      yield client
