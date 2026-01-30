"""Layer 3: MCP server integration tests for call_tool and list_tools."""
import json

import httpx
import pytest
import respx
from unittest.mock import AsyncMock, patch

from mcp.types import CallToolResult, TextContent, Tool

from kaiten_mcp.client import KaitenClient, KaitenApiError
from kaiten_mcp.server import call_tool, list_tools, get_client, ALL_TOOLS


BASE_URL = "https://test-company.kaiten.ru/api/latest"


@pytest.fixture(autouse=True)
def _inject_client():
    """Inject a real KaitenClient (with test credentials) into the server module."""
    client = KaitenClient(domain="test-company", token="test-token")
    with patch("kaiten_mcp.server._client", client):
        yield client


# ── helpers ──────────────────────────────────────────────────────────────────


def _text(result: CallToolResult) -> str:
    """Extract the text string from a CallToolResult."""
    assert len(result.content) == 1
    item = result.content[0]
    assert isinstance(item, TextContent)
    return item.text


# ── 1. Unknown tool ─────────────────────────────────────────────────────────


async def test_call_tool_unknown_name():
    result = await call_tool("no_such_tool", {})
    assert _text(result) == "Unknown tool: no_such_tool"


async def test_call_tool_unknown_name_special_chars():
    result = await call_tool("foo/bar:baz", {"x": 1})
    assert _text(result) == "Unknown tool: foo/bar:baz"


# ── 2. Handler returns dict ─────────────────────────────────────────────────


async def test_call_tool_handler_returns_dict():
    payload = {"id": 1, "title": "Test Space"}
    tool_name = "kaiten_get_space"
    with patch.dict(ALL_TOOLS, {tool_name: {**ALL_TOOLS[tool_name], "handler": AsyncMock(return_value=payload)}}):
        result = await call_tool(tool_name, {"space_id": 1})
    parsed = json.loads(_text(result))
    assert parsed == payload


async def test_call_tool_handler_returns_nested_dict():
    payload = {"id": 1, "meta": {"key": "value", "count": 42}}
    tool_name = "kaiten_get_space"
    with patch.dict(ALL_TOOLS, {tool_name: {**ALL_TOOLS[tool_name], "handler": AsyncMock(return_value=payload)}}):
        result = await call_tool(tool_name, {"space_id": 1})
    parsed = json.loads(_text(result))
    assert parsed == payload
    assert parsed["meta"]["count"] == 42


# ── 3. Handler returns list ─────────────────────────────────────────────────


async def test_call_tool_handler_returns_list():
    payload = [{"id": 1}, {"id": 2}]
    tool_name = "kaiten_list_spaces"
    with patch.dict(ALL_TOOLS, {tool_name: {**ALL_TOOLS[tool_name], "handler": AsyncMock(return_value=payload)}}):
        result = await call_tool(tool_name, {})
    parsed = json.loads(_text(result))
    assert parsed == payload
    assert len(parsed) == 2


async def test_call_tool_handler_returns_empty_list():
    tool_name = "kaiten_list_spaces"
    with patch.dict(ALL_TOOLS, {tool_name: {**ALL_TOOLS[tool_name], "handler": AsyncMock(return_value=[])}}):
        result = await call_tool(tool_name, {})
    assert json.loads(_text(result)) == []


# ── 4. Handler returns None ─────────────────────────────────────────────────


async def test_call_tool_handler_returns_none():
    tool_name = "kaiten_delete_space"
    with patch.dict(ALL_TOOLS, {tool_name: {**ALL_TOOLS[tool_name], "handler": AsyncMock(return_value=None)}}):
        result = await call_tool(tool_name, {"space_id": 1})
    assert _text(result) == "OK"


# ── 5. Handler returns string ───────────────────────────────────────────────


async def test_call_tool_handler_returns_string():
    tool_name = "kaiten_get_space"
    with patch.dict(ALL_TOOLS, {tool_name: {**ALL_TOOLS[tool_name], "handler": AsyncMock(return_value="some text")}}):
        result = await call_tool(tool_name, {"space_id": 1})
    assert _text(result) == "some text"


async def test_call_tool_handler_returns_integer():
    """Non-dict/list/None/str values are converted via str()."""
    tool_name = "kaiten_get_space"
    with patch.dict(ALL_TOOLS, {tool_name: {**ALL_TOOLS[tool_name], "handler": AsyncMock(return_value=42)}}):
        result = await call_tool(tool_name, {"space_id": 1})
    assert _text(result) == "42"


# ── 6. KaitenApiError ───────────────────────────────────────────────────────


async def test_call_tool_kaiten_api_error():
    tool_name = "kaiten_get_space"
    handler = AsyncMock(side_effect=KaitenApiError(404, "Space not found"))
    with patch.dict(ALL_TOOLS, {tool_name: {**ALL_TOOLS[tool_name], "handler": handler}}):
        result = await call_tool(tool_name, {"space_id": 999})
    assert _text(result) == "Kaiten API Error 404: Space not found"
    assert result.isError is True


async def test_call_tool_kaiten_api_error_rate_limit():
    tool_name = "kaiten_list_spaces"
    handler = AsyncMock(side_effect=KaitenApiError(429, "Rate limit exceeded"))
    with patch.dict(ALL_TOOLS, {tool_name: {**ALL_TOOLS[tool_name], "handler": handler}}):
        result = await call_tool(tool_name, {})
    assert _text(result) == "Kaiten API Error 429: Rate limit exceeded"
    assert result.isError is True


