"""Shared fixtures for handler integration tests."""

import pytest
import respx

from kaiten_mcp.client import KaitenClient

BASE_URL = "https://test-company.kaiten.ru/api/latest"


@pytest.fixture
def mock_api():
    with respx.mock(base_url=BASE_URL, assert_all_called=False) as router:
        yield router


@pytest.fixture
async def client():
    c = KaitenClient(domain="test-company", token="test-token-12345")
    c._last_request_time = 0.0
    yield c
    if c._client and not c._client.is_closed:
        await c._client.aclose()
