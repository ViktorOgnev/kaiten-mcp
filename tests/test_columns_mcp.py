"""Exercise column validation through a connected MCP session, before HTTP."""

import json
from contextlib import asynccontextmanager
from datetime import timedelta

import pytest
import respx
from mcp.shared.memory import create_connected_server_and_client_session
from mcp.types import TextContent

from kaiten_mcp import runtime
from kaiten_mcp.client import KaitenClient


@pytest.fixture
def mcp_client(monkeypatch):
    @asynccontextmanager
    async def connect():
        client = KaitenClient(domain="test-company", token="test-token")
        monkeypatch.setattr(runtime, "_client", client)
        try:
            async with create_connected_server_and_client_session(
                runtime.app, read_timeout_seconds=timedelta(seconds=10)
            ) as session:
                yield session
        finally:
            await client.close()

    return connect


@pytest.mark.parametrize(
    "tool_name, identifiers",
    [
        ("kaiten_update_column", {"board_id": 10, "column_id": 5}),
        ("kaiten_update_subcolumn", {"column_id": 10, "subcolumn_id": 20}),
    ],
)
@pytest.mark.parametrize(
    "fields, error_fragment",
    [
        ({}, "at least one non-null"),
        ({"auto_archive_days": 14}, "Additional properties"),
        ({"title": "Done", "auto_archive_days": 14}, "Additional properties"),
        ({"wip_limit": None}, "not of type"),
    ],
)
async def test_invalid_update_returns_mcp_error_without_http(
    mcp_client, tool_name, identifiers, fields, error_fragment
):
    async with mcp_client() as session:
        with respx.mock(assert_all_called=False) as http:
            result = await session.call_tool(tool_name, {**identifiers, **fields})
    assert result.isError is True
    text = " ".join(c.text for c in result.content if isinstance(c, TextContent))
    assert error_fragment in text
    assert not http.calls


@pytest.mark.parametrize(
    "tool_name, identifiers, path",
    [
        ("kaiten_update_column", {"board_id": 10, "column_id": 5}, "/boards/10/columns/5"),
        (
            "kaiten_update_subcolumn",
            {"column_id": 10, "subcolumn_id": 20},
            "/columns/10/subcolumns/20",
        ),
    ],
)
async def test_valid_zero_update_reaches_http(mcp_client, tool_name, identifiers, path):
    async with mcp_client() as session:
        with respx.mock(base_url="https://test-company.kaiten.ru/api/latest") as http:
            route = http.patch(path).respond(json={"id": 5, "wip_limit": 0})
            result = await session.call_tool(tool_name, {**identifiers, "wip_limit": 0})
            assert route.call_count == 1
            assert json.loads(route.calls[0].request.content) == {"wip_limit": 0}
    assert result.isError is False