async def test_call_tool_kaiten_api_error_server():
    tool_name = "kaiten_list_spaces"
    handler = AsyncMock(side_effect=KaitenApiError(500, "Internal Server Error"))
    with patch.dict(ALL_TOOLS, {tool_name: {**ALL_TOOLS[tool_name], "handler": handler}}):
        result = await call_tool(tool_name, {})
    assert _text(result) == "Kaiten API Error 500: Internal Server Error"
    assert result.isError is True


# ── 7. Generic exception ────────────────────────────────────────────────────


async def test_call_tool_generic_exception():
    tool_name = "kaiten_get_space"
    handler = AsyncMock(side_effect=ValueError("bad value"))
    with patch.dict(ALL_TOOLS, {tool_name: {**ALL_TOOLS[tool_name], "handler": handler}}):
        result = await call_tool(tool_name, {"space_id": 1})
    assert _text(result) == "Error: ValueError: bad value"
    assert result.isError is True


async def test_call_tool_runtime_error():
    tool_name = "kaiten_get_space"
    handler = AsyncMock(side_effect=RuntimeError("connection lost"))
    with patch.dict(ALL_TOOLS, {tool_name: {**ALL_TOOLS[tool_name], "handler": handler}}):
        result = await call_tool(tool_name, {"space_id": 1})
    assert _text(result) == "Error: RuntimeError: connection lost"
    assert result.isError is True


async def test_call_tool_key_error():
    tool_name = "kaiten_get_space"
    handler = AsyncMock(side_effect=KeyError("missing_field"))
    with patch.dict(ALL_TOOLS, {tool_name: {**ALL_TOOLS[tool_name], "handler": handler}}):
        result = await call_tool(tool_name, {"space_id": 1})
    assert "Error: KeyError:" in _text(result)
    assert result.isError is True


# ── 8. list_tools returns correct count ─────────────────────────────────────


async def test_list_tools_count():
    tools = await list_tools()
    assert len(tools) == len(ALL_TOOLS)


async def test_list_tools_non_empty():
    tools = await list_tools()
    assert len(tools) > 0


# ── 9. list_tools returns Tool objects ──────────────────────────────────────


async def test_list_tools_returns_tool_objects():
    tools = await list_tools()
    for tool in tools:
        assert isinstance(tool, Tool)


async def test_list_tools_tool_has_name_description_schema():
    tools = await list_tools()
    for tool in tools:
        assert isinstance(tool.name, str) and len(tool.name) > 0
        assert isinstance(tool.description, str) and len(tool.description) > 0
        assert isinstance(tool.inputSchema, dict)
        assert tool.inputSchema.get("type") == "object"
        assert "properties" in tool.inputSchema


async def test_list_tools_names_match_all_tools():
    tools = await list_tools()
    tool_names = {t.name for t in tools}
    assert tool_names == set(ALL_TOOLS.keys())


# ── 10. Parametrized: one tool per module via respx ─────────────────────────


# ── 10.5. get_client() ─────────────────────────────────────────────────────


def test_get_client_creates_kaiten_client():
    """get_client() creates a KaitenClient when _client is None."""
    import kaiten_mcp.server as srv
    original = srv._client
    try:
        srv._client = None
        c = get_client()
        assert isinstance(c, KaitenClient)
        assert c is get_client()  # cached
    finally:
        srv._client = original


_PARAMETRIZED_TOOLS = [
    # (tool_name, arguments, http_method, url_path, response_json)
    pytest.param(
        "kaiten_list_spaces",
        {},
        "GET",
        "/spaces",
        [{"id": 1, "title": "Dev"}],
        id="spaces",
    ),
    pytest.param(
        "kaiten_get_board",
        {"board_id": 10},
        "GET",
        "/boards/10",
        {"id": 10, "title": "Sprint Board"},
        id="boards",
    ),
    pytest.param(
        "kaiten_get_card",
        {"card_id": 42},
        "GET",
        "/cards/42",
        {"id": 42, "title": "Fix login bug"},
        id="cards",
    ),
    pytest.param(
        "kaiten_list_tags",
        {},
        "GET",
        "/tags",
        [{"id": 1, "name": "urgent"}],
        id="tags",
    ),
    pytest.param(
        "kaiten_list_comments",
        {"card_id": 5},
        "GET",
        "/cards/5/comments",
        [{"id": 100, "text": "Looks good"}],
        id="comments",
    ),
    pytest.param(
        "kaiten_get_current_user",
        {},
        "GET",
        "/users/current",
        {"id": 7, "username": "dev"},
        id="members",
    ),
    pytest.param(
        "kaiten_list_documents",
        {},
        "GET",
        "/documents",
        [{"id": 3, "title": "Design Doc"}],
        id="documents",
    ),
    pytest.param(
        "kaiten_list_webhooks",
        {"space_id": 2},
        "GET",
        "/spaces/2/webhooks",
        [{"id": 9, "url": "https://example.com/hook"}],
        id="webhooks",
    ),
]


@pytest.mark.parametrize(
    "tool_name, arguments, http_method, url_path, response_json",
    _PARAMETRIZED_TOOLS,
)
@respx.mock
async def test_call_tool_with_respx(
    tool_name,
    arguments,
    http_method,
    url_path,
    response_json,
    _inject_client,
):
    route = respx.request(
        http_method,
        url=f"{BASE_URL}{url_path}",
    ).respond(json=response_json)

    result = await call_tool(tool_name, arguments)

    assert route.called
    parsed = json.loads(_text(result))
    assert parsed == response_json
