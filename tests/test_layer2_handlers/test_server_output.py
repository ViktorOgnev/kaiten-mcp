"""Tests for server.py compact JSON, file-based output, base64 stripping, and error resilience."""

import json
import os
import tempfile
from unittest.mock import AsyncMock, patch

import pytest
from mcp.types import CallToolResult, TextContent

from kaiten_mcp.server import ALL_TOOLS, call_tool


def _text(result: CallToolResult) -> str:
    """Extract the text string from a CallToolResult."""
    assert len(result.content) == 1
    item = result.content[0]
    assert isinstance(item, TextContent)
    return item.text


@pytest.fixture(autouse=True)
def _inject_client():
    """Inject a mock client so get_client() does not create a real one."""
    with patch("kaiten_mcp.server._client", object()):
        yield


class TestCompactJsonSerialization:
    """Test that large responses use compact JSON (no indent)."""

    async def test_small_response_uses_indent(self):
        """Small responses should be pretty-printed with indentation."""
        handler = AsyncMock(return_value={"id": 1})
        with patch.dict(
            ALL_TOOLS,
            {
                "test_tool": {
                    "handler": handler,
                    "description": "t",
                    "inputSchema": {"type": "object", "properties": {}},
                },
            },
        ):
            result = await call_tool("test_tool", {})
        text = _text(result)
        # Pretty-printed JSON has newlines
        assert "\n" in text

    async def test_large_response_uses_compact_json(self):
        """Responses exceeding threshold should use compact JSON."""
        from kaiten_mcp.server import COMPACT_JSON_THRESHOLD

        # Create data that produces indented JSON larger than the threshold
        item_count = (COMPACT_JSON_THRESHOLD // 20) + 50
        large_data = [{"id": i, "data": "x" * 10} for i in range(item_count)]
        handler = AsyncMock(return_value=large_data)
        with patch.dict(
            ALL_TOOLS,
            {
                "test_tool": {
                    "handler": handler,
                    "description": "t",
                    "inputSchema": {"type": "object", "properties": {}},
                },
            },
        ):
            result = await call_tool("test_tool", {})
        text = _text(result)
        # Compact JSON: no space after colon in keys
        assert '"id":' in text

    async def test_compact_json_is_valid(self):
        """Compact JSON output should be valid parseable JSON."""
        from kaiten_mcp.server import COMPACT_JSON_THRESHOLD

        item_count = (COMPACT_JSON_THRESHOLD // 20) + 50
        large_data = [{"id": i, "val": "test"} for i in range(item_count)]
        handler = AsyncMock(return_value=large_data)
        with patch.dict(
            ALL_TOOLS,
            {
                "test_tool": {
                    "handler": handler,
                    "description": "t",
                    "inputSchema": {"type": "object", "properties": {}},
                },
            },
        ):
            result = await call_tool("test_tool", {})
        text = _text(result)
        parsed = json.loads(text)
        assert isinstance(parsed, list)
        assert len(parsed) == item_count


class TestFileBasedOutput:
    """Test file-based output for oversized responses."""

    async def test_file_output_when_configured(self):
        """When KAITEN_MCP_OUTPUT_DIR is set, oversized responses save to file."""
        from kaiten_mcp.server import FILE_OUTPUT_THRESHOLD

        # Create data large enough to exceed FILE_OUTPUT_THRESHOLD
        item_count = (FILE_OUTPUT_THRESHOLD // 30) + 100
        large_data = [{"id": i, "data": "x" * 20} for i in range(item_count)]
        handler = AsyncMock(return_value=large_data)
        with tempfile.TemporaryDirectory() as tmpdir:
            with (
                patch.dict(
                    ALL_TOOLS,
                    {
                        "test_tool": {
                            "handler": handler,
                            "description": "t",
                            "inputSchema": {"type": "object", "properties": {}},
                        },
                    },
                ),
                patch.dict(os.environ, {"KAITEN_MCP_OUTPUT_DIR": tmpdir}),
            ):
                result = await call_tool("test_tool", {})
            text = _text(result)
            summary = json.loads(text)
            assert "saved_to" in summary
            assert summary["total_items"] == item_count
            assert os.path.exists(summary["saved_to"])  # noqa: ASYNC240
            # Verify saved file contains correct data
            with open(summary["saved_to"]) as f:  # noqa: ASYNC230
                saved_data = json.loads(f.read())
            assert len(saved_data) == item_count

    async def test_no_file_output_without_env(self):
        """Without KAITEN_MCP_OUTPUT_DIR, oversized responses are returned inline."""
        from kaiten_mcp.server import FILE_OUTPUT_THRESHOLD

        item_count = (FILE_OUTPUT_THRESHOLD // 30) + 100
        large_data = [{"id": i, "data": "x" * 20} for i in range(item_count)]
        handler = AsyncMock(return_value=large_data)
        env = os.environ.copy()
        env.pop("KAITEN_MCP_OUTPUT_DIR", None)
        with (
            patch.dict(
                ALL_TOOLS,
                {
                    "test_tool": {
                        "handler": handler,
                        "description": "t",
                        "inputSchema": {"type": "object", "properties": {}},
                    },
                },
            ),
            patch.dict(os.environ, env, clear=True),
        ):
            result = await call_tool("test_tool", {})
        text = _text(result)
        # Should return the full data inline (compact JSON), not a file summary
        parsed = json.loads(text)
        assert isinstance(parsed, list)
        assert len(parsed) == item_count

    async def test_file_output_not_triggered_for_small_response(self):
        """Small responses should not trigger file output even with env set."""
        small_data = [{"id": 1}]
        handler = AsyncMock(return_value=small_data)
        with tempfile.TemporaryDirectory() as tmpdir:
            with (
                patch.dict(
                    ALL_TOOLS,
                    {
                        "test_tool": {
                            "handler": handler,
                            "description": "t",
                            "inputSchema": {"type": "object", "properties": {}},
                        },
                    },
                ),
                patch.dict(os.environ, {"KAITEN_MCP_OUTPUT_DIR": tmpdir}),
            ):
                result = await call_tool("test_tool", {})
            text = _text(result)
            parsed = json.loads(text)
            # Small result should be returned directly, not as file summary
            assert isinstance(parsed, list)
            assert parsed == [{"id": 1}]


class TestBase64AutoStripping:
    """Test that base64 data URIs are automatically stripped from all tool responses."""

    async def test_base64_auto_stripped_in_call_tool(self):
        """call_tool should auto-strip base64 data URIs from handler results."""
        data_with_avatar = {
            "id": 1,
            "title": "Card",
            "avatar_url": "data:image/png;base64," + "A" * 2048,
        }
        handler = AsyncMock(return_value=data_with_avatar)
        with patch.dict(
            ALL_TOOLS,
            {
                "test_tool": {
                    "handler": handler,
                    "description": "t",
                    "inputSchema": {"type": "object", "properties": {}},
                },
            },
        ):
            result = await call_tool("test_tool", {})
        text = _text(result)
        assert "data:image" not in text
        assert "[base64 ~" in text

    async def test_strip_note_appended(self):
        """When base64 fields are stripped, a note should be appended to the response."""
        data_with_avatars = [
            {"id": 1, "avatar": "data:image/png;base64,aaa"},
            {"id": 2, "avatar": "data:image/png;base64,bbb"},
        ]
        handler = AsyncMock(return_value=data_with_avatars)
        with patch.dict(
            ALL_TOOLS,
            {
                "test_tool": {
                    "handler": handler,
                    "description": "t",
                    "inputSchema": {"type": "object", "properties": {}},
                },
            },
        ):
            result = await call_tool("test_tool", {})
        text = _text(result)
        assert "[Omitted 2 base64-encoded field(s)" in text

    async def test_no_note_when_clean(self):
        """When no base64 fields are present, no note should be appended."""
        clean_data = {"id": 1, "title": "Card", "url": "https://example.com/avatar.png"}
        handler = AsyncMock(return_value=clean_data)
        with patch.dict(
            ALL_TOOLS,
            {
                "test_tool": {
                    "handler": handler,
                    "description": "t",
                    "inputSchema": {"type": "object", "properties": {}},
                },
            },
        ):
            result = await call_tool("test_tool", {})
        text = _text(result)
        assert "[Omitted" not in text


class TestErrorResilience:
    """Test that call_tool never crashes the MCP server."""

    async def test_error_in_get_client_returns_error(self):
        """ValueError from get_client() should return error result, not crash."""
        handler = AsyncMock()
        with (
            patch.dict(
                ALL_TOOLS,
                {
                    "test_tool": {
                        "handler": handler,
                        "description": "t",
                        "inputSchema": {"type": "object", "properties": {}},
                    },
                },
            ),
            patch(
                "kaiten_mcp.server.get_client", side_effect=ValueError("KAITEN_DOMAIN is required")
            ),
        ):
            result = await call_tool("test_tool", {})
        text = _text(result)
        assert result.isError is True
        assert "ValueError" in text
        assert "KAITEN_DOMAIN" in text

    async def test_handler_type_error_returns_error(self):
        """TypeError in handler (wrong argument type) should return error, not crash."""
        handler = AsyncMock(side_effect=TypeError("expected int, got str"))
        with patch.dict(
            ALL_TOOLS,
            {
                "test_tool": {
                    "handler": handler,
                    "description": "t",
                    "inputSchema": {"type": "object", "properties": {}},
                },
            },
        ):
            result = await call_tool("test_tool", {})
        text = _text(result)
        assert result.isError is True
        assert "TypeError" in text

    async def test_unknown_tool_returns_error_not_crash(self):
        """Unknown tool name should return text error, not exception."""
        result = await call_tool("nonexistent_tool_xyz", {})
        text = _text(result)
        assert "Unknown tool" in text
        assert "nonexistent_tool_xyz" in text
