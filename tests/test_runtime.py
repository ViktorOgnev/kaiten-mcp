"""Tests for shared runtime helpers."""

from unittest.mock import AsyncMock, patch

import pytest

from kaiten_mcp import runtime


@pytest.mark.asyncio
async def test_close_client_closes_and_clears_cached_client():
    client = AsyncMock()
    with patch("kaiten_mcp.runtime._client", client):
        await runtime.close_client()

    client.close.assert_awaited_once()
    assert runtime._client is None
